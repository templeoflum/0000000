"""Import saved clip programs against a captured native composition. No writes to Arena."""
import argparse,json,re,xml.etree.ElementTree as ET
from pathlib import Path
from authored import xml_program,equal

def build(native,soup,feedback):
    refs={};fm={};report={'matched':[],'unmatched':[],'parameter_changes':[],'skipped':[]}
    for path in (soup,feedback):
        root=ET.parse(path).getroot()
        for deck in root.findall('Deck'):
            for c in deck.findall('Clip'):
                refs.setdefault(int(c.get('uniqueId')),(str(path),c))
                if path==feedback:fm[(int(deck.get('deckIndex','0'))+1,int(c.get('layerIndex'))+1,int(c.get('columnIndex'))+1)]=(str(path),c)
    stage={m['id'] if isinstance(m,dict) else m for g in native.get('layergroups',[]) if g.get('name',{}).get('value','').startswith('__stage__') for m in g.get('layers',[])}
    profiles={}
    for layer in native['layers']:
        if layer['id'] in stage:continue
        for clip in layer.get('clips',[]):
            v=clip.get('video')
            if not v:continue
            name=clip['name']['value'];match=re.search(r'^FM · .*\[(\d+)\.(\d+)\.(\d+)\]$',name)
            ref=fm.get(tuple(map(int,match.groups()))) if match else refs.get(clip['id'])
            if not ref:report['unmatched'].append(dict(id=clip['id'],name=name,layer=layer['name']['value']));continue
            path,x=ref;targets=[]
            def target(tid,kind,params,nodes,effect_name=None):
                converted=[]
                for p in nodes:
                    key=p.get('name');lp=params.get(key)
                    if not lp:report['skipped'].append([name,key,'not exposed']);continue
                    try:q=xml_program(p,lp)
                    except (ValueError,IndexError,KeyError):q=None
                    if not q:report['skipped'].append([name,key,'unsupported or changed']);continue
                    converted.append(q)
                    if q.get('source','static')=='static' and not equal(q['value'],lp.get('value')):report['parameter_changes'].append(dict(clip=clip['id'],clip_name=name,target=tid,parameter=key,id=q['id'],before=lp.get('value'),original=q['value']))
                if converted:targets.append(dict(id=tid,identity=[kind,'clip',layer['id'],clip['id'],effect_name],params=converted))
            source=x.find('./VideoTrack/PrimarySource/VideoSource/RenderPass')
            if source is not None and (v.get('sourceparams') or {}):
                target('source:'+str(clip['id']),'source',v['sourceparams'],source.findall('./Params/*'))
            effects=x.findall('./VideoTrack/RenderPass[@name="RenderPassChain"]/RenderPass');seen={}
            for old in effects:
                ename=old.get('name');ordinal=seen.get(ename,0);seen[ename]=ordinal+1
                exact=next((e for e in v.get('effects',[]) if str(e['id'])==old.get('uniqueId') and e['name']==ename),None)
                candidates=[e for e in v.get('effects',[]) if e['name']==ename];live=exact or (candidates[ordinal] if len(candidates)>ordinal else None)
                if not live:report['skipped'].append([name,ename,'effect missing or replaced']);continue
                nodes=old.findall('./Params/*')+old.findall('./RenderPass/Params/*')
                target('effect:'+str(live['id']),'effect',{**(live.get('params') or {}),**(live.get('mixer') or {})},nodes,ename)
            if targets:
                profiles[str(clip['id'])]=dict(id=clip['id'],name=name,layer_id=layer['id'],reference=path,reference_clip=x.get('uniqueId'),targets=targets)
                report['matched'].append(dict(id=clip['id'],name=name,layer=layer['name']['value'],reference=Path(path).name,parameters=sum(len(t['params']) for t in targets),timelines=sum(p.get('source')=='timeline' for t in targets for p in t['params'])))
            else:report['unmatched'].append(dict(id=clip['id'],name=name,layer=layer['name']['value'],reason='No serialized source/effect controls'))
    return dict(epoch=str(native['name']['id']),clips=profiles),report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('native');p.add_argument('soup');p.add_argument('feedback');p.add_argument('--output',default='authored-clips.json');a=p.parse_args()
    profiles,report=build(json.loads(Path(a.native).read_text()),Path(a.soup),Path(a.feedback));Path(a.output).write_text(json.dumps(profiles,indent=2)+'\n');Path('checks/authored-clip-audit-2026-09-11.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(clips=len(profiles['clips']),parameters=sum(len(t['params']) for c in profiles['clips'].values() for t in c['targets']),timelines=sum(m['timelines'] for m in report['matched']),static_differences=len(report['parameter_changes']),unmatched=len(report['unmatched']),skipped=len(report['skipped']))))
