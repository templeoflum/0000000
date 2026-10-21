#!/usr/bin/env python3
"""lint_isf.py <file.fs>...  — wrap an ISF fragment as plain GLSL and run glslang on it."""
import sys,re,json,subprocess,tempfile,os
GL={"float":"float","bool":"bool","long":"int","point2D":"vec2","color":"vec4","image":"sampler2D","audio":"sampler2D","audioFFT":"sampler2D","event":"bool"}
PRE="""#version 410 compatibility
uniform vec2 RENDERSIZE; uniform float TIME; uniform float TIMEDELTA; uniform vec4 DATE; uniform int PASSINDEX; uniform int FRAMEINDEX;
varying vec2 isf_FragNormCoord;
"""
def lint(path):
    s=open(path,errors='ignore').read()
    m=re.search(r'/\*(\{.*?\})\*/',s,re.S)
    if not m: return ["NO ISF HEADER"]
    try: hdr=json.loads(m.group(1))
    except Exception as e: return [f"BAD HEADER JSON: {e}"]
    uni="".join(f"uniform {GL.get(i['TYPE'],'float')} {i['NAME']};\n" for i in hdr.get("INPUTS",[]))
    for ps in hdr.get("PASSES",[]):
        if ps.get("TARGET"): uni+=f"uniform sampler2D {ps['TARGET']};\n"
    body=s[m.end():]
    body=re.sub(r'IMG_NORM_PIXEL\((\w+),',r'texture2D(\1,',body); body=re.sub(r'IMG_PIXEL\((\w+),',r'texture2D(\1,',body); body=re.sub(r'IMG_THIS_PIXEL\((\w+)\)',r'texture2D(\1,isf_FragNormCoord)',body)
    src=PRE+uni+body
    with tempfile.NamedTemporaryFile('w',suffix='.frag',delete=False) as f: f.write(src); p=f.name
    r=subprocess.run(["glslang",p],capture_output=True,text=True); os.unlink(p)
    errs=[l for l in (r.stdout+r.stderr).splitlines() if l.startswith("ERROR") and "compilation errors" not in l]
    return errs
if __name__=="__main__":
    bad=0
    for path in sys.argv[1:]:
        e=lint(path); name=os.path.basename(path)
        if e: bad+=1; print(f"✗ {name}"); [print("    ",x[:160]) for x in e[:4]]
        else: print(f"✓ {name}")
    print(f"\n{len(sys.argv)-1-bad}/{len(sys.argv)-1} clean")
