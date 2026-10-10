#!/usr/bin/env python3
"""Public preview of eight DEVELOPMENT observations."""
import json
from pathlib import Path
import sys
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from visual_control.environment import Environment
from visual_control.contract import FAMILIES,TIERS
rows=[json.loads(x) for x in (ROOT/"data/development/scenes.jsonl").read_text().splitlines()]
canvas=Image.new("RGB",(768,8*410),"white");draw=ImageDraw.Draw(canvas)
for i,(family,tier) in enumerate((f,t) for f in FAMILIES for t in TIERS):
    row=next(r for r in rows if r["family"]==family and r["tier"]==tier);env=Environment(row)
    draw.text((8,i*410+5),family+" / "+tier+" — top | oblique",fill="black")
    canvas.paste(env.render("top"),(0,i*410+26));canvas.paste(env.render("oblique"),(384,i*410+26))
canvas.save(ROOT/"evidence/development-preview.png")
print("Rendered eight public-development examples; no model calls.")
