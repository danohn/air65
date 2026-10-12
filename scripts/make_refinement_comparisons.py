"""Preserve labelled before/after views at identical authored camera settings."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/refinement'
OUT.mkdir(parents=True,exist_ok=True)
font=ImageFont.load_default(size=20)
small=ImageFont.load_default(size=15)


def pairs(title, pairs, filename):
    width=1300; tile=620; band=70
    image=Image.new('RGB',(width,band+len(pairs)*(tile+38)), '#f7f7f4')
    d=ImageDraw.Draw(image);d.text((25,14),title,font=font,fill='#242b23')
    d.text((25,44),'BEFORE — preserved baseline',font=small,fill='#5e675b')
    d.text((665,44),'AFTER — refined source, same camera and studio',font=small,fill='#5e675b')
    for row,(label,left,right) in enumerate(pairs):
        y=band+row*(tile+38)
        for col,path in enumerate([left,right]):
            source=Image.open(ROOT/path).convert('RGB');source.thumbnail((tile,tile))
            image.paste(source,(20+col*645+(tile-source.width)//2,y+(tile-source.height)//2))
        d.text((25,y+tile+8),label,font=small,fill='#40493a')
    image.save(OUT/filename)


if __name__=='__main__':
    pairs('Air65 II canopy / assembly refinement',[(name,'output/refinement_baseline/final/'+name+'.png','output/final/'+name+'.png') for name in ['hero','reference','front','right','top']], 'before_after_assembly.jpg')
    pairs('LAVA II 280 mAh — optional battery refinement',[(name,'output/refinement_baseline/with_battery/'+name+'.png','output/with_battery/'+name+'.png') for name in ['hero','underside']], 'before_after_battery.jpg')
    pairs('Continuous canopy — identical inspection cameras',[(name,'output/refinement_baseline/inspection/'+name+'.png','output/refinement_inspection/'+name+'.png') for name in ['canopy_oblique','canopy_front','canopy_right']], 'before_after_canopy.jpg')
    pairs('Matrix II board — estimated body and surface reconstruction',[(name,'output/refinement_baseline/inspection/'+name+'.png','output/refinement_inspection/'+name+'.png') for name in ['pcb_top','pcb_bottom']], 'before_after_pcb.jpg')
    pairs('Selected LAVA II 280 mAh — pouch and printed wrapper', [('Battery close-up','output/refinement_baseline/inspection/battery_closeup.png','output/refinement_inspection/battery_closeup.png')], 'before_after_battery_closeup.jpg')
    print(OUT)
