"""Immediate native-claim stand-in for pure envelope unit tests."""
from concurrent.futures import Future
class ClaimedExecutor:
 def submit(self,fn,*args,**kwargs):
  result=Future();result.set_result(True if fn.__module__=='effect_claim' else fn(*args,**kwargs));return result
