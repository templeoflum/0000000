import json, unittest
from status_stream import StatusStream
class StreamTests(unittest.TestCase):
 def test_roundtrip_changes_reordering_and_new_rows(self):
  stream=StatusStream();decoded={}
  for state in [{'layers':[{'i':1,'v':0},{'i':2,'v':0}],'hold':False},{'layers':[{'i':1,'v':.5},{'i':2,'v':0}],'hold':False},{'layers':[{'i':2,'v':0},{'i':1,'v':.5}],'hold':True},{'layers':[],'hold':True}]:
   msg=json.loads(stream.encode(state));decoded.update(msg['set'])
   for k,rows in msg['rows'].items():
    for i,row in rows.items():decoded[k][int(i)]=row
   self.assertEqual(decoded,state)
 def test_unchanged_catalog_is_not_resent(self):
  s=StatusStream();state={'layers':[{'name':'x','clips':['a']*500}]};s.encode(state)
  msg=json.loads(s.encode(state));self.assertEqual(msg['set'],{});self.assertEqual(msg['rows'],{})
