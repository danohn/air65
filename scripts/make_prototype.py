"""Create the intentionally simple, locked-dimension integration prototype."""
from contracts import ROOT, read_json, write_json


def p(name,scale=1,offset=0):
    return {"param":name,"scale":scale,"offset":offset}


def main():
    architecture=read_json(ROOT/"specs/spatial_architecture.json")
    nodes=[]
    for label,x,y in [("FL",-1,1),("FR",1,1),("RL",-1,-1),("RR",1,-1)]:
        xy=[p("motor_axis_offset",x),p("motor_axis_offset",y)]
        nodes.append({"id":"duct_"+label,"op":"ring_profile","material":"frame_lavender","args":{"profile":[[p("duct_inner_radius"),p("duct_bottom_z")],[p("duct_outer_radius"),p("duct_bottom_z")],[p("duct_outer_radius"),p("duct_top_z")],[p("duct_inner_radius"),p("duct_top_z")]],"segments":96},"transform":{"location":xy+[0]}})
        nodes.append({"id":"motor_"+label,"op":"cylinder","material":"motor_silver","args":{"radius":p("motor_body_radius"),"depth":p("motor_body_height")},"transform":{"location":xy+[p("motor_body_center_z")]}})
        nodes.append({"id":"prop_swept_clearance_"+label,"op":"annulus","material":"prop_clear","args":{"inner_radius":p("prop_swept_radius",1,-0.18),"outer_radius":p("prop_swept_radius"),"depth":0.12},"transform":{"location":xy+[p("prop_blade_reference_z")]}})
    nodes.append({"id":"frame_datum","op":"box","material":"frame_lavender","args":{"size":[11.4,18,0.7]},"transform":{"location":[0,0,0.35]},"notes":"Prototype datum marker only, not final battery cradle."})
    nodes.append({"id":"pcb_proxy","op":"box","material":"pcb_black","args":{"size":[p("fc_body_side"),p("fc_body_side"),p("fc_board_thickness")]},"transform":{"location":[0,0,p("fc_pcb_center_z")],"rotation_deg":[0,0,45]},"notes":"Prototype PCB square; actual outline and lugs are added only in detailed modelling."})
    comp={"schema_version":"1.0","id":"prototype","contract":architecture["contract"],"description":"Minimal JSON-to-Blender validation fixture. Not the final recreation.","provenance":[{"feature":"prototype simplifications","status":"simplified","source_ids":["frame_drawing"],"confidence":"low","note":"Cylindrical motor proxies, rectangular ring cross-section, clearance circles and PCB proxy validate the pipeline before detailed modelling."}],"nodes":nodes}
    write_json(ROOT/"specs/components/prototype.json",comp)
    assembly={"schema_version":"1.0","id":"prototype","architecture":"specs/spatial_architecture.json","materials":"specs/materials.json","components":{"prototype":"specs/components/prototype.json"},"instances":[{"id":"prototype","component":"prototype"}]}
    write_json(ROOT/"specs/prototype_assembly.json",assembly)


if __name__=="__main__":
    main()
