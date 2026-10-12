"""Arrange original renders and attributed reference thumbnails for inspection."""
import argparse
from pathlib import Path

from PIL import Image,ImageDraw,ImageFont,ImageOps

ROOT=Path(__file__).resolve().parents[1]


def font(size):
    return ImageFont.load_default(size=size)


def card(canvas,path,box,label):
    x,y,w,h=box
    draw=ImageDraw.Draw(canvas)
    draw.rounded_rectangle((x,y,x+w,y+h),radius=12,fill="#ffffff",outline="#d3d9df",width=1)
    im=Image.open(path).convert("RGB")
    im=ImageOps.contain(im,(w-16,h-54))
    canvas.paste(im,(x+(w-im.width)//2,y+8+(h-54-im.height)//2))
    draw.text((x+16,y+h-35),label,font=font(20),fill="#283747")


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",default="output/final")
    args=parser.parse_args()
    output=ROOT/args.output
    w,h=480,455
    canvas=Image.new("RGB",(1500,1535),"#ecf0f3")
    draw=ImageDraw.Draw(canvas)
    draw.text((30,23),"AIR65 II / RACING",font=font(37),fill="#172b41")
    draw.text((30,70),"Parametric recreation · millimetres · Cycles / Blender 5.2.2",font=font(19),fill="#45586b")
    names=[("hero","Assembly / three-quarter"),("reference","Assembly / perspective"),("top","Top / orthographic"),("front","Front / orthographic"),("right","Right / orthographic"),("left","Left / orthographic"),("rear","Rear / orthographic"),("underside","Underside / dry aircraft")]
    for i,(name,label) in enumerate(names):
        card(canvas,output/(name+".png"),(20+(i%3)*493,112+(i//3)*467,w,h),label)
    x,y=20+2*493,112+2*467
    draw.rounded_rectangle((x,y,x+w,y+h),radius=12,fill="#ffffff",outline="#d3d9df")
    draw.text((x+28,y+32),"Nominal anchors",font=font(28),fill="#172b41")
    lines=["65 mm motor diagonal","82.6 x 82.6 x 15.1 mm frame","33 mm duct opening","31 mm propeller sweep","25° selected camera setting","","Shape and optical details include","documented visual estimates.","See validation report for limits."]
    for j,line in enumerate(lines):
        draw.text((x+28,y+88+j*31),line,font=font(21),fill="#45586b")
    canvas.save(output/"multiview.png")
    comparison=Image.new("RGB",(1500,660),"#ecf0f3")
    draw=ImageDraw.Draw(comparison)
    draw.text((24,22),"Visual revision / qualitative comparison",font=font(31),fill="#172b41")
    for i,(path,label) in enumerate([(ROOT/"output/review_v1/hero.png","First integrated model"),(output/"hero.png","Revised model"),(ROOT/"references/photo_racing_oblique.webp","Physical Racing reference / Drone Vortex")]):
        card(comparison,path,(20+i*493,80,480,500),label)
    draw.text((26,600),"Views, lighting and sample motor colors differ. Images are not calibrated; no pixel-accuracy claim is made.",font=font(19),fill="#45586b")
    comparison.save(ROOT/"reports/visual_comparison.png")
    print(output/"multiview.png")


if __name__=="__main__":
    main()
