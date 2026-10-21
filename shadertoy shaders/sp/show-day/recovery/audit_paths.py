"""Read-only saved composition path inventory; writes only beside this script."""
from pathlib import Path
from collections import Counter
import json, xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[3]
files=list((ROOT/'sp/restored-compositions').rglob('*.avc'))+list((ROOT/'sp/engine/patches').glob('*.avc'))+[ROOT/'sp/design/heart-performance-plan/Heart Performance.avc']
result=[]
for file in sorted(files):
    root=ET.parse(file).getroot(); refs=[]; presets=[]
    for node in root.iter():
        for attr,value in node.attrib.items():
            if attr.lower() in ('filename','path','filepath') and value:
                p=Path(value); resolved=p if p.is_absolute() else file.parent/p
                refs.append({'tag':node.tag,'attribute':attr,'path':value,'exists':resolved.exists(),'resolved':str(resolved)})
        name=node.get('name','')
        if name.endswith('ShortcutPreset'):
            kind={'Midi':'MIDI','Osc':'OSC','Dmx':'DMX','Keyboard':'Keyboard'}.get(name.removesuffix('ShortcutPreset'))
            if kind:
                p=Path.home()/'Documents/Resolume Arena/Shortcuts'/kind/(node.get('value','')+'.xml')
                presets.append({'kind':kind,'name':node.get('value'),'path':str(p),'exists':p.exists()})
    counts=Counter((r['path'],r['exists']) for r in refs)
    result.append({'composition':str(file),'dimensions':root.find('CompositionInfo').attrib,'reference_count':len(refs),'missing_reference_count':sum(not r['exists'] for r in refs),'unique_missing_count':len({r['path'] for r in refs if not r['exists']}),'references':[{'path':p,'exists':e,'occurrences':n} for (p,e),n in counts.items()],'shortcut_presets':presets})
out=Path(__file__).with_name('PATH-INVENTORY.json'); out.write_text(json.dumps({'scope':'Saved XML fileName/path/filePath attributes; existence only, not decoding, plugin installation or live routing. Relative paths resolved against composition directory.','compositions':result},indent=2)+'\n')
for item in result:
    print(Path(item['composition']).relative_to(ROOT),item['reference_count'],item['missing_reference_count'],item['unique_missing_count'])
