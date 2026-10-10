"""Small deterministic RGB PNG renderer; no fonts, network or image model."""
import struct
import zlib
from pathlib import Path

DIGITS = {
"0":["111","101","101","101","111"],"1":["010","110","010","010","111"],
"2":["111","001","111","100","111"],"3":["111","001","111","001","111"],
"4":["101","101","111","001","001"],"5":["111","100","111","001","111"],
"6":["111","100","111","101","111"],"7":["111","001","010","010","010"],
"8":["111","101","111","101","111"],"9":["111","101","111","001","111"],
"-":["000","000","111","000","000"]}

def render(params, path):
    w = h = 448
    pixels = bytearray([255] * w * h * 3)
    def rect(x0, y0, x1, y1, color):
        for y in range(max(0,y0), min(h,y1)):
            for x in range(max(0,x0), min(w,x1)):
                off = (y*w+x)*3
                pixels[off:off+3] = bytes(color)
    def number(value,x,y,scale=2):
        for i,ch in enumerate(str(value)):
            for yy,row in enumerate(DIGITS[ch]):
                for xx,bit in enumerate(row):
                    if bit == "1":
                        rect(x+i*4*scale+xx*scale,y+yy*scale,x+i*4*scale+(xx+1)*scale,y+(yy+1)*scale,(20,20,20))
    if params["kind"] == "grid":
        n = params["n"]
        cell = 360 // n
        for r in range(n):
            for c in range(n):
                color = (220,35,40) if (r,c) == tuple(params["target"]) else (50,110,200)
                rect(50+c*cell+4,45+r*cell+4,50+(c+1)*cell-4,45+(r+1)*cell-4,color)
        for i in range(n):
            number(i+1,25,45+i*cell+cell//2-5)
            number(i+1,50+i*cell+cell//2-3,415)
    else:
        for v in range(0,41,5):
            y=390-v*8
            rect(45,y,420,y+1,(215,215,215))
            number(v,12,y-5)
        colors=[(50,110,200),(50,160,90),(235,150,20),(140,70,180)]
        for i,v in enumerate(params["values"]):
            rect(65+i*85,390-v*8,112+i*85,390,colors[i])
            number(i+1,84+i*85,410)
        rect(44,65,46,391,(20,20,20))
        rect(44,390,422,392,(20,20,20))
    raw = b"".join(b"\0"+bytes(pixels[y*w*3:(y+1)*w*3]) for y in range(h))
    def chunk(kind,data):
        return struct.pack(">I",len(data))+kind+data+struct.pack(">I",zlib.crc32(kind+data)&0xffffffff)
    out=b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",struct.pack(">IIBBBBB",w,h,8,2,0,0,0))+chunk(b"IDAT",zlib.compress(raw,9))+chunk(b"IEND",b"")
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(out)

