import unittest
from types import SimpleNamespace as N
from unittest.mock import patch
import heart
class NativeGlobalChoiceTests(unittest.TestCase):
 def test_numeric_labels_are_not_sent_as_option_indexes(self):
  c=N(gids={'Spread':12,'Seed':13},sp={'Spread':{'valuetype':'ParamChoice','options':[str(n) for n in range(1,9)]},'Seed':{'valuetype':'ParamChoice','options':[str(n) for n in range(32)]}})
  with patch.object(heart,'cur_val',return_value='1'),patch.object(heart,'put_http') as put:
   heart.wglob(c,'Spread',8,{})
   put.assert_called_with(12,'8')
   heart.wglob(c,'Seed',5,{})
   put.assert_called_with(13,'5')
 def test_continuous_values_keep_numeric_payload(self):
  c=N(gids={'Depth':14},sp={'Depth':{'valuetype':'ParamRange'}})
  with patch.object(heart,'cur_val',return_value=.5),patch.object(heart,'put_http') as put:
   heart.wglob(c,'Depth',1.,{});put.assert_called_with(14,1.)
