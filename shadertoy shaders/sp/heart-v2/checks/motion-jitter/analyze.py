import json,struct,collections,statistics
from pathlib import Path
D=Path(__file__).parent;x=json.loads((D/'delivery-trace.json').read_text());e=json.loads((D/'engine-trace.json').read_text());series=collections.defaultdict(list)
for t,frame,sampled,raw in x['packets']:
 b=bytes.fromhex(raw);pos=16
 while pos<len(b):
  n=struct.unpack('>i',b[pos:pos+4])[0];p=b[pos+4:pos+4+n];pos+=4+n
  address=p.split(b'\0',1)[0].decode();value=struct.unpack('>f',p[-4:])[0];series[address].append((t,sampled,frame,value))
start=min(v[0][0] for v in series.values());end=max(v[-1][0] for v in series.values());cutoff=start+8
percentile=lambda a,p:sorted(a)[int((len(a)-1)*p)] if a else None
summary=[];gaps=[]
for address,vs in series.items():
 vs=[v for v in vs if v[0]>=cutoff]
 if len(vs)<10:continue
 dts=[1000*(b[0]-a[0]) for a,b in zip(vs,vs[1:])];ages=[1000*(v[0]-v[1]) for v in vs]
 for a,b in zip(vs,vs[1:]):
  if b[0]-a[0]>.025:gaps.append(dict(at=b[0]-start,gap_ms=(b[0]-a[0])*1000,phase_step=b[3]-a[3],address=address,sampled_ms=(b[1]-a[1])*1000,age_ms=(b[0]-b[1])*1000))
 summary.append(dict(address=address,count=len(vs),gap_p95=percentile(dts,.95),gap_max=max(dts),age_p95=percentile(ages,.95),age_max=max(ages),bursts=sum(dt<2 for dt in dts)))
latencies=[(b-a)*1000 for a,b,path,values in x['reads'] if a>=cutoff]
events=[dict(start=a-start,ms=b*1000,name=name) for a,b,name in e['events'] if a>=cutoff]
engine_gaps=[v for s in e['samples'] for v in s['gaps']];works=[v for s in e['samples'] for v in s['work']]
result=dict(duration=end-start,addresses=len(series),packets=len(x['packets']),read_count=len(x['reads']),read_ms=dict(p50=percentile(latencies,.5),p95=percentile(latencies,.95),max=max(latencies)),owned=sorted(set(s['owned'] for s in e['samples'])),engine_gap_max=max(engine_gaps),engine_work_max=max(works),waiting=max(m['delivery']['waiting'] for m in x['reports'] if 'delivery' in m),worst_routes=sorted(summary,key=lambda r:-r['gap_max'])[:8],worst_gaps=sorted(gaps,key=lambda r:-r['gap_ms'])[:12],worst_events=sorted(events,key=lambda r:-r['ms'])[:12])
(D/'analysis.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
