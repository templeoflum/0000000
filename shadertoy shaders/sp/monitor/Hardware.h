#import <CoreMIDI/CoreMIDI.h>
#import <GameController/GameController.h>
@interface HeartHardware : NSObject
@property MIDIClientRef midi;
@property MIDIPortRef port;
@property NSMutableDictionary<NSNumber*,NSString*> *sources;
@property NSMutableArray *events;
@property NSUInteger sequence;
@property NSMutableDictionary *latest;
- (NSDictionary*)snapshot;
@end
@implementation HeartHardware
- (instancetype)init {if((self=[super init])){
 self.sources=[NSMutableDictionary new];self.events=[NSMutableArray new];self.latest=[NSMutableDictionary new];
 MIDIClientCreate(CFSTR("Heart inputs"),NULL,NULL,&_midi);
 __weak HeartHardware *weak=self;
 MIDIInputPortCreateWithBlock(_midi,CFSTR("Heart MIDI"),&_port,^(const MIDIPacketList *list,void *ref){
  const MIDIPacket *p=&list->packet[0];
  for(UInt32 i=0;i<list->numPackets;i++){
   NSData *data=[NSData dataWithBytes:p->data length:p->length];NSNumber *source=@((uintptr_t)ref);
   dispatch_async(dispatch_get_main_queue(),^{HeartHardware *s=weak;if(!s)return;
    NSMutableArray *bytes=[NSMutableArray new];const UInt8 *b=data.bytes;for(NSUInteger j=0;j<MIN(data.length,48);j++)[bytes addObject:@(b[j])];
    [s.events addObject:@{@"seq":@(++s.sequence),@"device":s.sources[source]?:@"MIDI",@"kind":@"midi",@"bytes":bytes}];s.latest[s.events.lastObject[@"device"]]=s.events.lastObject;while(s.events.count>16)[s.events removeObjectAtIndex:0];
   });p=MIDIPacketNext(p);
  }
 });
 }return self;}
- (NSDictionary*)snapshot {
 NSMutableSet *present=[NSMutableSet new];
 for(ItemCount i=0;i<MIDIGetNumberOfSources();i++){
  MIDIEndpointRef e=MIDIGetSource(i);NSNumber *key=@(e);[present addObject:key];
  if(!self.sources[key]){CFStringRef n=NULL;MIDIObjectGetStringProperty(e,kMIDIPropertyDisplayName,&n);self.sources[key]=n?CFBridgingRelease(n):@"MIDI";MIDIPortConnectSource(self.port,e,(void*)(uintptr_t)e);}
 }
 for(NSNumber *key in self.sources.allKeys)if(![present containsObject:key]){MIDIPortDisconnectSource(self.port,key.unsignedIntValue);[self.sources removeObjectForKey:key];}
 NSMutableArray *pads=[NSMutableArray new];
 for(GCController *c in GCController.controllers){
  [pads addObject:c.vendorName?:@"Game controller"];
  if(c.extendedGamepad && !c.extendedGamepad.valueChangedHandler){
   __weak HeartHardware *weak=self;NSString *name=c.vendorName?:@"Game controller";
   c.extendedGamepad.valueChangedHandler=^(GCExtendedGamepad *pad,GCControllerElement *element){
    if(![element isKindOfClass:GCControllerButtonInput.class])return;
    NSString *label=element.localizedName?:@"Control";float value=[element isKindOfClass:GCControllerButtonInput.class]?((GCControllerButtonInput*)element).value:0;
    dispatch_async(dispatch_get_main_queue(),^{HeartHardware *s=weak;if(!s)return;[s.events addObject:@{@"seq":@(++s.sequence),@"device":name,@"kind":@"gamepad",@"control":label,@"value":@(value)}];s.latest[s.events.lastObject[@"device"]]=s.events.lastObject;while(s.events.count>16)[s.events removeObjectAtIndex:0];});
   };
  }
 }
 return @{@"midi":self.sources.allValues,@"gamepads":pads,@"latest":[self.latest copy],@"events":[self.events copy],@"timestamp":@(NSDate.date.timeIntervalSince1970)};
}
- (void)dealloc {if(_port)MIDIPortDispose(_port);if(_midi)MIDIClientDispose(_midi);}
@end
