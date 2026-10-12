# /// script
# requires-python = ">=3.14"
# dependencies = ["Pillow==12.2.0"]
# ///
"""Draw original PCB artwork and apply a bounded Matrix II surface refinement.

Run with ``uv run scripts/refine_electronics.py``. No reference photo is loaded.
Coordinates are estimates from the manufacturer photographs, fitted to the
existing shared contract. Texture grain and artwork are fully deterministic.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
BOARD_RGB = (27, 30, 31)
CHIP_RGB = (24, 25, 25)
SILK = (199, 215, 212)
GOLD = (175, 149, 98)
TRACE = (36, 41, 41)
SCALE = 2048 / 40
LEGACY_TOP_BODY_SIDE = 24.0  # Only for migrating original rigid child offsets.
ATLAS_TILES = {"fc_stm32g473": (0, 0), "fc_flash16m": (1, 0),
               "fc_current_sensor": (0, 1), "fc_refine_bottom_at7456e": (1, 1)}

# ID, x, y, width, length, height, Z rotation. Heights are explicit estimates.
# Bottom photograph is viewed from below: image right is world -X.
BOTTOM_PACKAGES = [
    ("vtx", 1.05, 8.35, 6.0, 6.0, .72, 45),
    ("at7456e", .7, .35, 6.8, 4.5, .72, 135),
    ("esc_control_fl", 6.35, 3.2, 2.65, 2.65, .58, 45),
    ("esc_control_fr", -6.65, 3.5, 2.65, 2.65, .58, 45),
    ("esc_control_rl", 5.25, -5.4, 2.65, 2.65, .58, 45),
    ("esc_control_rr", -5.8, -4.4, 2.65, 2.65, .58, 45),
    ("power_fl_outer", 9.5, 7.0, 2.65, 2.85, .52, 45),
    ("power_fr_outer", -9.5, 7.0, 2.65, 2.85, .52, 45),
    ("power_left_mid", 10.8, .1, 2.65, 2.85, .52, 45),
    ("power_right_mid", -10.8, .1, 2.65, 2.85, .52, 45),
    ("power_left_inner", 8.4, -2.65, 2.65, 2.85, .52, 45),
    ("power_right_inner", -8.2, -2.65, 2.65, 2.85, .52, 45),
    ("power_rl_outer", 9.0, -6.75, 2.65, 2.85, .52, 45),
    ("power_rr_outer", -9.4, -6.65, 2.65, 2.85, .52, 45),
]

# Selected visible passive neighbourhoods in matrix_ii_bottom.jpg. Dimensions,
# exact centres and electrical identity are estimates, not a recovered netlist.
# name, X, Y, width, length, height, Z rotation, body material
BOTTOM_PASSIVES = [
    ("fore_cap_a",1.90,13.10,.50,1.00,.40,45,"ceramic_tan"),
    ("fore_cap_b",2.95,12.40,.50,1.00,.40,45,"ceramic_tan"),
    ("fore_dark_a",.10,14.50,.50,.75,.28,-45,"chip_black"),
    ("fore_dark_b",-1.40,13.40,.45,.75,.26,45,"chip_black"),
    ("between_cap_a",3.25,3.20,.65,1.25,.46,45,"ceramic_tan"),
    ("between_cap_c",4.55,2.00,.65,1.20,.43,45,"ceramic_tan"),
    ("between_dark",-2.80,4.20,.60,1.40,.33,45,"chip_black"),
    ("right_cap_a",-3.90,3.30,.65,1.25,.46,45,"ceramic_tan"),
    ("right_cap_b",-4.60,2.20,.65,1.20,.40,45,"ceramic_tan"),
    ("right_dark",-4.00,.80,.45,.80,.24,45,"chip_black"),
    ("right_cap_c",-3.00,-1.10,.70,1.20,.43,45,"ceramic_tan"),
    ("right_rear_dark",-4.20,-2.00,.50,.80,.25,45,"chip_black"),
    ("left_rear_cap_a",3.25,-3.30,.65,1.20,.43,45,"ceramic_tan"),
    ("left_rear_cap_b",2.40,-4.35,.70,1.25,.43,45,"ceramic_tan"),
    ("centre_rear_dark",1.35,-4.80,.45,.75,.22,45,"chip_black"),
    ("centre_rear_cap_a",-1.50,-4.10,.65,1.20,.40,45,"ceramic_tan"),
    ("centre_rear_cap_b",-2.50,-5.20,.65,1.20,.40,45,"ceramic_tan"),
]


def resolve(value, parameters):
    if isinstance(value, dict) and "param" in value:
        return parameters[value["param"]]["value"] * value.get("scale", 1) + value.get("offset", 0)
    return value


def grain(size, colour):
    """Original low-amplitude grain; integer hash avoids random/version drift."""
    pixels = bytearray(size[0] * size[1] * 3)
    for y in range(size[1]):
        for x in range(size[0]):
            h = ((x * 374761393) ^ (y * 668265263)) & 0xffffffff
            h = ((h ^ (h >> 13)) * 1274126177) & 0xffffffff
            delta = ((h >> 24) % 3) - 1
            i = (y * size[0] + x) * 3
            pixels[i:i+3] = bytes(c + delta for c in colour)
    return Image.frombytes("RGB", size, bytes(pixels))


def xy(x, y):
    return ((x + 20) * SCALE, (20 - y) * SCALE)


def rotate_point(x, y, cx, cy, degrees):
    a = math.radians(degrees)
    return cx+x*math.cos(a)-y*math.sin(a), cy+x*math.sin(a)+y*math.cos(a)


def line(image, points, colour=SILK, width=.09):
    ImageDraw.Draw(image).line([xy(*p) for p in points], fill=colour,
                               width=max(1, round(width*SCALE)), joint="curve")


def text_mm(image, value, x, y, height=.55, degrees=0, colour=SILK):
    """Render own typography using Pillow's embedded font, centred in XY."""
    font = ImageFont.load_default(size=96)
    left, top, right, bottom = font.getbbox(value)
    tile = Image.new("RGBA", (right-left+8, bottom-top+8), (0, 0, 0, 0))
    ImageDraw.Draw(tile).text((4-left, 4-top), value, fill=(*colour, 255), font=font)
    target_h = max(2, round(height*SCALE))
    tile = tile.resize((max(2, round(tile.width*target_h/tile.height)), target_h), Image.Resampling.LANCZOS)
    tile = tile.rotate(degrees, Image.Resampling.BICUBIC, expand=True)
    cx, cy = xy(x, y)
    image.paste(tile, (round(cx-tile.width/2), round(cy-tile.height/2)), tile)


def rounded_pad(image, cx, cy, width, height, degrees=0, colour=GOLD):
    scale = 3
    w, h = round(width*SCALE*scale), round(height*SCALE*scale)
    tile = Image.new("RGBA", (w+8, h+8), (0, 0, 0, 0))
    ImageDraw.Draw(tile).rounded_rectangle((4, 4, w+3, h+3), radius=.12*SCALE*scale, fill=(*colour,255))
    tile = tile.resize((round(tile.width/scale), round(tile.height/scale)), Image.Resampling.LANCZOS)
    tile = tile.rotate(degrees, Image.Resampling.BICUBIC, expand=True)
    x, y = xy(cx,cy)
    image.paste(tile,(round(x-tile.width/2),round(y-tile.height/2)),tile)


def ring(image, x, y, radius=.2):
    draw = ImageDraw.Draw(image)
    cx, cy = xy(x,y)
    r = radius*SCALE
    draw.ellipse((cx-r,cy-r,cx+r,cy+r),fill=GOLD)
    r *= .5
    draw.ellipse((cx-r,cy-r,cx+r,cy+r),fill=BOARD_RGB)


def corner_marks(image, cx, cy, width, height, angle):
    hw, hh = width/2+.19, height/2+.19
    for sx in (-1,1):
        for sy in (-1,1):
            pts = [(sx*(hw-.40), sy*hh),(sx*hw,sy*hh),(sx*hw,sy*(hh-.40))]
            line(image,[rotate_point(x,y,cx,cy,angle) for x,y in pts],width=.075)


def board_images(nodes, params):
    top = grain((2048,2048),BOARD_RGB)
    bottom = grain((2048,2048),BOARD_RGB)
    # Low-contrast short mask-track fragments, an appearance estimate without nets.
    tracks = [[(-12,2.7),(-10.6,2.7),(-9.5,3.8)],
              [(3.1,10.1),(4.0,9.2),(4,7.8)],
              [(-6.4,-7.5),(-4.9,-7.5),(-3.6,-8.8)],
              [(9.7,-3.6),(8.8,-4.5),(8.8,-6.0)],
              [(-2.0,12.0),(-1.2,11.2),(-1.2,9.8)]]
    for pts in tracks:
        line(top,pts,TRACE,.09)
    for n in nodes:
        if n["op"] != "box" or n.get("material") not in {"chip_black","chip_markings_print"}:
            continue
        if "passive" in n["id"]:
            continue  # Do not turn small passive additions into invented print.
        if n["id"].startswith("fc_refine_bottom_"):
            loc = [resolve(v,params) for v in n["transform"]["location"]]
            w,h,_=n["args"]["size"]
            corner_marks(bottom,-loc[0],loc[1],w,h,-n["transform"].get("rotation_deg",[0,0,0])[2])
        elif n["id"].startswith("fc_") and "underside" not in n["id"]:
            loc=[resolve(v,params) for v in n["transform"]["location"]]
            w,h,_=n["args"]["size"]
            corner_marks(top,loc[0],loc[1],w,h,n["transform"].get("rotation_deg",[0,0,0])[2])

    by_id={n["id"]:n for n in nodes}
    def loc(nid):return [resolve(v,params) for v in by_id[nid]["transform"]["location"]]
    # Abbreviated print, not expanded diagram-callout labels. Follow pad centres.
    for label,index in [("G",3),("T1",2),("R1",1),("5V",0)]:
        x,y,_=loc(f"fc_side_pad_left_{index}")
        text_mm(top,label,x+1.22,y,.58)
    for label,index in [("5V",2),("L",1),("GND",0)]:
        x,y,_=loc(f"fc_side_pad_right_{index}")
        text_mm(top,label,x-1.35,y,.59)
    camx,camy,_=loc("camera_connector_base")
    for label,dx,dy in [("CAM",.45,2.25),("GND",1.75,.95),("5V",3.05,-.35)]:
        x,y=camx+dx,camy+dy
        rounded_pad(top,x,y,1.2,.94,45)
        text_mm(top,label,x+1.15,y+1.15,.65,45)
    bx,by,_=loc("fc_round_testpad_0")
    text_mm(top,"+",bx-1.35,by+.95,1.2)
    bx,by,_=loc("fc_round_testpad_1")
    line(top,[(bx-.55,by+.82),(bx+.1,by+.20)],width=.17)
    # Forward-pointing factory-style arrow silhouette; no letter substitution.
    ImageDraw.Draw(top).polygon([xy(*p) for p in [(-.7,-10.3),(0,-8.8),(.7,-10.3),(0,-9.85)]],fill=SILK)
    for x,y in [(-3.1,13.15),(-1.9,12.25),(10.5,-5.8),(11.1,-5.2),(-12.1,-.6),(-2.3,-8.3),(.6,-5.9),(4.5,-5.8)]:
        ring(top,x,y,.10)
    # Four groups of motor-terminal through-pad indications, only printed detail.
    for sx in (-1,1):
        for sy in (-1,1):
            for j in range(3):
                px=params["fc_side_rear_clip_radius"]["value"]-3.55+j*.78
                py=params["fc_body_corner_radius"]["value"]-px-.08
                ring(top,sx*px,sy*py,.32)

    # Bottom image follows actual view handedness; UV flips U on the mesh.
    front=params["fc_front_clip_y"]["value"]
    side_clip=params["fc_side_rear_clip_radius"]["value"]
    text_mm(bottom,"Matrix 5IN1",-3.72,front-1.75,.67,45)
    text_mm(bottom,"V2.1",-side_clip+1.55,-.4,.71,45)
    text_mm(bottom,"+",6.7,-9.2,1.08)
    line(bottom,[(5.0,-10.25),(4.4,-10.85)],width=.14)
    for x in (-1.3,1.3):
        rounded_pad(bottom,x,front-.45,1.0,.8,45)
    for x,y in [(-5.5,7.0),(-6.1,6.15),(4.6,1.4),(5.5,1.4),(-4.5,-3.4),(-5.5,-4.15),(2.4,-5.4),(3.4,-6.35)]:
        ring(bottom,x,y,.19)
    return top,bottom


def chip_atlas():
    atlas=grain((1024,1024),CHIP_RGB)
    # No invented serials or full names inferred solely from diagram callouts.
    for text,col,row,relative_height in [("ST",0,0,.18),("PUYA",1,0,.13),("R001",0,1,.22),("AT7456E",1,1,.11)]:
        font=ImageFont.load_default(size=120)
        box=font.getbbox(text)
        tile=Image.new("RGBA",(box[2]-box[0]+8,box[3]-box[1]+8),(0,0,0,0))
        colour=(77,80,75,255) if text!="R001" else (177,187,185,255)
        ImageDraw.Draw(tile).text((4-box[0],4-box[1]),text,font=font,fill=colour)
        target_h=round(512*relative_height)
        tile=tile.resize((round(tile.width*target_h/tile.height),target_h),Image.Resampling.LANCZOS)
        centre=(col*512+256,row*512+(245 if text=="R001" else 205))
        atlas.paste(tile,(centre[0]-tile.width//2,centre[1]-tile.height//2),tile)
        if text!="R001":
            ImageDraw.Draw(atlas).ellipse((col*512+48,row*512+425,col*512+67,row*512+444),fill=(48,49,45))
    return atlas


def chip_uv(node, tile, bottom=False):
    w,h,_=node["args"]["size"]
    col,row=tile
    u0,v0=col/2,(1-row)/2
    span_x,span_y=2*w,2*h
    x0,y0=-w/2-u0*span_x,-h/2-v0*span_y
    # Mirror selection within the atlas for a bottom face by flipping its artwork
    # locally using negative U extent is disallowed; board etch remains visible
    # under the geometry's chosen package orientation. Renderer flips U globally.
    node["uv_projection"]={"axes":[0,1],"bounds":[x0,y0,x0+span_x,y0+span_y]}
    if bottom:
        # Global flip swaps columns: choose opposite atlas column beforehand.
        mirrored_u0=(1-col)/2
        x0=-w/2-mirrored_u0*span_x
        node["uv_projection"]["bounds"]=[x0,y0,x0+span_x,y0+span_y]
        node["uv_projection"]["flip_u"]=True
    node["material"]="chip_markings_print"


def underside_nodes(params):
    result=[]
    board_side=params["fc_body_side"]["value"]
    for suffix,x,y,w,h,d,angle in BOTTOM_PACKAGES:
        if suffix.endswith("_outer"):
            # Reference estimates are not a calibrated PCB scan. The existing
            # connector size is frozen; move these four estimates along the
            # diagonal edge to preserve a visible separation, rather than
            # intersect the housing. This 0.71 mm local fit is reported.
            x-=math.copysign(.50,x)
            y+=math.copysign(.50,y)
        nid=f"fc_refine_bottom_{suffix}"
        result.append({"id":nid,"op":"box","material":"chip_black","args":{"size":[w,h,d]},
                       "transform":{"location":[{"param":"fc_body_side","scale":x/board_side},{"param":"fc_body_side","scale":y/board_side},{"param":"fc_pcb_bottom_z","offset":-d/2-.035}],"rotation_deg":[0,0,angle]},
                       "modifiers":{"bevel":.035},"evidence":["fc_bottom_surface_diagram","fc_bottom_surface_photo"],
                       "notes":"Reference-estimated underside package, not measured or electrically certified. Height is an explicit estimate. Shared substrate and mount axes unchanged."})
        # Coarse real lead rows; enough to read physically without costly pin meshes.
        sides=4 if "control" in suffix or suffix=="vtx" else 2
        count=8 if suffix=="vtx" else (5 if suffix=="at7456e" else 4)
        for side in range(sides):
            for j in range(count):
                a=side*90 if sides==4 else side*180
                along=(j-(count-1)/2)*(min(w,h)-.65)/count
                lx,ly=along,h/2+.12
                lx,ly=rotate_point(lx,ly,0,0,a)
                px,py=rotate_point(lx,ly,x,y,angle)
                result.append({"id":f"{nid}_lead_{side}_{j}","op":"box","material":"steel","args":{"size":[.13,.34,.08]},
                               "transform":{"location":[{"param":"fc_body_side","scale":px/board_side},{"param":"fc_body_side","scale":py/board_side},{"param":"fc_pcb_bottom_z","offset":-.11}],"rotation_deg":[0,0,angle+a]},
                               "notes":"Simplified visible lead row; pin count is not an electrical specification."})
    for suffix,x,y,w,h,d,angle,material in BOTTOM_PASSIVES:
        nid=f"fc_refine_bottom_passive_{suffix}"
        result.append({"id":nid,"op":"box","material":material,"args":{"size":[w,h,d]},
            "transform":{"location":[{"param":"fc_body_side","scale":x/board_side},{"param":"fc_body_side","scale":y/board_side},{"param":"fc_pcb_bottom_z","offset":-d/2-.035}],"rotation_deg":[0,0,angle]},
            "modifiers":{"bevel":.035},"evidence":["fc_bottom_surface_diagram","fc_bottom_surface_photo"],
            "notes":"Selected observed passive-bank shape; material/type/position/height are visual estimates. No readable marking or electrical-value claim."})
        for sign in (-1,1):
            dx,dy=rotate_point(0,sign*(h/2-.055),0,0,angle)
            result.append({"id":f"{nid}_termination_{sign}","op":"box","material":"solder","args":{"size":[w+.06,.20,min(.25,d*.6)]},
                "transform":{"location":[{"param":"fc_body_side","scale":x/board_side,"offset":dx},{"param":"fc_body_side","scale":y/board_side,"offset":dy},{"param":"fc_pcb_bottom_z","offset":-.11}],"rotation_deg":[0,0,angle]},
                "notes":"Rigid metal termination of the adjacent estimated passive body."})
    return result


def correct_top_details(nodes,params):
    """Resolve the reviewed overhangs and adjacent contacts without moving mounts."""
    by_id={n["id"]:n for n in nodes}
    side=params["fc_body_side"]["value"]
    # Gyro body and all its leads move together away from the NW edge.
    gyro=by_id["fc_gyro"]
    old=[resolve(v,params) for v in gyro["transform"]["location"][:2]]
    new=(-3.935,11.80)
    for n in nodes:
        if n["id"]=="fc_gyro" or n["id"].startswith("fc_gyro_pin_"):
            delta=[round(resolve(v,params)-old[i],10) for i,v in enumerate(n["transform"]["location"][:2])]
            n["transform"]["location"][:2]=[{"param":"fc_body_side","scale":new[i]/side,"offset":delta[i]} for i in (0,1)]
            n["notes"]="Reviewed NW edge fit: gyro cluster shifted0.30mm inward per axis, retaining body dimensions and rigid lead offsets. Position remains estimated."
    targets={
        0:(-1.50,15.10,45),1:(-2.60,14.00,45),
        5:(-9.57,8.25,135),6:(-11.88,5.94,135),
        7:(-11.06,3.46,45),9:(-12.54,-.77,135),10:(9.10,7.29,45),
        20:(-7.09,-7.87,45),21:(-6.25,-9.05,45),
        23:(3.60,-13.10,45),24:(3.60,-11.25,45),
    }
    for index,(x,y,angle) in targets.items():
        body=by_id[f"fc_passive_{index}"]
        body["transform"]["location"][:2]=[{"param":"fc_body_side","scale":v/side} for v in (x,y)]
        body["transform"]["rotation_deg"]=[0,0,angle]
        body["evidence"]=["fc_top_image","fc_top_surface_photo"]
        body["notes"]="Local reference-informed passive fit after independent PCB review. Estimated placement/orientation; existing body dimensions/Z retained."
        for suffix,sign in (("n1",-1),("1",1)):
            cap=by_id[f"fc_passive_solder_{index}_{suffix}"]
            dx,dy=rotate_point(0,sign*(body["args"]["size"][1]/2-.075),0,0,angle)
            cap["transform"]["location"][:2]=[{"param":"fc_body_side","scale":x/side,"offset":dx},{"param":"fc_body_side","scale":y/side,"offset":dy}]
            cap["transform"]["rotation_deg"]=[0,0,angle]
            cap["notes"]="Rigid termination of the reviewed passive; follows the same translation and rotation."
    # The top macro clearly shows leads on all four MCU edges. Existing two
    # rows remain; add two orthogonal rows with the same approximate count.
    stm=by_id["fc_stm32g473"]
    cx,cy=[resolve(v,params) for v in stm["transform"]["location"][:2]]
    w,h,_=stm["args"]["size"]
    angle=stm["transform"]["rotation_deg"][2]
    for sign in (-1,1):
        for j in range(8):
            lx,ly=sign*(w/2+.13),(j-3.5)*(h*.8)/7
            dx,dy=rotate_point(lx,ly,0,0,angle)
            nodes.append({"id":f"fc_stm32g473_pin_side_{sign}_{j}","op":"box","material":"solder","args":{"size":[.46,.22,.14]},
                "transform":{"location":[{"param":"fc_body_side","scale":cx/side,"offset":dx},{"param":"fc_body_side","scale":cy/side,"offset":dy},{"param":"fc_pcb_top_z","offset":.09}],"rotation_deg":[0,0,angle]},
                "evidence":["fc_top_image","fc_top_surface_photo"],"notes":"Four-sided MCU lead presence observed. Eight leads per side are a display approximation, not a claimed package pinout."})


def relocate_motor_connectors(nodes, params):
    """Rejoin the last two wire control points after the approved relocation."""
    by_id={n["id"]:n for n in nodes}
    board_side=params["fc_body_side"]["value"]
    for quadrant,sx,sy in [("front_left",-1,1),("front_right",1,1),("rear_left",-1,-1),("rear_right",1,-1)]:
        centre=(sx*12.4,sy*5.2)
        connector=by_id[f"motor_connector_{quadrant}"]
        connector["transform"]["location"][:2]=[{"param":"fc_body_side","scale":v/board_side} for v in centre]
        connector["evidence"]=["fc_bottom_surface_diagram","fc_bottom_surface_photo"]
        connector["notes"]="Reference-estimated underside edge position with centrally revised board outline. Original housing dimensions/Z/rotation retained."
        wires=[by_id[f"motor_wire_{quadrant}_{s}"] for s in ("n1","0","1")]
        old_mid=[resolve(v,params) for v in wires[1]["args"]["points"][0][:2]]
        offsets=[[resolve(v,params)-old_mid[i] for i,v in enumerate(w["args"]["points"][0][:2])] for w in wires]
        for wire,offset in zip(wires,offsets):
            points=wire["args"]["points"]
            end=[centre[i]+offset[i] for i in (0,1)]
            prior=[resolve(v,params) for v in points[-3][:2]]
            points[-1][:2]=[{"param":"fc_body_side","scale":centre[i]/board_side,"offset":offset[i]} for i in (0,1)]
            points[-2][:2]=[{"param":"fc_body_side","scale":(.6*end[i]+.4*prior[i])/board_side} for i in (0,1)]
            wire["notes"]="Estimated motor-wire route; last two control points refitted to relocated underside connector. Motor-end coordinates, conductor radius and all Z positions retained."


def apply_spec(data, params):
    removed={"silkscreen_board_mark","silkscreen_camera_mark","silkscreen_power_mark","silkscreen_rear_arrow","fc_side_pad_right_3"}
    nodes=[n for n in data["nodes"] if n["id"] not in removed and not n["id"].startswith(("fc_underside_power_","fc_refine_bottom_","fc_stm32g473_pin_side_"))]
    nodes.extend(underside_nodes(params))
    relocate_motor_connectors(nodes,params)
    by_id={n["id"]:n for n in nodes}
    # Preserve package/pad solder-joint offsets as rigid offsets when the board
    # estimate changes. Original positions encoded those offsets in a24mm ratio.
    for n in nodes:
        parent_id=None
        if "_pin_" in n["id"]:parent_id=n["id"].split("_pin_",1)[0]
        elif n["id"].startswith("fc_passive_solder_"):
            parent_id="fc_passive_"+n["id"].split("_")[3]
        elif n["id"].startswith("camera_connector_contact_"):parent_id="camera_connector_base"
        if parent_id not in by_id:continue
        parent=by_id[parent_id]
        for axis in (0,1):
            child_coord=n["transform"]["location"][axis]
            parent_coord=parent["transform"]["location"][axis]
            if isinstance(child_coord,dict) and isinstance(parent_coord,dict) and child_coord.get("param")==parent_coord.get("param")=="fc_body_side":
                ps=parent_coord.get("scale",1)
                delta=LEGACY_TOP_BODY_SIDE*(child_coord.get("scale",1)-ps)+child_coord.get("offset",0)
                n["transform"]["location"][axis]={"param":"fc_body_side","scale":ps,"offset":delta}
    correct_top_details(nodes,params)
    outline=[
        [{"param":"fc_front_clip_half_width","scale":-1},{"param":"fc_front_clip_y"}],
        [{"param":"fc_front_clip_half_width"},{"param":"fc_front_clip_y"}],
        [{"param":"fc_side_rear_clip_radius"},{"param":"fc_side_clip_half_width"}],
        [{"param":"fc_side_rear_clip_radius"},{"param":"fc_side_clip_half_width","scale":-1}],
        [{"param":"fc_side_clip_half_width"},{"param":"fc_side_rear_clip_radius","scale":-1}],
        [{"param":"fc_side_clip_half_width","scale":-1},{"param":"fc_side_rear_clip_radius","scale":-1}],
        [{"param":"fc_side_rear_clip_radius","scale":-1},{"param":"fc_side_clip_half_width","scale":-1}],
        [{"param":"fc_side_rear_clip_radius","scale":-1},{"param":"fc_side_clip_half_width"}],
    ]
    for n in nodes:
        if n['id'].startswith('fc_lug_gold_rim_'):
            n['args']['outer_radius']={'param':'fc_lug_hole_radius','offset':.10}
            n['notes']='Thin estimated inner exposed metal/laminate rim from Matrix II photo; large gold eyelet from earlier model removed after independent visual review.'
        if n["id"] in {"fc_substrate_diamond","fc_soldermask_top","fc_soldermask_bottom"}:
            n["args"]["outline"]=outline
        if n["id"] in {"fc_soldermask_top","fc_soldermask_bottom"}:
            bottom=n["id"].endswith("bottom")
            n["material"]="fc_bottom_print" if bottom else "fc_top_print"
            n["uv_projection"]={"axes":[0,1],"bounds":[-20,-20,20,20]}
            if bottom:n["uv_projection"]["flip_u"]=True
            n["notes"]="Original drawn surface artwork from readable manufacturer evidence; placement and fine mask texture estimated. No photo pixels."
        if n["id"].startswith("fc_side_pad_"):
            sign=-1 if "_left_" in n["id"] else 1
            n["transform"]["location"][0]={"param":"fc_side_rear_clip_radius","scale":sign,"offset":-sign*1.1}
        if n["id"].startswith("fc_side_pad_right_"):
            index=int(n["id"].rsplit("_",1)[1])
            n["transform"]["location"][1]=(-1.85,0,1.85)[index]
            n["notes"]="Three right-lug pads confirmed by manufacturer top photograph, from rear to front GND/L/5V. Spacing remains an image estimate."
            n["evidence"]=["fc_top_image","fc_top_surface_photo"]
        if n["id"] in ATLAS_TILES:
            chip_uv(n,ATLAS_TILES[n["id"]],n["id"].startswith("fc_refine_bottom_"))
    data["nodes"]=nodes
    for record in data["provenance"]:
        if record["feature"]=="PCB outline and installed stack":
            record["note"]="Board body now follows centrally approved26.4mm side estimate with16.2mm front and16.3mm side/rear clips. The shared26mm lug pitch and1mm substrate are unchanged. Top package sizes stay fixed; package centres follow the registry, with rigid pin/solder-cap offsets preserved."
    features={"Printed Matrix II surface reconstruction","Matrix II underside package correction","PCB review perimeter and passive correction"}
    data["provenance"]=[p for p in data["provenance"] if p["feature"] not in features]
    data["provenance"].extend([
        {"feature":"Printed Matrix II surface reconstruction","status":"estimated","confidence":"medium","source_ids":["fc_top_image","fc_top_surface_photo","fc_bottom_surface_diagram"],"note":"Own-drawn textures replace four raised text objects. Only readable physical marks are reproduced; placement/typeface/grain are approximate. Right-lug pad count corrected from four to three. No source-photo mapping or invented serial/lot markings."},
        {"feature":"Matrix II underside package correction","status":"estimated","confidence":"medium","source_ids":["fc_bottom_surface_diagram","fc_bottom_surface_photo"],"note":"Eight uniform placeholders replaced by VTX, AT7456E, four controller and eight power-package estimates.0.85 fit removed after central26.4mm board revision; outer power centres adjusted0.5mm per XY axis to clear connector housings. Four motor connectors/last two wire control points relocated coherently; housing dimensions/Z/rotation and mounts preserved. Heights/lead counts simplified. Polygon uses central clip parameters to preserve lug bores."},
        {"feature":"PCB review perimeter and passive correction","status":"estimated","confidence":"medium","source_ids":["fc_top_image","fc_top_surface_photo","fc_bottom_surface_diagram","fc_bottom_surface_photo"],"note":"Moved two overhanging fore passives and NW gyro rigidly inside board; corrected nearby passive orientations/clearances with both terminations. Added missing two MCU lead rows, with estimated lead count. Added 17 selected underside passive bodies in visible fore-tip and central-package banks, with rigid solder ends; no added labels or blanket printed pattern. One ambiguous central passive omitted to preserve clearance from VTX leads."}
    ])
    return data


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--textures-only",action="store_true",help="Regenerate artwork from the existing spec without editing JSON.")
    parser.add_argument("--spec-only",action="store_true",help="Update JSON only; the integrator can regenerate derived textures before rendering.")
    args=parser.parse_args()
    if args.textures_only and args.spec_only:parser.error("--textures-only and --spec-only are mutually exclusive")
    path=ROOT/"specs/components/electronics.json"
    data=json.loads(path.read_text())
    params=json.loads((ROOT/"specs/spatial_architecture.json").read_text())["parameters"]
    old_count=len(data["nodes"])
    if not args.textures_only:data=apply_spec(data,params)
    if not args.spec_only:
        top,bottom=board_images(data["nodes"],params)
        dest=ROOT/"assets/textures"
        dest.mkdir(parents=True,exist_ok=True)
        for name,im in [("fc_top.png",top),("fc_bottom.png",bottom),("chip_markings.png",chip_atlas())]:
            out=dest/name
            im.save(out,optimize=False,compress_level=9)
            print(f"{out.relative_to(ROOT)} {im.width}x{im.height} sha256={hashlib.sha256(out.read_bytes()).hexdigest()}")
    if not args.textures_only:
        path.write_text(json.dumps(data,indent=2)+"\n")
        print(f"electronics nodes {old_count} -> {len(data['nodes'])}; shared dimensions untouched")


if __name__=="__main__":main()
