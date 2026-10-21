"""Read-only final pair check. No server calls, writes or engine import."""
import argparse, hashlib, json, sys
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'sp/engine'))
from patches import validate_snapshot, composition_signature
from dependencies import validate_contract


def verify(avc,sources,effects,live=None,after=None):
    companion=avc.with_suffix('.json')
    paths=[avc,companion]
    before={p:(p.stat().st_size,p.stat().st_mtime_ns) for p in paths}
    assert all(size>0 for size,_ in before.values()),'Empty pair file'
    if after is not None:
        assert all(p.stat().st_mtime>=after for p in paths),'Pair predates save start'
    assert not companion.with_suffix('.json.tmp').exists(),'Incomplete companion temporary file remains'
    data=json.loads(companion.read_text());tree=ET.parse(avc)
    assert data['version']==1 and data['name']==avc.stem,'Wrong name/version'
    assert data['composition']==avc.name,'Wrong companion composition filename'
    for key in ('instruments','effects','layers','signature','dependencies'):
        assert isinstance(data[key],dict),f'Missing/invalid {key}'
    assert isinstance(data['hold'],bool),'Invalid Hold state'
    assert isinstance(data['bars'],(int,float)) and data['bars']>0,'Invalid bars'
    validate_snapshot(avc,data['layers'])
    errors=validate_contract(data['dependencies'],avc,sources=sources,effects=effects)
    assert not errors,'; '.join(errors)
    if live is not None:
        # Canonical JSON converts signature tuples to the serialized list form.
        assert json.loads(json.dumps(composition_signature(live)))==data['signature'],'Live/saved signature mismatch'
    scratch=[]
    for deck in tree.getroot().findall('Deck'):
        for clip in deck.findall('Clip'):
            # Arena serializes empty slots as attribute-only Clip nodes and may
            # retain uniqueId. Also tolerate empty PrimarySource containers.
            nonempty=any(len(primary)>0 for track in ('VideoTrack','AudioTrack')
                         for primary in clip.findall(track+'/PrimarySource'))
            if clip.get('uniqueId')=='1788780038810' and nonempty:
                scratch.append({'deck':deck.get('deckIndex'),'layer_index':clip.get('layerIndex'),'clip_id':clip.get('uniqueId')})
    assert not scratch,'Scratch identity still in saved XML: '+json.dumps(scratch)
    hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    assert before=={p:(p.stat().st_size,p.stat().st_mtime_ns) for p in paths},'Pair changed while checking'
    return {'result':'PASS — offline pair integrity/dependency check only','sha256':hashes,'hold':data['hold'],'bars':data['bars'],'active_layers':data['layers'],'live_signature_compared':live is not None}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('avc',type=Path);p.add_argument('--sources',required=True,type=Path);p.add_argument('--effects',required=True,type=Path)
    p.add_argument('--live',type=Path,help='Fresh saved GET composition response, not Heart status')
    p.add_argument('--after',type=float,help='Epoch seconds recorded before Save setup')
    a=p.parse_args()
    try:
        print(json.dumps(verify(a.avc,json.loads(a.sources.read_text()),json.loads(a.effects.read_text()),json.loads(a.live.read_text()) if a.live else None,a.after),indent=2))
    except Exception as e:
        print('FAIL: '+str(e),file=sys.stderr);sys.exit(1)
