import asyncio
import json
import struct
import time
import unittest
from phase_frames import PhaseFrames, split_bundles
from bridge import phase_bundle


def packet_values(packet):
    result=[];offset=16
    while offset<len(packet):
        size=struct.unpack('>i',packet[offset:offset+4])[0]
        result.append(struct.unpack('>f',packet[offset+size:offset+size+4])[0]);offset+=size+4
    return result


class PhaseFrameTests(unittest.IsolatedAsyncioTestCase):
    async def test_reordered_members_keep_the_same_validation_lease(self):
        reads=[];packets=[]
        native=dict(id=100,params={str(pid):dict(id=pid,min=0,max=1) for pid in (1,2)})
        async def read(path):reads.append(path);return native
        frames=PhaseFrames(read,phase_bundle,packets.append,lambda r:True,lambda rows,error:self.fail(error),lambda **m:None)
        frames.refresh_seconds=1;frames.lease_seconds=1
        rows=[(pid,{'phase':.4},dict(read='/effect',address=f'/p/{pid}/phase',identity={'id':100},path=['params',str(pid)],min=0,max=1),0,0) for pid in (1,2)]
        task=asyncio.create_task(frames.run())
        try:
            frames.submit(1,time.perf_counter(),rows);await asyncio.sleep(.02)
            self.assertEqual(len(reads),1);self.assertEqual(len(packets),1)
            frames.submit(2,time.perf_counter(),list(reversed(rows)));await asyncio.sleep(.02)
            self.assertEqual(len(reads),1);self.assertEqual(len(packets),2)
            self.assertEqual(len(packet_values(packets[-1])),2)
        finally:task.cancel();await asyncio.gather(task,return_exceptions=True)

    async def test_slow_validation_does_not_block_other_scope_or_mix_frame_values(self):
        emitted=[];failures=[];slow=asyncio.Event();versions={1:0,2:0};reads=[]
        async def read(path):
            reads.append(path)
            if path=='/slow':await slow.wait()
            return dict(id=1 if path=='/fast' else 2,min=0,max=1)
        valid=lambda r:versions.get(r[0])==r[3]
        frames=PhaseFrames(read,phase_bundle,lambda p:emitted.append(p),valid,lambda rows,error:failures.append(error),lambda **m:None)
        def row(pid,value):return (pid,{'phase':value},dict(read='/fast' if pid==1 else '/slow',address=f'/scope/{pid}/phase',identity={'id':pid},path=[],min=0,max=1),versions[pid],0)
        task=asyncio.create_task(frames.run())
        try:
            for n in range(1,7):
                frames.submit(n,time.perf_counter(),[row(1,n/10),row(2,n/10)])
                await asyncio.sleep(.012)
            self.assertTrue(emitted);self.assertTrue(all(len(packet_values(p))==1 for p in emitted))
            slow.set();emitted.clear()
            for n in range(7,10):
                frames.submit(n,time.perf_counter(),[row(1,n/10),row(2,n/10)])
                await asyncio.sleep(.025)
            together=[packet_values(p) for p in emitted if len(packet_values(p))==2]
            self.assertTrue(together);self.assertTrue(all(abs(a-b)<1e-7 for a,b in together))
            self.assertEqual(failures,[])
            # Delivery rate is independent of the much slower validation rate.
            self.assertLess(len(reads),15)
            emitted.clear();versions[1]=1;versions[2]=1
            await asyncio.sleep(.03);self.assertEqual(emitted,[])
        finally:task.cancel();await asyncio.gather(task,return_exceptions=True)

    async def test_expired_identity_and_stale_frame_fail_closed(self):
        packets=[];blocked=[];valid=True
        async def read(path):
            if not valid:await asyncio.sleep(.2)
            return dict(id=1,min=0,max=1)
        frames=PhaseFrames(read,phase_bundle,packets.append,lambda r:True,lambda rows,error:blocked.append(error),lambda **m:None)
        frames.lease_seconds=.04;frames.refresh_seconds=.02
        route=dict(read='/p',address='/p/phase',identity={'id':1},path=[],min=0,max=1)
        rows=[(1,{'phase':.4},route,0,0)];task=asyncio.create_task(frames.run())
        try:
            frames.submit(1,time.perf_counter(),rows);await asyncio.sleep(.025);self.assertTrue(packets)
            valid=False;await asyncio.sleep(.06);packets.clear()
            frames.submit(2,time.perf_counter(),rows);await asyncio.sleep(.025);self.assertEqual(packets,[])
            frames.submit(3,time.perf_counter()-1,rows);await asyncio.sleep(.03);self.assertEqual(packets,[])
        finally:task.cancel();await asyncio.gather(task,return_exceptions=True)

    def test_udp_partition_keeps_sample_order_and_packet_bound(self):
        native=dict(id=1,min=0,max=1)
        parts=[phase_bundle(native,[(1,{'phase':i/100},dict(address='/long/'+('name'*30)+'/phase',read='/p',identity={'id':1},path=[],min=0,max=1))]) for i in range(50)]
        packets=list(split_bundles(parts));self.assertGreater(len(packets),1);self.assertTrue(all(len(p)<=1200 for p in packets))
        values=[v for p in packets for v in packet_values(p)]
        self.assertEqual(len(values),50)
        for i,v in enumerate(values):self.assertAlmostEqual(v,i/100,places=6)


if __name__=='__main__':unittest.main()
