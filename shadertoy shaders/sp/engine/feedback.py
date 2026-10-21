"""Bounded starting behaviors for the separately installed Heart feedback instrument."""
import copy
ATOM={'_global':{'pattern':0,'seed':0,'spread':1,'depth':1.,'fm':0.}}
NAMES=['Zoom','Rotate','Drift X','Drift Y','Center X','Center Y','Gain','Floor','Key','Loop Hue','Loop Invert','Loop Fold','Loop Detail','Red Decay','Green Decay','Blue Decay']
for name in NAMES:ATOM[name]={'cyclic':False,'drive':False,'ratio':'1:1','mult':1,'offset':0,'shape':1,'lo':0,'hi':1,'lock':False}
STATIC=dict(zip(NAMES,[.5,.5,.5,.5,.5,.5,.9,.015,0.,.5,0.,0.,.5,1.,1.,1.]))
def profile(bindings,static=None):
 return {'speed':.25,'static':dict(STATIC,**(static or {})), 'bindings':{k:{'center':(lo+hi)/2,'range':[lo,hi]} for k,(lo,hi) in bindings.items()}}
BEHAVIORS={
 'Turn':profile({'Zoom':(.505,.525),'Rotate':(.502,.509),'Loop Hue':(.499,.501)}),
 'Drift':profile({'Zoom':(.501,.512),'Drift X':(.47,.53),'Drift Y':(.48,.52),'Loop Hue':(.499,.501)}),
 'Breathe':profile({'Zoom':(.47,.535),'Rotate':(.498,.502),'Center X':(.46,.54),'Center Y':(.47,.53)}),
 'Fold':profile({'Zoom':(.505,.52),'Rotate':(.498,.503),'Loop Fold':(.2,.7),'Loop Hue':(.499,.501)}, {'Loop Detail':.57})}
# Bound controls override the neutral static settings.
for item in BEHAVIORS.values():
 for name in item['bindings']:item['static'].pop(name,None)
def get(name):
 if name not in BEHAVIORS:raise ValueError('Unknown feedback behavior')
 return copy.deepcopy(BEHAVIORS[name])
