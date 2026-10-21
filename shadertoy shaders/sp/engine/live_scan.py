"""Parse large Arena compositions outside the motion process; preserve active controls."""
import json
import sys
import urllib.request
import clip_catalog

def compact(comp):
    catalog=clip_catalog.build(comp)
    for layer in comp.get('layers',[]):
        for i,clip in enumerate(layer.get('clips',[])):
            video=clip.get('video')
            if not video or 'Connected' in str(clip.get('connected',{}).get('value','')):continue
            layer['clips'][i]={k:clip[k] for k in ('id','name','connected') if k in clip}
            layer['clips'][i]['video']={'description':video.get('description')}
    comp['_heart_catalog']=catalog
    return comp

if __name__=='__main__':
    for line in sys.stdin:
        try:
            with urllib.request.urlopen(line.strip()+'/composition',timeout=15) as response:
                result=compact(json.load(response))
            print(json.dumps(result,separators=(',',':')),flush=True)
        except Exception as exc:print(json.dumps({'_scan_error':str(exc)}),flush=True)
