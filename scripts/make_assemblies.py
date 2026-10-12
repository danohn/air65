"""Assemble independent component files using the sole shared spatial contract."""
from contracts import ROOT,read_json,write_json


def main():
    arch=read_json(ROOT/"specs/spatial_architecture.json")
    components={key:f"specs/components/{key}.json" for key in ["frame","motor","prop_cw","prop_ccw","canopy","camera","electronics"]}
    instances=[{"id":key,"component":key} for key in ["frame","electronics","camera","canopy"]]
    for name,label,phase in [("front_left","FL",20),("front_right","FR",-15),("rear_left","RL",50),("rear_right","RR",-45)]:
        anchor=arch["anchors"]["motor_axes"][name]
        location=anchor["location"][:2]+[0]
        instances.append({"id":"motor_"+label,"component":"motor","transform":{"location":location,"rotation_deg":[0,0,30 if "left" in name else -30]}})
        instances.append({"id":"prop_"+label,"component":"prop_cw" if anchor["prop_handedness"]==1 else "prop_ccw","transform":{"location":location,"rotation_deg":[0,0,phase]}})
    assembly={"schema_version":"1.0","id":"air65-ii-racing-dry","architecture":"specs/spatial_architecture.json","materials":"specs/materials.json","components":components,"instances":instances,"notes":["Motor mounting rotations align frame screw pads. Prop phase is a deterministic presentation choice, not a measured static phase.","Dry aircraft; optional battery is provided as a separate assembly."],"views":{"hero":{"position":[112,142,119],"target":[0,0,18],"projection":"ORTHO","scale":112},"front":{"position":[0,200,26],"target":[0,0,26],"projection":"ORTHO","scale":99},"right":{"position":[200,0,26],"target":[0,0,26],"projection":"ORTHO","scale":99},"rear":{"position":[0,-200,26],"target":[0,0,26],"projection":"ORTHO","scale":99},"reference":{"position":[-105,155,114],"target":[0,0,18],"projection":"PERSP","lens":61}}}
    # All diagnostic orthographic views share the same millimetres per pixel.
    assembly["views"]["left"]={"position":[-200,0,26],"target":[0,0,26],"projection":"ORTHO","scale":99}
    assembly["views"]["top"]={"position":[0,0,200],"target":[0,0,0],"projection":"ORTHO","scale":99}
    assembly["views"]["underside"]={"position":[0,0,-200],"target":[0,0,0],"projection":"ORTHO","scale":99}
    write_json(ROOT/"specs/assembly.json",assembly)
    battery={**assembly,"id":"air65-ii-racing-with-280mah","components":{**components,"battery":"specs/components/battery.json"},"instances":instances+[{"id":"battery","component":"battery"}],"notes":["Optional280mAh battery. The underside manufacturer reference depicts320mAh; do not infer equal length."]}
    write_json(ROOT/"specs/assembly_with_battery.json",battery)
    frame={**assembly,"id":"air65-ii-frame-inspection","components":{"frame":components["frame"]},"instances":[{"id":"frame","component":"frame"}]}
    frame["views"]={"hero":{"position":[110,140,90],"target":[0,0,7],"projection":"ORTHO","scale":112},"front":{"position":[0,200,7.55],"target":[0,0,7.55],"projection":"ORTHO","scale":94}}
    write_json(ROOT/"specs/frame_assembly.json",frame)


if __name__=="__main__":
    main()
