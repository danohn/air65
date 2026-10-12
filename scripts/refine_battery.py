"""Deterministically author a reference-based LAVA II 280 mAh wrapper and pouch.

All imagery is drawn here, not copied from the manufacturer photo. Text values
are legible in the selected 280 mAh reference; exact typography and motif paths
are estimated. The frozen 54 x 10 x 6 mm body envelope is retained.
"""
import math
from PIL import Image, ImageDraw, ImageFont
from contracts import ROOT, read_json, write_json


def p(name, scale=1, offset=0):
    return {"param":name,"scale":scale,"offset":offset}


def n(name,op,material,args,location=(0,0,0),bevel=None,rotation=None):
    value={"id":name,"op":op,"material":material,"args":args,"transform":{"location":list(location)}}
    if bevel: value["modifiers"]={"bevel":bevel}
    if rotation: value["transform"]["rotation_deg"]=rotation
    return value


def lettering(canvas, xy, body, size, fill, stroke=0, outline=None, italic=True):
    font=ImageFont.load_default(size=size)
    left,top,right,bottom=font.getbbox(body,stroke_width=stroke)
    pad=4
    tile=Image.new('RGBA',(right-left+2*pad,bottom-top+2*pad))
    ImageDraw.Draw(tile).text((pad-left,pad-top),body,font=font,fill=fill,stroke_width=stroke,stroke_fill=outline or fill)
    if italic:
        lean=.16
        tile=tile.transform((tile.width+math.ceil(lean*tile.height),tile.height),Image.Transform.AFFINE,(1,lean,-lean*tile.height,0,1,0),Image.Resampling.BICUBIC)
    canvas.paste(tile,(round(xy[0]+left-pad),round(xy[1]+top-pad)),tile)


def textures():
    folder=ROOT/"assets/textures"; folder.mkdir(parents=True,exist_ok=True)
    w,h=1536,320
    image=Image.new("RGB",(w,h))
    d=ImageDraw.Draw(image)
    for y in range(h):
        t=y/(h-1)
        d.line([(0,y),(w,y)],fill=(int(96+139*t),int(208+36*t),int(35-16*t)))
    # Angular printing follows the reference's direction/density, not exact pixels.
    dark=(30,33,32); yellow=(238,236,64); white=(224,235,213)
    for points in [
      [(0,0),(330,0),(198,32),(285,62),(115,48),(60,100),(0,90)],
      [(0,142),(138,110),(93,82),(263,54),(180,111),(52,164),(0,218)],
      [(350,0),(685,0),(620,45),(725,70),(560,60),(501,29)],
      [(895,0),(1150,0),(1030,45),(1288,30),(1190,84),(980,55)],
      [(1170,150),(1536,37),(1536,86),(1320,173),(1490,136),(1536,172),(1536,230),(1230,250)],
      [(780,320),(1536,320),(1536,289),(1310,299),(1380,256),(1050,284),(1144,239),(991,253)],
      [(50,320),(172,301),(338,305),(432,264),(568,273),(666,214),(732,234),(666,292),(807,295),(763,320)],
    ]: d.polygon(points,fill=dark)
    for pts in [[(770,280),(870,250),(816,246),(998,202)],[(1420,0),(1360,40),(1500,12)],[(400,18),(340,43),(482,29)]]:
        d.line(pts,fill=yellow,width=8)
    d.line([(0,23),(47,42),(75,35),(116,49),(177,31),(210,47),(260,30),(329,49),(373,41),(431,64),(477,48),(523,63),(570,57),(611,91),(665,81),(696,96),(733,82),(788,99),(840,118),(889,119),(940,149),(970,139),(1008,159),(1069,153),(1112,174),(1160,167),(1200,199),(1270,196),(1330,236),(1400,219),(1470,241),(1536,233)],fill=white,width=5)
    for xy,body,size,border,weight in [((95,51),'280',127,9,4),((389,55),'95C',65,6,2),((395,128),'mAh',43,4,1),((97,218),'LiHV 3.8V 1.06Wh',54,5,2)]:
        lettering(image,xy,body,size,dark,border,yellow)
        lettering(image,xy,body,size,dark,weight,dark)
    # Large outlined LAVA wordmark; deliberate hand-authored typography approximation.
    lettering(image,(777,36),'LAVA',218,white,23,white)
    lettering(image,(777,36),'LAVA',218,dark,16,dark)
    lettering(image,(777,36),'LAVA',218,yellow,9,yellow)
    d.line([(778,276),(882,298),(1126,271),(1469,177)],fill=yellow,width=6)
    d.rectangle((0,0,w-1,h-1),outline=(29,32,28),width=5)
    image.save(folder/"battery_280_wrapper.png",optimize=False)
    cap=Image.new("RGB",(512,1024),(26,28,27)); cd=ImageDraw.Draw(cap)
    # Rotate the cap's brand printing with the label's transverse orientation.
    logo=Image.new("RGBA",(820,130)); ld=ImageDraw.Draw(logo)
    lettering(logo,(15,12),'BETAFPV',99,(111,194,62,255),stroke=1,italic=False)
    logo=logo.rotate(90,expand=True)
    cap.paste(logo,((512-logo.width)//2,(1024-logo.height)//2),logo)
    cap.save(folder/"battery_cap.png",optimize=False)


def component():
    # Flat faces with rounded folded shoulders rather than a bevelled cuboid.
    profile=[]
    for cx,cz,start in [(4.28,2.28,0),(-4.28,2.28,90),(-4.28,-2.28,180),(4.28,-2.28,270)]:
        for i in range(9):
            a=math.radians(start+i*90/8)
            profile.append([cx+.67*math.cos(a),cz+.67*math.sin(a)])
    sections=[]
    for y,scale in [(p('battery_length',-.5,5),.965),(p('battery_length',-.5,5.8),1),(0,1),(p('battery_length',.5,-1),1),(p('battery_length',.5),.96)]:
        sections.append({'y':y,'profile':[[p('battery_width',x*scale/10),p('battery_height',z*scale/6)] for x,z in profile]})
    nodes=[n('foil_cell','loft_shell','battery_sleeve',{'sections':sections,'closed_profile':True,'cap_ends':True},[0,0,p('battery_center_z')]),
           n('terminal_cap','box','battery_sleeve',{'size':[p('battery_width'),5,p('battery_height',1,-.004)]},[0,p('battery_length',-.5,2.5),p('battery_center_z')],.24)]
    # A one-sided printed face avoids projecting the top logo through the cap
    # onto its underside. The 0.002 mm ink offset stays in the body envelope.
    cap_print=n('terminal_cap_top_print','mesh','battery_cap_print',{'vertices':[[-4.75,-2.25,3],[4.75,-2.25,3],[4.75,2.25,3],[-4.75,2.25,3]],'faces':[[0,1,2,3]]},[0,p('battery_length',-.5,2.5),p('battery_center_z')])
    cap_print['uv_projection']={'axes':[1,0],'bounds':[-2.5,-5,2.5,5],'flip_v':True}
    nodes.append(cap_print)
    for side,z in [('top',2.975),('bottom',-2.975)]:
        xs=[-4.85,-4.72,-4.52,-4.28,0,4.28,4.52,4.72,4.85]
        zs=[2.56,2.79,2.94,2.99,2.99,2.99,2.94,2.79,2.56]
        vertices=[[x,y,h*(1 if side=='top' else -1)] for y in [-24,-23.5,23.5,24] for x,h in zip(xs,zs)]
        faces=[[r*9+i,r*9+i+1,(r+1)*9+i+1,(r+1)*9+i] for r in range(3) for i in range(8)]
        node=n('label_'+side,'mesh','battery_wrapper_print',{'vertices':vertices,'faces':faces},[0,2.5,p('battery_center_z')])
        node['modifiers']={'solidify':.02}
        node['smooth']=True
        node['uv_projection']={'axes':[1,0],'bounds':[-24,-4.85,24,4.85],'flip_v':side=='top'}
        nodes.append(node)
    # Thin foil seam and folded end lip inside the existing nominal envelope.
    for side in [-1,1]:
        nodes.append(n('pouch_fold_'+str(side).replace('-','n'),'tube','battery_foil',{'points':[[side*4.86,-21.5,p('battery_center_z',1,-2.46)],[side*4.975,-18,p('battery_center_z',1,-2.51)],[side*4.975,22.5,p('battery_center_z',1,-2.51)],[side*4.75,26.9,p('battery_center_z',1,-2.41)]],'radius':.014,'smooth':False,'resolution':8}))
    nodes.append(n('sealed_end_lip','box','battery_foil',{'size':[9.4,.10,5.15]},[0,p('battery_length',.5,-.11),p('battery_center_z')],.045))
    # Black BT2.0 shroud; an annular rim and dark recess make the sockets readable.
    nodes.extend([n('terminal_connector','box','battery_sleeve',{'size':[3.8,5,3.9]},[0,p('battery_length',-.5,-2.1),p('battery_center_z')],.28),n('terminal_neck','box','battery_sleeve',{'size':[2.3,2,2.8]},[0,p('battery_length',-.5,-4.9),p('battery_center_z')],.10)])
    for side,x in [('left',-.8),('right',.8)]:
        nodes.append(n('contact_rim_'+side,'annulus','steel',{'inner_radius':.32,'outer_radius':.43,'depth':.11,'segments':32},[x,p('battery_length',-.5,-6.0),p('battery_center_z')],rotation=[90,0,0]))
        nodes.append(n('contact_recess_'+side,'cylinder','wire_black',{'radius':.315,'depth':.16,'segments':32},[x,p('battery_length',-.5,-5.91),p('battery_center_z')],rotation=[90,0,0]))
    source=read_json(ROOT/'specs/components/battery.json')
    source['description']='Optional LAVA II 280mAh reference accessory: folded pouch, authored printed wrapper, black BT2.0 terminal; unplugged display pose.'
    source['nodes']=nodes
    source['provenance']=[{'feature':'body envelope','status':'verified','source_ids':['batteryii','battery_drawing'],'confidence':'high','note':'54 x 10 x 6 mm nominal body; connector nose excluded by published drawing. Published anchor values unchanged.'},{'feature':'wrapper text and black terminal color','status':'verified','source_ids':['batteryii','battery_drawing','lava_ii_280_surface_photo'],'confidence':'high','note':'Visible 280,95C,mAh,LiHV 3.8V 1.06Wh,LAVA and cap BETAFPV are transcribed from the selected 280mAh product photo. No II or 1S text invented on this face.'},{'feature':'graphic layout, pouch folds and terminal recesses','status':'estimated','source_ids':['battery_drawing','lava_ii_280_surface_photo'],'confidence':'medium','note':'Own deterministic redraw; typography, color values, motif placement and local crease/shell depths are approximate. Black shroud replaces incorrect prior white connector. Printed detail is a UV texture with no raised lettering. Reverse-face graphic is unverified and repeats the visible front label as an explicit estimate. Body remains in nominal envelope.'}]
    write_json(ROOT/'specs/components/battery.json',source)


if __name__=='__main__':
    textures(); component()
