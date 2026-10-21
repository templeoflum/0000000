import json,struct,socket,time,urllib.request,re
from pathlib import Path
OUT=Path(__file__).parent

def read(path):
 with urllib.request.urlopen('http://127.0.0.1:8080/api/v1'+path,timeout=2) as r:return json.load(r)
def text(s):
 b=s.encode()+b'\0';return b+b'\0'*((-len(b))%4)
sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
def send(address,v):sock.sendto(text(address)+text(',f')+struct.pack('>f',v),('127.0.0.1',7000))
results=[]
for cid,col in [(1789742611659,13),(1789742611667,14)]:
 clip=read('/composition/layers/22/clips/'+str(col));assert clip['id']==cid
 p=clip['video']['sourceparams']['Quat W'];program=read(f"/parameter/by-id/{p['id']}/phase-source");assert program['phase_source']=='timeline' and program['parameters']['PlayDirection']['value']=='||'
 phase=(p['value']-p['in'])/(p['out']-p['in']);test=phase+.015 if phase<.95 else phase-.015
 name=clip['video']['description'];slug=re.sub(r'\s','',name.lower());address=f'/composition/layers/22/clips/{col}/video/source/{slug}/quatw/phase'
 send(address,test);time.sleep(.15);after=read(f"/parameter/by-id/{p['id']}");worked=abs(after['value']-(p['in']+test*(p['out']-p['in'])))<.00001
 if worked:send(address,phase);time.sleep(.1)
 result=dict(name=name,address=address,before=p['value'],after=after['value'],works=worked,restored=read(f"/parameter/by-id/{p['id']}")['value']);results.append(result);print(result)
(OUT/'source-address-probe.json').write_text(json.dumps(results,indent=2))
