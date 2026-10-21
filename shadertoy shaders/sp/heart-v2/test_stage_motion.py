import copy,unittest
from unittest.mock import patch
from server import Engine

def engine():
 e=Engine();e.rack_config={'epoch':'stage-test','stage_motion':{'groups':[{'group_id':100,'sections':[{'id':'rings','label':'Rings','members':[20,21]},{'id':'background','label':'Background','members':[22]},{'id':'effects','label':'Shared effects','scope':'group'}]}]}}
 groups=[dict(id=100,name='__stage__ Different layout',stage=True,members=[20,21,22]),dict(id=101,name='__stage__ Other stage',stage=True,members=[30])]
 layers=[dict(id=lid,i=i+1,name='Layer '+str(lid),group_id=100 if lid in (20,21,22) else 101 if lid==30 else None,stage=100 if lid in (20,21,22) else 101 if lid==30 else None,active=0,clips=[]) for i,lid in enumerate((20,21,22,30,40))]
 targets=[]
 for pid,lid,kind,prepared in [(1,20,'layer',True),(2,21,'layer',True),(3,22,'layer',True),(4,None,'effect',True),(5,30,'layer',True),(6,40,'source',True),(7,20,'effect',False),(8,20,'effect',True),(9,21,'effect',True)]:
  group=100 if lid in (None,20,21,22) else 101 if lid==30 else None
  p=dict(id=pid,name='Level',type='ParamRange',min=0,max=1,value=.4,**{'in':.2,'out':.7})
  if prepared:p['native_phase']={'address':'/example/'+str(pid)+'/phase'}
  targets.append(dict(id='target:'+str(pid),label='Target '+str(pid),kind=kind,scope='stage' if lid is None else 'layer',layer_id=lid,group_id=group,stage=group,params=[p]))
 e.reconcile(dict(type='catalog',epoch='stage-test',native_phase_mode=True,layers=layers,groups=groups,targets=targets));e.armed=e.connected=True
 for pid in (1,2,3,4,5,6,9):e.drive(pid,True)
 e.parameter_lock(dict(epoch='stage-test',id=9,on=True));e.parameter_motion(1,dict(mult=.025,seconds=0));e.settings('target:1',dict(rate=.5,amount=.3))
 return e

class StageMotionTests(unittest.TestCase):
 def shuffle(self,e,section=None,group=100):
  with patch('server.random.random',return_value=.731):e.stage_shuffle(dict(epoch='stage-test',group_id=group,section=section))
 def test_section_shuffle_only_prepared_active_unlocked_members(self):
  e=engine();before={pid:copy.deepcopy(sl.cfg) for pid,sl in e.slots.items()};groups=copy.deepcopy(e.groups);catalog=copy.deepcopy(e.catalog);owned=e.owned.copy()
  self.shuffle(e,'rings')
  for pid,sl in e.slots.items():
   if pid in (1,2):
    self.assertEqual(sl.cfg['offset'],.731)
    for key in ('lo','hi','manual','mult','shape','lock'):self.assertEqual(sl.cfg[key],before[pid][key])
   else:self.assertEqual(sl.cfg,before[pid])
  self.assertEqual(e.groups,groups);self.assertEqual(e.catalog,catalog);self.assertEqual(e.owned,owned)
 def test_whole_stage_includes_its_shared_effects_and_excludes_other_stages(self):
  e=engine();self.shuffle(e)
  for pid in (1,2,3,4):self.assertEqual(e.slots[pid].cfg['offset'],.731)
  for pid in (5,6,7,8,9):self.assertNotEqual(e.slots[pid].cfg['offset'],.731)
 def test_summary_without_native_observation_and_paused_drive_off_counts(self):
  e=engine();e.selected='target:6';e.watched=set();s=e.state();rows={r['section']:r for r in s['stage_motion'] if r['group_id']==100}
  self.assertEqual((rows['rings']['prepared'],rows['rings']['driven'],rows['rings']['shuffleable']),(4,3,2))
  self.assertNotIn(1,s['values']);self.assertIn('stage_shuffle',s['capabilities']);e.drive(1,False)
  self.assertEqual(next(r for r in e.stage_motion_state() if r['section']=='rings')['shuffleable'],1)
 def test_changed_members_stale_epoch_unknown_section_and_disarmed_reject(self):
  for change in ('member','epoch','section','group','disarmed'):
   e=engine();data=dict(epoch='stage-test',group_id=100,section='rings');before={pid:copy.deepcopy(sl.cfg) for pid,sl in e.slots.items()}
   if change=='member':e.catalog['groups'][0]['members'].remove(21)
   elif change=='epoch':data['epoch']='old'
   elif change=='section':data['section']='missing'
   elif change=='group':data['group_id']=999
   else:e.armed=False
   with self.assertRaises(ValueError):e.stage_shuffle(data)
   self.assertEqual(before,{pid:sl.cfg for pid,sl in e.slots.items()})
 def test_unconfigured_stage_uses_current_members_and_native_group_only_section(self):
  e=engine();rows=[r for r in e.stage_motion_state() if r['group_id']==101];self.assertEqual([r['section'] for r in rows],[None,'layer:30'])
  self.shuffle(e,'effects');self.assertEqual(e.slots[4].cfg['offset'],.731);self.assertEqual(e.slots[1].cfg['offset'],0)

if __name__=='__main__':unittest.main()
