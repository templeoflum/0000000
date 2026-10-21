#import <Cocoa/Cocoa.h>
#import <WebKit/WebKit.h>
#import <CoreMIDI/CoreMIDI.h>
#import "Inputs.h"

@interface HeartMidiSource : NSObject
@property MIDIEndpointRef endpoint;
@property NSString *identifier;
@property NSString *name;
@property UInt8 status;
@property NSMutableArray<NSNumber *> *pending;
@end
@implementation HeartMidiSource
@end

@interface HeartWindow : NSObject <NSApplicationDelegate, NSWindowDelegate, WKScriptMessageHandler, WKNavigationDelegate>
@property NSWindow *window;
@property WKWebView *web;
@property MIDIClientRef midiClient;
@property MIDIPortRef midiPort;
@property NSMutableDictionary<NSNumber *, HeartMidiSource *> *sources;
// Disconnected contexts stay alive until the input port is disposed.
@property NSMutableArray<HeartMidiSource *> *retiredSources;
@property HeartInputs *inputs;
@property id eventMonitor;
@property NSTimer *inputTimer;
@property BOOL touchLocked;
@property BOOL pressureReady;
@property BOOL inputPending;
@property NSTimeInterval inputStarted;
@property NSTimeInterval touchHeartbeat;
- (void)releaseTouch;
- (void)scanMidi;
- (void)emitMidi:(NSDictionary *)event;
@end

static void HeartMidiNotify(const MIDINotification *notification, void *context) {
 HeartWindow *owner=(__bridge HeartWindow *)context;
 dispatch_async(dispatch_get_main_queue(), ^{[owner scanMidi];});
}
static void HeartMidiRead(const MIDIPacketList *packets, void *context, void *sourceContext) {
 HeartWindow *owner=(__bridge HeartWindow *)context;
 HeartMidiSource *source=(__bridge HeartMidiSource *)sourceContext;
 if(!source)return;
 NSMutableArray *events=[NSMutableArray array];
 @synchronized(source){
  const MIDIPacket *packet=&packets->packet[0];
  for(UInt32 p=0;p<packets->numPackets;p++,packet=MIDIPacketNext(packet)) {
   for(UInt16 i=0;i<packet->length;i++) {
    UInt8 byte=packet->data[i];
    if(byte>=0xF8)continue; // Clock is not a controller action; preserve running status.
    if(byte&0x80){
     [source.pending removeAllObjects];
     source.status=byte<0xF0?byte:0; // Ignore system messages and SysEx payloads.
     continue;
    }
    if(!source.status)continue;
    [source.pending addObject:@(byte)];
    UInt8 kind=source.status&0xF0;
    NSUInteger length=(kind==0xC0||kind==0xD0)?1:2;
    if(source.pending.count==length){
     NSMutableArray *data=[NSMutableArray arrayWithObject:@(source.status)];
     [data addObjectsFromArray:source.pending];
     [events addObject:@{@"type":@"message",@"id":source.identifier,@"name":source.name,@"data":data}];
     [source.pending removeAllObjects];
    }
   }
  }
 }
 if(events.count)dispatch_async(dispatch_get_main_queue(), ^{
  // Discard packets from a source disconnected before delivery.
  if(owner.sources[@(source.endpoint)]!=source)return;
  for(NSDictionary *event in events)[owner emitMidi:event];
 });
}

@implementation HeartWindow
- (BOOL)isLocalSurface:(NSURL *)url {
 return [url.scheme isEqualToString:@"http"] && [url.host isEqualToString:@"localhost"] && url.port.integerValue==8875;
}
- (void)emitMidi:(NSDictionary *)event {
 NSAssert([NSThread isMainThread],@"WebKit requires the main thread");
 if(![self isLocalSurface:self.web.URL])return;
 NSData *json=[NSJSONSerialization dataWithJSONObject:event options:0 error:nil];
 NSString *payload=[[NSString alloc] initWithData:json encoding:NSUTF8StringEncoding];
 [self.web evaluateJavaScript:[NSString stringWithFormat:@"window.heartNativeMidi && window.heartNativeMidi(%@)",payload] completionHandler:nil];
}
- (void)scanMidi {
 NSAssert([NSThread isMainThread],@"MIDI discovery requires the main thread");
 if(!self.midiPort)return;
 NSMutableSet *present=[NSMutableSet set];
 for(ItemCount i=0;i<MIDIGetNumberOfSources();i++){
  MIDIEndpointRef endpoint=MIDIGetSource(i);
  NSNumber *key=@(endpoint);[present addObject:key];
  if(self.sources[key])continue;
  HeartMidiSource *source=[HeartMidiSource new];source.endpoint=endpoint;
  SInt32 uid=0;MIDIObjectGetIntegerProperty(endpoint,kMIDIPropertyUniqueID,&uid);
  source.identifier=[NSString stringWithFormat:@"coremidi:%d",uid?:endpoint];
  CFStringRef name=NULL;MIDIObjectGetStringProperty(endpoint,kMIDIPropertyDisplayName,&name);
  source.name=name?CFBridgingRelease(name):@"MIDI input";
  source.pending=[NSMutableArray array];
  if(MIDIPortConnectSource(self.midiPort,endpoint,(__bridge void *)source)==noErr)self.sources[key]=source;
 }
 for(NSNumber *key in [self.sources.allKeys copy])if(![present containsObject:key]){
  HeartMidiSource *source=self.sources[key];MIDIPortDisconnectSource(self.midiPort,source.endpoint);
  [self.retiredSources addObject:source];[self.sources removeObjectForKey:key];
 }
 NSMutableArray *inputs=[NSMutableArray array];
 for(HeartMidiSource *source in self.sources.allValues)[inputs addObject:@{@"id":source.identifier,@"name":source.name}];
 [inputs sortUsingComparator:^NSComparisonResult(NSDictionary *a,NSDictionary *b){return [a[@"name"] compare:b[@"name"]];}];
 [self emitMidi:@{@"type":@"ports",@"inputs":inputs}];
}
- (void)userContentController:(WKUserContentController *)controller didReceiveScriptMessage:(WKScriptMessage *)message {
 if(!message.frameInfo.isMainFrame || ![self isLocalSurface:message.frameInfo.request.URL])return;
 if([message.name isEqualToString:@"heartMidi"] && [message.body isEqual:@"scan"])[self scanMidi];
 if(![message.name isEqualToString:@"heartInputs"] || ![message.body isKindOfClass:NSDictionary.class])return;
 NSString *action=message.body[@"action"];
 if([action isEqualToString:@"release"]){[self releaseTouch];return;}
 if([action isEqualToString:@"heartbeat"]){self.touchHeartbeat=NSProcessInfo.processInfo.systemUptime;return;}
 if([action isEqualToString:@"grab"] && !self.touchLocked) {
  if(!self.inputs.touchDevices || !NSApp.active || !self.window.keyWindow || CGAssociateMouseAndMouseCursorPosition(false)!=kCGErrorSuccess){[self emitInput:@{@"type":@"capture",@"locked":@NO,@"error":@"Trackpad capture unavailable"}];return;}
  self.touchLocked=YES;self.pressureReady=NO;self.touchHeartbeat=NSProcessInfo.processInfo.systemUptime;[NSCursor hide];
  [self emitInput:@{@"type":@"capture",@"locked":@YES}];
 }
}
- (void)webView:(WKWebView *)webView didFinishNavigation:(WKNavigation *)navigation {[self scanMidi];}
- (void)webView:(WKWebView *)webView didStartProvisionalNavigation:(WKNavigation *)navigation {[self releaseTouch];}
- (void)webViewWebContentProcessDidTerminate:(WKWebView *)webView {[self releaseTouch];}
- (void)emitInput:(NSDictionary *)event {
 if(![self isLocalSurface:self.web.URL])return;
 NSData *json=[NSJSONSerialization dataWithJSONObject:event options:0 error:nil];
 NSString *payload=[[NSString alloc] initWithData:json encoding:NSUTF8StringEncoding];
 [self.web evaluateJavaScript:[NSString stringWithFormat:@"window.heartNativeInputs?.(%@)",payload] completionHandler:nil];
}
- (void)inputTick:(NSTimer *)timer {
 NSTimeInterval now=NSProcessInfo.processInfo.systemUptime;
 if(self.touchLocked && now-self.touchHeartbeat>2)[self releaseTouch];
 if(self.inputPending){if(now-self.inputStarted>1)[self releaseTouch];return;}
 NSDictionary *snapshot=[self.inputs snapshot];
 for(NSDictionary *frame in snapshot[@"touch"])if(frame[@"fingers"] && ![frame[@"fingers"] count])self.pressureReady=YES;
 if(!NSApp.active || !self.window.keyWindow || ![self isLocalSurface:self.web.URL])return;
 self.inputPending=YES;self.inputStarted=now;
 NSData *json=[NSJSONSerialization dataWithJSONObject:snapshot options:0 error:nil];
 NSString *payload=[[NSString alloc] initWithData:json encoding:NSUTF8StringEncoding];
 [self.web evaluateJavaScript:[NSString stringWithFormat:@"window.heartNativeInputs?.(%@)",payload] completionHandler:^(id value,NSError *error){self.inputPending=NO;if(error && self.touchLocked)[self releaseTouch];}];
}
- (void)releaseTouch {
 if(self.touchLocked){self.touchLocked=NO;CGAssociateMouseAndMouseCursorPosition(true);[NSCursor unhide];}
 [self emitInput:@{@"type":@"capture",@"locked":@NO}];
}
- (void)applicationDidResignActive:(NSNotification *)notification {[self releaseTouch];[self emitInput:@{@"type":@"suspend"}];}
- (void)applicationDidBecomeActive:(NSNotification *)notification {[self emitInput:@{@"type":@"resume"}];}
- (void)windowDidResignKey:(NSNotification *)notification {[self releaseTouch];[self emitInput:@{@"type":@"suspend"}];}
- (void)windowDidBecomeKey:(NSNotification *)notification {[self emitInput:@{@"type":@"resume"}];}
- (void)suspendInputs:(NSNotification *)notification {[self releaseTouch];[self emitInput:@{@"type":@"suspend"}];}
- (void)applicationDidFinishLaunching:(NSNotification *)notification {
 self.sources=[NSMutableDictionary dictionary];self.retiredSources=[NSMutableArray array];
 OSStatus result=MIDIClientCreate(CFSTR("Heart v2"),HeartMidiNotify,(__bridge void *)self,&_midiClient);
 if(result==noErr)result=MIDIInputPortCreate(self.midiClient,CFSTR("Heart controller input"),HeartMidiRead,(__bridge void *)self,&_midiPort);
 if(result!=noErr)NSLog(@"Heart MIDI unavailable: %d",(int)result);
 self.window=[[NSWindow alloc] initWithContentRect:NSMakeRect(0,0,1280,860) styleMask:NSWindowStyleMaskTitled|NSWindowStyleMaskClosable|NSWindowStyleMaskMiniaturizable|NSWindowStyleMaskResizable backing:NSBackingStoreBuffered defer:NO];
 self.window.title=@"Heart v2";self.window.delegate=self;[self.window setFrameAutosaveName:@"HeartV2Surface"];[self.window center];
 WKWebViewConfiguration *config=[WKWebViewConfiguration new];
 [config.userContentController addScriptMessageHandler:self name:@"heartMidi"];
 [config.userContentController addScriptMessageHandler:self name:@"heartInputs"];
 self.web=[[WKWebView alloc] initWithFrame:self.window.contentView.bounds configuration:config];self.web.navigationDelegate=self;
 self.web.autoresizingMask=NSViewWidthSizable|NSViewHeightSizable;self.window.contentView=self.web;
 [self.web loadRequest:[NSURLRequest requestWithURL:[NSURL URLWithString:@"http://localhost:8875/"]]];
 [self.window makeKeyAndOrderFront:nil];[NSApp activateIgnoringOtherApps:YES];
 self.inputs=[HeartInputs new];
 self.inputTimer=[NSTimer scheduledTimerWithTimeInterval:1./60 target:self selector:@selector(inputTick:) userInfo:nil repeats:YES];
 __weak HeartWindow *weak=self;
 self.eventMonitor=[NSEvent addLocalMonitorForEventsMatchingMask:NSEventMaskAny handler:^NSEvent *(NSEvent *event){
  HeartWindow *h=weak;if(!h.touchLocked)return event;
  if(event.type==NSEventTypeKeyDown && (event.keyCode==53 || (event.modifierFlags&NSEventModifierFlagCommand))){[h releaseTouch];return event.keyCode==53?nil:event;}
  if(event.type==NSEventTypePressure){if(event.stage==0)h.pressureReady=YES;else if(h.pressureReady)[h releaseTouch];return nil;}
  switch(event.type){
   case NSEventTypeMouseMoved:case NSEventTypeLeftMouseDragged:case NSEventTypeRightMouseDragged:
   case NSEventTypeLeftMouseDown:case NSEventTypeLeftMouseUp:case NSEventTypeRightMouseDown:case NSEventTypeRightMouseUp:
   case NSEventTypeOtherMouseDown:case NSEventTypeOtherMouseUp:case NSEventTypeScrollWheel:case NSEventTypeMagnify:
   case NSEventTypeRotate:case NSEventTypeSwipe:case NSEventTypeGesture:case NSEventTypeBeginGesture:case NSEventTypeEndGesture:return nil;
   default:return event;
  }
 }];
 for(NSString *name in @[NSWorkspaceWillSleepNotification,NSWorkspaceScreensDidSleepNotification,NSWorkspaceSessionDidResignActiveNotification])[NSWorkspace.sharedWorkspace.notificationCenter addObserver:self selector:@selector(suspendInputs:) name:name object:nil];
}
- (void)applicationWillTerminate:(NSNotification *)notification {
 [self releaseTouch];[self.inputTimer invalidate];[NSEvent removeMonitor:self.eventMonitor];[NSWorkspace.sharedWorkspace.notificationCenter removeObserver:self];
 if(self.midiPort)MIDIPortDispose(self.midiPort);
 if(self.midiClient)MIDIClientDispose(self.midiClient);
 [self.web.configuration.userContentController removeScriptMessageHandlerForName:@"heartMidi"];
 [self.web.configuration.userContentController removeScriptMessageHandlerForName:@"heartInputs"];
}
- (BOOL)applicationShouldTerminateAfterLastWindowClosed:(NSApplication *)sender{return YES;}
@end
int main(){@autoreleasepool{NSApplication *app=[NSApplication sharedApplication];[app setActivationPolicy:NSApplicationActivationPolicyRegular];HeartWindow *delegate=[HeartWindow new];app.delegate=delegate;[app run];}return 0;}
