"""Package the local research archive, including downloaded reference photographs.

Use package_release.py for public GitHub release assets instead.
"""
import hashlib
import json
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[1]


def main():
    required=["README.md","reports/validation_report.md","reports/final_visual_signoff.md","reports/refinement_validation.json","reports/refinement_validation.md","reports/refinement_independent_visual_review.md","reports/browser_performance.json","reports/site/deployment.json","output/final/air65_ii.blend","output/final/validation.json","output/final/render_manifest.json","output/final/reopen_validation.json","output/final/reproducibility.json","output/with_battery/fit_validation.json","output/web_optimized/air65-ii.glb","output/web_optimized/anchor-validation.json","output/web_optimized/reproducibility.json"]
    for name in required:
        if not (ROOT/name).is_file():
            raise ValueError(f"Required delivery file missing: {name}")
    validation=json.loads((ROOT/"output/final/validation.json").read_text())
    if validation["status"]!="pass":
        raise ValueError("Final validation must pass before packaging")
    refinement=json.loads((ROOT/"reports/refinement_validation.json").read_text())
    for field in ["web_anchor_validation","web_reproducibility","battery_fit","repeatability","reopen"]:
        if refinement[field]["status"]!="pass":
            raise ValueError(f"Refinement evidence failed: {field}")
    asset_sha=refinement["assets"]["refined_optimized"]["sha256"]
    for name in ["output/web_optimized/air65-ii.glb","site/dist/assets/air65-ii.glb"]:
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=asset_sha:
            raise ValueError(f"Public asset does not match validated export: {name}")
    files=[ROOT/name for name in ["README.md","IMPLEMENTATION_PLAN.md","REFINEMENT_PLAN.md","pyproject.toml","uv.lock",".gitignore"]]
    for directory in ["assets","specs","scripts","tests","research","references","reports"]:
        files.extend(path for path in (ROOT/directory).rglob("*") if path.is_file() and "__pycache__" not in path.parts and path.suffix not in {".pyc",".blend1"} and path.name!=".DS_Store" and "contract_check" not in path.parts)
    for directory in ["output/final","output/with_battery","output/web","output/web_optimized","output/prototype","output/refinement_baseline","output/refinement_inspection","output/browser_benchmark","output/frame_final","output/canopy_refinement/isolated_final","site/dist"]:
        files.extend(path for path in (ROOT/directory).rglob('*') if path.is_file() and path.suffix not in {'.blend1','.pyc'} and '__pycache__' not in path.parts and path.name!='.DS_Store')
    files.extend(ROOT/name for name in ['site/README.md','site/VALIDATION.md','site/package.json','site/.openai/hosting.json'])
    files.extend(ROOT/name for name in ['output/canopy_refinement/authoring_validation.json','output/canopy_refinement/component_validation.json'])
    files=sorted(set(files),key=lambda p:p.relative_to(ROOT).as_posix())
    entries=[{"path":path.relative_to(ROOT).as_posix(),"bytes":path.stat().st_size,"sha256":hashlib.sha256(path.read_bytes()).hexdigest()} for path in files]
    manifest={"project":"BETAFPV Air65 II Racing parametric recreation","date":"2026-10-12","geometry_input_sha256":validation["geometry_input_sha256"],"geometry_fingerprint_sha256":validation["geometry_fingerprint_sha256"],"public_glb_sha256":asset_sha,"file_count":len(entries),"files":entries,"note":"Reference images retain original owners' copyright; see README and reference manifests. Environment caches and Blender backup files are excluded."}
    content=json.dumps(manifest,indent=2,ensure_ascii=False)+"\n"
    destination=ROOT/"dist"
    destination.mkdir(exist_ok=True)
    (destination/"deliverables_manifest.json").write_text(content)
    archive=destination/"air65_ii_project.zip"
    with zipfile.ZipFile(archive,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for path in files:
            info=zipfile.ZipInfo("air65_ii/"+path.relative_to(ROOT).as_posix(),date_time=(2026,10,12,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o100644<<16
            z.writestr(info,path.read_bytes())
        info=zipfile.ZipInfo("air65_ii/MANIFEST.json",date_time=(2026,10,12,0,0,0))
        info.compress_type=zipfile.ZIP_DEFLATED
        info.external_attr=0o100644<<16
        z.writestr(info,content)
    with zipfile.ZipFile(archive) as z:
        corrupt=z.testzip()
        if corrupt:
            raise RuntimeError(f"Archive CRC check failed: {corrupt}")
    receipt={"archive":archive.name,"bytes":archive.stat().st_size,"sha256":hashlib.sha256(archive.read_bytes()).hexdigest(),"file_count":len(entries)+1,"crc_check":"pass"}
    (destination/"archive_receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps(receipt,indent=2))


if __name__=="__main__":
    main()
