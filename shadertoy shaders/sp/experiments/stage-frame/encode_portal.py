import json,pathlib,subprocess,time,concurrent.futures
import imageio_ffmpeg
root=pathlib.Path(__file__).resolve().parent
j=json.loads((root/'Heart Portal Frame/Heart Portal Frame.wire').read_text())['patch']; banks={}
for n in j['nodes'].values():
 if ' image ' in n['name'] and n['class']['id'].lower()=='77697265-3683-409b-8c89-43afaea9a2b0':
  name,num=n['name'].rsplit(' image ',1);banks.setdefault(name,[]).append((int(num),n['attributes']['image']['value']['path']['main']))
out=root/'portal-stream-banks';out.mkdir(exist_ok=True)
def encode(item):
 name,entries=item;entries.sort();target=out/(name+'.mov');t=time.monotonic()
 p=subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-loglevel','error','-f','image2pipe','-framerate','1','-c:v','png','-i','pipe:0','-an','-c:v','qtrle','-pix_fmt','argb','-g','1','-threads','2','-y',str(target)],stdin=subprocess.PIPE)
 for _,path in entries:p.stdin.write(pathlib.Path(path).read_bytes())
 p.stdin.close();assert p.wait()==0,name
 d={'name':name,'path':str(target),'frames':len(entries),'bytes':target.stat().st_size,'seconds':round(time.monotonic()-t,2),'source_paths':[p for _,p in entries]};print(name,d['frames'],d['seconds'],flush=True);return d
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool: result=list(pool.map(encode,banks.items()))
(out/'manifest.json').write_text(json.dumps(result,indent=2));print('DONE',sum(d['frames'] for d in result),flush=True)
