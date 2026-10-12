"""Assemble machine-readable evidence for the refinement report from final artifacts."""
import hashlib
import json
import statistics
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def read(name):return json.loads((ROOT/name).read_text())
def sha(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()

def main():
    baseline=read('output/refinement_baseline/specs/spatial_architecture.json')['parameters']
    current=read('specs/spatial_architecture.json')['parameters']
    changed_verified=[k for k,v in baseline.items() if v['status']=='verified' and current[k]['value']!=v['value']]
    if changed_verified:raise ValueError('Published anchors changed: '+str(changed_verified))
    revised={k:{'before':baseline[k]['value'],'after':v['value'],'status':v['status'],'confidence':v['confidence'],'sources':v['source_ids']} for k,v in current.items() if k in baseline and v['value']!=baseline[k]['value']}
    original=read('output/refinement_baseline/web/model-metadata.json')
    detailed=read('output/web/model-metadata.json')
    optimized=read('output/web_optimized/model-metadata.json')
    benchmark=read('reports/browser_performance.json')
    if benchmark['invalidated_by_background_or_gpu_disjoint']:raise ValueError('Browser timing was invalidated; rerun')
    for key,metadata in [('original',original),('refined_full',detailed),('refined_optimized',optimized)]:
        if benchmark['assets'][key]['sha256'] != metadata['asset_sha256']:raise ValueError('Benchmark asset mismatch: '+key)
    anchors=read('output/web_optimized/anchor-validation.json')
    repeat=read('output/web_optimized/reproducibility.json')
    if anchors['status']!='pass' or repeat['status']!='pass':raise ValueError('Web validation incomplete')
    timing={}
    for name in ['original','refined_full','refined_optimized']:
        rows=[r for r in benchmark['runs'] if r['case']==name]
        timing[name]={'rounds':len(rows),'median_of_round_cpu_medians_ms':statistics.median(r['cpu_submission']['median_ms'] for r in rows),'median_of_round_cpu_p95_ms':statistics.median(r['cpu_submission']['p95_ms'] for r in rows),'mean_of_round_fps':statistics.mean(r['mean_fps'] for r in rows),'median_of_round_gpu_medians_ms':statistics.median(r['gpu_elapsed']['median_ms'] for r in rows) if all(r['gpu_elapsed'] for r in rows) else None}
    def asset(m):return {'bytes':m['asset_bytes'],'sha256':m['asset_sha256'],'triangles':m['validation']['exported_triangles'],'vertices':m['validation']['exported_vertices'],'materials':m['validation']['material_count'],'textures':len(m.get('embedded_textures',[])),'components':m['validation']['component_count']}
    validation=read('output/final/validation.json')
    result={'date':'2026-10-12','published_anchors_unchanged':True,'published_anchor_count':sum(v['status']=='verified' for v in baseline.values()),'revised_parameters':revised,'added_parameters':{k:v for k,v in current.items() if k not in baseline},'dry_validation':validation['status'],'numeric_checks':len(validation['checks']),'parameter_status_counts':validation['parameter_status_counts'],'source_geometry_fingerprint_sha256':validation['geometry_fingerprint_sha256'],'source_input_sha256':validation['geometry_input_sha256'],'reopen':read('output/final/reopen_validation.json'),'repeatability':read('output/final/reproducibility.json'),'battery_fit':read('output/with_battery/fit_validation.json'),'assets':{'original':asset(original),'refined_full':asset(detailed),'refined_optimized':asset(optimized)},'optimization':optimized['optimization'],'web_anchor_validation':anchors,'web_reproducibility':repeat,'browser_timing_summary':timing,'browser_evidence_sha256':sha('reports/browser_performance.json'),'claim_limits':['Photographic estimates have no calibrated physical error percentage.','Source-to-web sampled mesh distance does not establish physical accuracy or a continuous Hausdorff bound.','Browser timings describe one local GPU/browser at the recorded viewport, not internet loading or universal performance.']}
    publication_path=ROOT/'reports/site/deployment.json'
    public_check_path=ROOT/'reports/site/public_asset_validation.json'
    if publication_path.is_file() and public_check_path.is_file():
        publication=read('reports/site/deployment.json')
        public_check=read('reports/site/public_asset_validation.json')
        if publication.get('public_glb_sha256')!=optimized['asset_sha256'] or public_check['status']!='pass':
            raise ValueError('Published asset evidence does not match this refinement')
        result['publication']=publication
        result['public_asset_validation']=public_check
    (ROOT/'reports/refinement_validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'numeric_checks':result['numeric_checks'],'assets':result['assets'],'browser_timing_summary':timing},indent=2))

if __name__=='__main__':main()
