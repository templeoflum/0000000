#import <GameController/GameController.h>
#import <dlfcn.h>

typedef struct { float x,y; } HeartPoint;
typedef struct { HeartPoint pos,vel; } HeartReadout;
typedef struct {
 int frame; double timestamp; int identifier,state,foo3,foo4;
 HeartReadout normalized; float size,zero1,angle,majorAxis,minorAxis;
 HeartReadout mm; int zero2[2]; float zdensity;
} HeartFinger;
typedef int (*HeartContactCallback)(void *,HeartFinger *,int,double,int);
static NSMutableArray *HeartContactFrames;
static int HeartContactFrame(void *device,HeartFinger *data,int count,double stamp,int frame) {
 @autoreleasepool {
  NSMutableArray *fingers=[NSMutableArray array];
  for(int i=0;i<count;i++) {
   HeartFinger f=data[i];
   if(f.state!=3 && f.state!=4)continue;
   [fingers addObject:@{@"id":[NSString stringWithFormat:@"%p:%d",device,f.identifier],@"x":@(f.normalized.pos.x),@"y":@(f.normalized.pos.y),@"size":@(f.size)}];
  }
  @synchronized(HeartContactFrames) {
   [HeartContactFrames addObject:@{@"device":[NSString stringWithFormat:@"%p",device],@"frame":@(frame),@"fingers":fingers}];
   // A stalled web process releases capture rather than replaying a backlog.
   if(HeartContactFrames.count>128){[HeartContactFrames removeAllObjects];[HeartContactFrames addObject:@{@"overflow":@YES}];}
  }
 }
 return 0;
}

@interface HeartInputs : NSObject
@property NSUInteger touchDevices;
@property CFArrayRef devices;
@property void *framework;
- (NSDictionary *)snapshot;
@end
@implementation HeartInputs
- (instancetype)init {
 if((self=[super init])) {
  HeartContactFrames=[NSMutableArray array];
  self.framework=dlopen("/System/Library/PrivateFrameworks/MultitouchSupport.framework/MultitouchSupport",RTLD_LAZY);
  if(self.framework) {
   CFArrayRef (*create)(void)=dlsym(self.framework,"MTDeviceCreateList");
   void (*registerFrame)(void *,HeartContactCallback)=dlsym(self.framework,"MTRegisterContactFrameCallback");
   void (*start)(void *,int)=dlsym(self.framework,"MTDeviceStart");
   if(create&&registerFrame&&start) {
    self.devices=create();self.touchDevices=self.devices?CFArrayGetCount(self.devices):0;
    for(CFIndex i=0;i<self.touchDevices;i++){void *device=(void *)CFArrayGetValueAtIndex(self.devices,i);registerFrame(device,HeartContactFrame);start(device,0);}
   }
  }
 }
 return self;
}
- (NSDictionary *)snapshot {
 NSMutableArray *frames;
 @synchronized(HeartContactFrames){frames=[HeartContactFrames mutableCopy];[HeartContactFrames removeAllObjects];}
 NSMutableArray *pads=[NSMutableArray array];NSMutableDictionary *counts=[NSMutableDictionary dictionary];
 for(GCController *c in GCController.controllers) {
  NSString *key=[NSString stringWithFormat:@"gc:%@:%@",c.vendorName?:@"Controller",c.productCategory?:@"Gamepad"];
  counts[key]=@([counts[key] integerValue]+1);
 }
 for(GCController *c in GCController.controllers) {
  GCExtendedGamepad *p=c.extendedGamepad;if(!p)continue;
  NSString *key=[NSString stringWithFormat:@"gc:%@:%@",c.vendorName?:@"Controller",c.productCategory?:@"Gamepad"];
  NSMutableDictionary *buttons=[@{@"cross":@(p.buttonA.value),@"circle":@(p.buttonB.value),@"square":@(p.buttonX.value),@"triangle":@(p.buttonY.value),@"l1":@(p.leftShoulder.value),@"r1":@(p.rightShoulder.value),@"l2":@(p.leftTrigger.value),@"r2":@(p.rightTrigger.value),@"up":@(p.dpad.up.value),@"down":@(p.dpad.down.value),@"left":@(p.dpad.left.value),@"right":@(p.dpad.right.value),@"options":@(p.buttonMenu.value)} mutableCopy];
  if(p.buttonOptions)buttons[@"share"]=@(p.buttonOptions.value);
  if(p.leftThumbstickButton)buttons[@"l3"]=@(p.leftThumbstickButton.value);
  if(p.rightThumbstickButton)buttons[@"r3"]=@(p.rightThumbstickButton.value);
  [pads addObject:@{@"id":key,@"name":c.vendorName?:@"Controller",@"ambiguous":@([counts[key] integerValue]>1),@"buttons":buttons,@"axes":@{@"lx":@(p.leftThumbstick.xAxis.value),@"ly":@(-p.leftThumbstick.yAxis.value),@"rx":@(p.rightThumbstick.xAxis.value),@"ry":@(-p.rightThumbstick.yAxis.value)}}];
 }
 return @{@"type":@"frame",@"touchDevices":@(self.touchDevices),@"touch":frames,@"gamepads":pads};
}
@end
