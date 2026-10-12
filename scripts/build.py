"""Validate source JSON, resolve the assembly, and invoke a local headless Blender."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

from jsonschema.exceptions import ValidationError

from contracts import ROOT, prepare, write_json


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assembly",default="specs/assembly.json")
    parser.add_argument("--output",default="output/final")
    parser.add_argument("--blender",default=os.environ.get("BLENDER_BIN"))
    parser.add_argument("--resolution",type=int,default=1100)
    parser.add_argument("--samples",type=int,default=48)
    parser.add_argument("--views",default="hero,top,front,right,left,rear,underside,reference")
    parser.add_argument("--no-render",action="store_true")
    parser.add_argument("--validate-only",action="store_true")
    args=parser.parse_args()
    if not 64<=args.resolution<=8192 or not 1<=args.samples<=4096:
        parser.error("Resolution must be 64–8192 and samples 1–4096")
    try:
        data=prepare(ROOT/args.assembly)
        output=(ROOT/args.output).resolve()
        output.mkdir(parents=True,exist_ok=True)
        resolved=output/"resolved_assembly.json"
        write_json(resolved,data)
        print(f"Validated {len(data['components'])} components and {len(data['assembly']['instances'])} instances",flush=True)
        if args.validate_only:
            return
        blender=args.blender or shutil.which("blender")
        if not blender and Path("/Applications/Blender.app/Contents/MacOS/Blender").exists():
            blender="/Applications/Blender.app/Contents/MacOS/Blender"
        if not blender or not Path(blender).exists():
            parser.error("Blender not found. Pass --blender /absolute/path/to/Blender or set BLENDER_BIN.")
        cmd=[blender,"--background","--factory-startup","--python-exit-code","1","--python",str(ROOT/"scripts/blender_render.py"),"--","--input",str(resolved),"--output",str(output),"--resolution",str(args.resolution),"--samples",str(args.samples),"--views",args.views]
        if args.no_render:
            cmd.append("--no-render")
        log=output/"build.log"
        print(f"Headless Blender started; log: {log}",flush=True)
        with log.open("w") as stream:
            process=subprocess.run(cmd,stdout=stream,stderr=subprocess.STDOUT)
        if process.returncode:
            print(log.read_text()[-8000:],file=sys.stderr)
            raise RuntimeError(f"Blender exited {process.returncode}; see {log}")
        print(f"Build complete: {output / 'air65_ii.blend'}",flush=True)
    except (ValueError,KeyError,OSError,RuntimeError,ValidationError) as exc:
        print(f"air65: {exc}",file=sys.stderr)
        sys.exit(1)


if __name__=="__main__":
    main()
