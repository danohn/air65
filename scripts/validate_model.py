"""Numerical conformance checks; distinguish source nominals from visual estimates."""
import argparse
import hashlib
import math
from pathlib import Path
import sys

from contracts import ROOT,prepare,read_json,write_json


def verify_render_manifest(output,input_hash,required_views):
    path=output/"render_manifest.json"
    if not path.exists():
        return {"status":"fail","errors":["Render manifest missing; complete a rendered build first."]}
    manifest=read_json(path)
    errors=[]
    if manifest.get("geometry_input_sha256")!=input_hash:
        errors.append("Render manifest belongs to different source inputs.")
    for name in required_views:
        record=manifest.get("views",{}).get(name)
        image=output/(name+".png")
        if not record or not image.exists():
            errors.append(f"Missing rendered view: {name}")
        elif hashlib.sha256(image.read_bytes()).hexdigest()!=record.get("sha256"):
            errors.append(f"Render checksum differs: {name}")
    return {"status":"fail" if errors else "pass","required_views":required_views,"errors":errors}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",default="output/final")
    parser.add_argument("--assembly",default="specs/assembly.json")
    parser.add_argument("--required-views",default="hero,top,front,right,left,rear,underside,reference")
    args=parser.parse_args()
    output=ROOT/args.output
    data=prepare(ROOT/args.assembly)
    metrics=read_json(output/"metrics.json")
    if metrics["geometry_input_sha256"] != data["geometry_input_sha256"]:
        raise ValueError("Saved metrics do not match current JSON/renderer sources; rebuild first")
    params=data["architecture"]["parameters"]
    p=lambda key:params[key]["value"]
    objects=metrics["objects"]
    named={o["name"]:o for o in objects}
    results=[]

    def check(name,measured,expected,tolerance,kind="source nominal",note=""):
        delta=abs(measured-expected)
        results.append({"check":name,"measured":measured,"expected":expected,"difference":delta,"numerical_tolerance":tolerance,"status":"pass" if delta<=tolerance else "fail","evidence_class":kind,"note":note})

    def minimum(name,measured,expected,note):
        results.append({"check":name,"measured":measured,"expected":expected,"comparison":">=","difference":max(0,expected-measured),"numerical_tolerance":0.002,"status":"pass" if measured+0.002>=expected else "fail","evidence_class":"estimated hardware fit","note":note})

    def bounds(group):
        return [min(o["bounds_min_mm"][i] for o in group) for i in range(3)],[max(o["bounds_max_mm"][i] for o in group) for i in range(3)]

    frame=[o for o in objects if o["name"].startswith("frame.")]
    if not frame:
        raise ValueError("No frame objects found")
    low,high=bounds(frame)
    for i,axis in enumerate("XYZ"):
        check("Frame envelope "+axis,high[i]-low[i],[82.6,82.6,15.1][i],0.012,note="Numerical CAD conformance tolerance, not a manufacturer manufacturing tolerance.")
    check("Frame bottom datum",low[2],0,0.012,"chosen datum")
    duct_objects={label:next(o for o in objects if o["name"]=="frame.duct_"+label) for label in ["FL","FR","RL","RR"]}
    centers={label:[(o["bounds_min_mm"][i]+o["bounds_max_mm"][i])/2 for i in range(2)] for label,o in duct_objects.items()}
    check("Evaluated diagonal motor/duct spacing",math.dist(centers["FL"],centers["RR"] ),p("wheelbase"),0.001)
    for label,obj in duct_objects.items():
        check(label+" duct outer diameter",obj["dimensions_mm"][0],p("duct_outer_radius")*2,0.012,"derived envelope")
        check(label+" duct upper band height",obj["dimensions_mm"][2],p("duct_band_height"),0.012)
        check(label+" evaluated duct vertex inner diameter",2*obj["local_xy_vertex_radius_min_mm"],33,0.005)
    for label in ["FL","FR","RL","RR"]:
        rotor=[o for o in objects if o["name"].startswith("prop_"+label+".")]
        if not rotor:
            raise ValueError("No rotor geometry for "+label)
        radius=max(o["maximum_radius_from_parent_axis_mm"] for o in rotor)
        check(label+" evaluated prop swept diameter",radius*2,p("prop_diameter"),0.025)
        check(label+" evaluated prop radial clearance",p("duct_inner_radius")-radius,1,0.015,"source nominal plus geometry", "Derived from full evaluated blade vertices, including sweep and twist.")
        check(label+" evaluated prop hub height",named["prop_"+label+".outer_hub_barrel"]["local_dimensions_mm"][2],3.3,0.01)
        shaft=named["motor_"+label+".upper_shaft"]
        motor=[o for o in objects if o["name"].startswith("motor_"+label+".")]
        check(label+" evaluated motor maximum diameter",2*max(o["maximum_radius_from_parent_axis_mm"] for o in motor),9,0.01)
        check(label+" evaluated motor base-to-shaft shoulder",named["motor_"+label+".upper_bushing"]["bounds_max_mm"][2]-named["motor_"+label+".lower_mount_center"]["bounds_min_mm"][2],8.55,0.005)
        check(label+" evaluated motor/duct concentricity",math.dist(shaft["world_origin_mm"][:2],centers[label]),0,0.001,"assembly constraint")
        check(label+" evaluated prop/duct concentricity",math.dist(named["prop_"+label+".outer_hub_barrel"]["world_origin_mm"][:2],centers[label]),0,0.001,"assembly constraint")
        check(label+" evaluated motor shaft diameter",shaft["local_dimensions_mm"][0],1,0.002)
        check(label+" evaluated shaft extension mesh length",shaft["local_dimensions_mm"][2],3.4,0.002,note="Extension above the motor shoulder; most is buried in the installed prop hub.")
    check("Motor diagonal parameter registry",2*math.sqrt(2)*p("motor_axis_offset"),65,1e-7,"derived")
    check("Frame adjacent mounting pitch",math.sqrt(2)*p("frame_mount_cardinal_offset"),25.5,1e-7)
    check("FC nominal adjacent mounting pitch",math.sqrt(2)*p("fc_mount_cardinal_offset"),26,1e-7)
    check("Evaluated frame mounting pitch",math.dist(named["frame.mount_boss_front"]["world_origin_mm"],named["frame.mount_boss_right"]["world_origin_mm"]),25.5,0.001)
    check("Evaluated PCB nominal lug pitch",math.dist(named["electronics.fc_lug_left"]["world_origin_mm"],named["electronics.fc_lug_rear"]["world_origin_mm"]),26,0.001)
    check("Evaluated FC substrate thickness",named["electronics.fc_substrate_diamond"]["dimensions_mm"][2],1,0.005)
    check("FC derived body corner",p("fc_body_corner_radius"),p("fc_body_side")/math.sqrt(2),1e-7,"derived from photographic estimate")
    check("FC derived side clip width",p("fc_side_clip_half_width"),p("fc_body_corner_radius")-p("fc_side_rear_clip_radius"),1e-7,"derived from photographic estimate")
    check("FC derived front clip width",p("fc_front_clip_half_width"),p("fc_body_corner_radius")-p("fc_front_clip_y"),1e-7,"derived from photographic estimate")
    substrate=named["electronics.fc_substrate_diamond"]
    check("Evaluated FC central outline X",substrate["dimensions_mm"][0],2*p("fc_side_rear_clip_radius"),0.01,"photographic outline estimate")
    check("Evaluated FC central outline Y",substrate["dimensions_mm"][1],p("fc_front_clip_y")+p("fc_side_rear_clip_radius"),0.01,"photographic outline estimate")
    minimum("PCB substrate clearance from side/rear lug bores",p("fc_mount_cardinal_offset")-p("fc_lug_hole_radius")-p("fc_side_rear_clip_radius"),0.5,"Stops the revised substrate filling the three mounting holes; outline and hole radius are estimates.")
    for label in ["front","rear","left","right"]:
        shank=named["electronics.assembly_screw_shank_"+label]
        head=named["electronics.assembly_screw_head_"+label]
        boss=named["frame.mount_boss_"+label]
        check(label+" screw/boss XY alignment",math.dist(shank["world_origin_mm"][:2],boss["world_origin_mm"][:2]),0,0.001,"estimated hardware fit")
        overlap=min(shank["bounds_max_mm"][2],boss["bounds_max_mm"][2])-max(shank["bounds_min_mm"][2],boss["bounds_min_mm"][2])
        minimum(label+" screw axial engagement in boss",overlap,1.0,"Chosen representative engagement, not a published screw length or thread-fit certification. Threads are simplified.")
        overlap=min(shank["bounds_max_mm"][2],head["bounds_max_mm"][2])-max(shank["bounds_min_mm"][2],head["bounds_min_mm"][2])
        minimum(label+" screw shank/head axial connection",overlap,0.1,"Prevents a floating head; evaluated solid intervals must overlap.")
        minimum(label+" screw shank below head top",head["bounds_max_mm"][2]-shank["bounds_max_mm"][2],0,"Prevents shank protrusion through the visible screw-head face.")
    check("Required radial grommet offset",p("fc_mount_cardinal_offset")-p("frame_mount_cardinal_offset"),0.3535533906,1e-7,"assembly assumption", "Manufacturer frame/FC pitch mismatch is preserved; actual elastomer deformation is unverified.")
    check("Camera axial depth",math.hypot(p("camera_front_center_y")-p("camera_pcb_center_y"),p("camera_front_center_z")-p("camera_pcb_center_z")),15,1e-7)
    check("Camera lens versus collar radial gap",p("canopy_clamp_inner_radius")-p("camera_lens_radius"),0.1,1e-7)
    lens=named["camera.lens_front_cup"]
    check("Evaluated camera barrel outer diameter",lens["local_dimensions_mm"][0],10,0.005)
    check("Evaluated camera optical elevation",math.degrees(math.asin(lens["world_axis_z"][2])),25,0.001,"selected official setting")
    pcb=named["camera.c03_shaped_pcb_substrate"]
    check("Evaluated camera axial reference depth",math.dist(lens["world_origin_mm"],pcb["world_origin_mm"]),15,0.001)
    check("Evaluated camera PCB width",pcb["local_dimensions_mm"][0],11,0.005)
    check("Evaluated camera PCB height",pcb["local_dimensions_mm"][1],14,0.005)
    check("Battery slot height",p("battery_slot_ceiling_z")-p("battery_slot_floor_z"),6.2,1e-7)
    ratios=[("Outer duct/frame span",2*p("duct_outer_radius")/p("frame_span_x"),0.442,0.005),("Motor spacing/frame span",p("motor_adjacent_distance")/p("frame_span_x"),0.553,0.004),("Clear duct/frame span",p("duct_inner_diameter")/p("frame_span_x"),0.398,0.006)]
    for name,value,estimated,uncertainty in ratios:
        check(name,value,estimated,uncertainty,"uncalibrated reference image estimate","Approximate black frame plan-photo landmark ratio; this is an independent visual cross-check, not metrology.")
    source_ids={s["id"] for s in read_json(ROOT/"specs/design_spec.json")["sources"]}
    manifest=read_json(ROOT/"references/manifest.json")
    # Reference asset IDs can be used as provenance locators alongside page source IDs.
    if isinstance(manifest,dict):
        records=manifest.get("assets",manifest.get("references",[]))
    else:
        records=manifest
    for item in records:
        if isinstance(item,dict) and "id" in item:
            source_ids.add(item["id"])
    confidence_counts={}
    for parameter_id,param in params.items():
        missing=set(param["source_ids"])-source_ids
        if missing:
            raise ValueError(f"Unresolved provenance for {parameter_id}: {sorted(missing)}")
        key=param["status"]
        confidence_counts[key]=confidence_counts.get(key,0)+1
    renders={name:(output/(name+".png")).exists() for name in ["hero","top","front","right","left","rear","underside","reference"]}
    render_verification=verify_render_manifest(output,data["geometry_input_sha256"],args.required_views.split(","))
    result={"status":"pass" if all(r["status"]=="pass" for r in results) and render_verification["status"]=="pass" else "fail","claim":"Conformance to declared source nominals and modelling contract. Does not certify an unmeasured physical specimen.","checks":results,"parameter_status_counts":confidence_counts,"geometry_fingerprint_sha256":metrics["geometry_fingerprint_sha256"],"geometry_input_sha256":data["geometry_input_sha256"],"geometry_object_count":metrics["geometry_object_count"],"total_vertices":metrics["total_vertices"],"full_aircraft_bounds_mm":{"min":metrics["assembly_bounds_min_mm"],"max":metrics["assembly_bounds_max_mm"],"dimensions":[b-a for a,b in zip(metrics["assembly_bounds_min_mm"],metrics["assembly_bounds_max_mm"])]},"render_presence":renders,"render_verification":render_verification,"limitations":["Source manufacturers publish nominal dimensions without manufacturing tolerances.","Canopy shape, exact PCB outline, installed vertical stack, antenna and small details are estimates.","Reference photographs are not calibrated and are not matched to the renderer lens exactly.","No aerodynamic, structural or manufacturing-fit certification."]}
    write_json(output/"validation.json",result)
    print(f"{sum(r['status']=='pass' for r in results)}/{len(results)} numeric conformance checks passed")
    for row in results:
        if row["status"]!="pass":
            print(f"FAIL {row['check']}: {row['measured']:.8g} vs {row['expected']:.8g}")
    for error in render_verification["errors"]:
        print("FAIL "+error)
    if result["status"]!="pass":
        sys.exit(1)


if __name__=="__main__":
    main()
