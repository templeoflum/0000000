"""Build only a new local Wire artifact; never install or contact Resolume."""
from pathlib import Path
from copy import deepcopy
from collections import Counter, defaultdict, deque
import hashlib
import json
import uuid

ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = Path(__file__).resolve().parent
VARIANTS = [
    {'source_name':'SP Delay Chain', 'name':'Heart Delay Line',
     'source_hash':'6d0780c8315e70b62442be812a6a2b429ca497a088c1c7dd819256da6a6de995',
     'identifier':'f19e6915-d501-4224-be36-a1706741a320'},
    {'source_name':'SP Delay Performance', 'name':'Heart Delay Performance',
     'source_hash':'b1913bd6e26918e94c8fff3b4dd7cc93eecf58a59903d8da1ce78df41c1f393d',
     'identifier':'ffc8dfb6-e73c-4523-a5f1-475bd1d1b7d4'},
]
REMOVED = set(range(712, 741))
BYPASS_EDGE = {'from': [386, 'output'], 'to': [2, 'input']}

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()

def ancestors(graph, target):
    incoming = defaultdict(list)
    for edge in graph['connections']:
        incoming[edge['to'][0]].append(edge['from'][0])
    found = set(); pending = [target]
    while pending:
        node = pending.pop()
        if node in found: continue
        found.add(node); pending.extend(incoming[node])
    return found

def verify(before, after):
    old, new = before['patch'], after['patch']
    assert uuid.UUID(new['meta']['identifier']).version == 4
    assert new['meta']['identifier'] != old['meta']['identifier']
    assert set(old['nodes']) - set(new['nodes']) == {str(n) for n in REMOVED}
    assert all(new['nodes'][k] == v for k, v in old['nodes'].items() if int(k) not in REMOVED)
    kept_edges = [e for e in old['connections'] if e['from'][0] not in REMOVED and e['to'][0] not in REMOVED]
    assert new['connections'] == kept_edges + [BYPASS_EDGE]
    assert old['nodes']['386']['name'] == 'Video Mixer'
    assert old['nodes']['2']['constants']['input']['type'] == 'texture2d'
    assert {'from':[386,'output'],'to':[712,'input0']} in old['connections']
    assert old['nodes']['712']['constants']['input0']['type'] == 'texture2d'
    assert {'from':[740,'output'],'to':[2,'input']} in old['connections']
    expected_order = deepcopy(old['inputOrder'])
    expected_order['roots'] = [r for r in expected_order['roots'] if r['node'] not in REMOVED]
    assert new['inputOrder'] == expected_order
    # Exhaustive allowlist: all unrelated fields must compare exactly as parsed JSON.
    restored = deepcopy(after)
    restored['patch']['nodes'] = old['nodes']
    restored['patch']['connections'] = old['connections']
    restored['patch']['inputOrder'] = old['inputOrder']
    for field in ('displayName', 'identifier', 'description'):
        restored['patch']['meta'][field] = old['meta'][field]
    assert restored == before
    ids = {int(k) for k in new['nodes']}
    assert all(e[end][0] in ids for e in new['connections'] for end in ('from','to'))
    assert all(r['node'] in ids for r in new['inputOrder']['roots'])
    assert all(int(k) in ids for k in new['ui']['selection'])
    assert not new['inputOrder']['groups']  # No hidden grouped input references.
    assert new['nextNodeId'] > max(ids)
    old_multi={k:v for k,v in Counter(tuple(e['to']) for e in kept_edges).items() if v>1}
    new_multi={k:v for k,v in Counter(tuple(e['to']) for e in new['connections']).items() if v>1}
    assert old_multi==new_multi
    assert sum(e['to']==[2,'input'] for e in new['connections'])==1
    output_ancestors = ancestors(new, 2)
    assert output_ancestors == ancestors(old, 2) - REMOVED
    delay_ids = {int(k) for k,n in new['nodes'].items() if n['name']=='Delay'}
    assert len(delay_ids) == 480 and delay_ids <= output_ancestors and 0 in output_ancestors
    outgoing=defaultdict(list); indegree={k:0 for k in ids}; depth={k:0 for k in ids}
    for e in new['connections']:
        outgoing[e['from'][0]].append(e['to'][0]); indegree[e['to'][0]]+=1
    pending=deque(k for k,d in indegree.items() if d==0); visited=0
    while pending:
        k=pending.popleft();visited+=1
        for nxt in outgoing[k]:
            depth[nxt]=max(depth[nxt],depth[k]+int(nxt in delay_ids));indegree[nxt]-=1
            if indegree[nxt]==0:pending.append(nxt)
    assert visited==len(ids) and depth[2]==480
    controls=[new['nodes'][str(r['node'])]['name'] for r in new['inputOrder']['roots']]
    assert controls==['Texture In','Taps','Span','⚡ Shuffle','⌂ Home','Glide','φ']
    return {'nodes_before':len(old['nodes']), 'nodes_after':len(ids), 'removed_nodes':sorted(REMOVED),
            'delay_nodes':len(delay_ids), 'maximum_delay_stages_to_output':depth[2], 'acyclic':True,
            'dangling_references':0, 'new_multiple_input_conflicts':0,
            'preserved_multi_input_destinations':[{'destination':list(k),'connections':v} for k,v in new_multi.items()],
            'all_remaining_nodes_exactly_equal':True, 'all_unrelated_fields_exactly_equal':True,
            'output_ancestors_preserved_except_removed_nodes':True, 'controls':controls,
            'remaining_nodes_semantic_sha256':digest(canonical(new['nodes'])),
            'preserved_connections_semantic_sha256':digest(canonical(kept_edges)),
            'added_edge':BYPASS_EDGE}

def build(variant):
    source=Path('/Users/donovan/Documents/Resolume Wire/Patches')/variant['source_name']/(variant['source_name']+'.wire')
    output=ROOT/'sp/patches'/variant['name']/(variant['name']+'.wire')
    raw=source.read_bytes()
    assert digest(raw)==variant['source_hash'], 'Installed source changed; review before rebuilding'
    before=json.loads(raw);after=deepcopy(before);g=after['patch']
    assert all(str(n) in g['nodes'] for n in REMOVED)
    g['nodes']={k:n for k,n in g['nodes'].items() if int(k) not in REMOVED}
    g['connections']=[e for e in g['connections'] if e['from'][0] not in REMOVED and e['to'][0] not in REMOVED]+[BYPASS_EDGE]
    g['inputOrder']['roots']=[r for r in g['inputOrder']['roots'] if r['node'] not in REMOVED]
    g['meta']['displayName']=variant['name'];g['meta']['identifier']=variant['identifier']
    if variant['source_name']=='SP Delay Chain':
        g['meta']['description']=g['meta']['description'].split(' + RGB:',1)[0]
    else:
        g['meta']['description']='Heart Delay Line with half-width/half-height history textures. Same tap timing and span. Softer echoes; current frame and final mix retain full resolution. Internal RGB offset stage removed.'
    result=verify(before,after)
    if variant['source_name']=='SP Delay Performance':
        assert g['nodes']['742']==before['patch']['nodes']['742']
        assert g['nodes']['742']['attributes']['resolution-relative']['value']==[.5,.5]
        assert {'from':[0,'output'],'to':[742,'input0']} in g['connections']
        assert {'from':[742,'output0'],'to':[1,'input0']} in g['connections']
        result['half_resolution_history_preserved']=True
    out=(json.dumps(after,indent=1,ensure_ascii=False)+'\n').encode()
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_bytes(out)
    verify(before,json.loads(output.read_bytes()))
    backup=EVIDENCE/(variant['source_name']+'.original.wire');backup.write_bytes(raw)
    assert source.read_bytes()==raw, 'Source changed during build'
    result.update(source=str(source),output=str(output),source_sha256=digest(raw),
                  original_backup_sha256=digest(backup.read_bytes()),
                  output_sha256=digest(out),original_identifier=before['patch']['meta']['identifier'],
                  new_identifier=variant['identifier'],rendered=False,installed=False)
    return result

def main():
    results=[build(v) for v in VARIANTS]
    assert len({r['new_identifier'] for r in results})==2
    assert not {r['new_identifier'] for r in results}&{r['original_identifier'] for r in results}
    (EVIDENCE/'verification.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps(results,indent=2))

if __name__=='__main__':main()
