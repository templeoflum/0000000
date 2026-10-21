#import <Cocoa/Cocoa.h>
#import <MetalKit/MetalKit.h>
#import <WebKit/WebKit.h>
#import <Syphon/Syphon.h>
#import <IOKit/IOKitLib.h>

@interface Heart : NSObject <NSApplicationDelegate, MTKViewDelegate, WKScriptMessageHandler, WKNavigationDelegate, NSWindowDelegate>
@property NSWindow *window;
@property WKWebView *web;
@property MTKView *view;
@property NSTextField *status;
@property SyphonMetalClient *client;
@property id<MTLCommandQueue> queue;
@property id<MTLRenderPipelineState> pipeline;
@property dispatch_semaphore_t flight;
@property double lastFrame;
@property NSUInteger frames;
@property NSUInteger width;
@property NSUInteger height;
@property BOOL pixelMode;
@property double lastTick;
@property BOOL mouseLocked;
@property id mouseMonitor;
@property double mouseX;
@property double mouseY;
@property NSEventModifierFlags mouseFlags;
@property BOOL mousePending;
@end
@implementation Heart
- (void)applicationDidFinishLaunching:(NSNotification *)notification {
    [NSApp setActivationPolicy:NSApplicationActivationPolicyRegular];
    NSMenu *menu=[NSMenu new], *appMenu=[NSMenu new];
    NSMenuItem *root=[NSMenuItem new]; root.submenu=appMenu; [menu addItem:root];
    [appMenu addItemWithTitle:@"Quit Heart" action:@selector(terminate:) keyEquivalent:@"q"];
    NSApp.mainMenu=menu;
    self.window=[[NSWindow alloc] initWithContentRect:NSMakeRect(0,0,1480,900) styleMask:NSWindowStyleMaskTitled|NSWindowStyleMaskClosable|NSWindowStyleMaskResizable|NSWindowStyleMaskMiniaturizable backing:NSBackingStoreBuffered defer:NO];
    self.window.title=@"Heart · Live output"; self.window.minSize=NSMakeSize(1100,700);
    self.window.delegate=self; self.window.acceptsMouseMovedEvents=YES;
    self.window.backgroundColor=[NSColor colorWithWhite:.04 alpha:1];
    NSSplitView *split=[[NSSplitView alloc] initWithFrame:self.window.contentView.bounds];
    split.vertical=NO; split.dividerStyle=NSSplitViewDividerStyleThin;
    split.autoresizingMask=NSViewWidthSizable|NSViewHeightSizable;
    [self.window.contentView addSubview:split];
    NSView *monitor=[[NSView alloc] initWithFrame:NSMakeRect(0,0,1480,320)];
    self.view=[[MTKView alloc] initWithFrame:NSMakeRect(0,30,1480,290) device:MTLCreateSystemDefaultDevice()];
    self.view.autoresizingMask=NSViewWidthSizable|NSViewHeightSizable;
    self.view.colorPixelFormat=MTLPixelFormatBGRA8Unorm; self.view.clearColor=MTLClearColorMake(0,0,0,1);
    self.view.preferredFramesPerSecond=60; self.view.delegate=self;
    CGColorSpaceRef space=CGColorSpaceCreateWithName(kCGColorSpaceSRGB);
    self.view.colorspace=space; CGColorSpaceRelease(space);
    [monitor addSubview:self.view];
    self.status=[NSTextField labelWithString:@"Waiting for Arena · Composition Syphon output…"];
    self.status.frame=NSMakeRect(16,6,1150,20); self.status.textColor=NSColor.lightGrayColor;
    self.status.font=[NSFont monospacedSystemFontOfSize:11 weight:NSFontWeightRegular];
    self.status.autoresizingMask=NSViewWidthSizable; [monitor addSubview:self.status];
    NSButton *fit=[NSButton buttonWithTitle:@"Fit / 1:1 pixels" target:self action:@selector(togglePixels:)];
    fit.frame=NSMakeRect(1300,2,160,26); fit.autoresizingMask=NSViewMinXMargin; [monitor addSubview:fit];
    WKWebViewConfiguration *config=[WKWebViewConfiguration new];
    [config.userContentController addScriptMessageHandler:self name:@"heartPointer"];
    NSString *pointer=[NSString stringWithContentsOfFile:[NSBundle.mainBundle pathForResource:@"pointer" ofType:@"js"] encoding:NSUTF8StringEncoding error:nil];
    if(pointer) [config.userContentController addUserScript:[[WKUserScript alloc] initWithSource:pointer injectionTime:WKUserScriptInjectionTimeAtDocumentStart forMainFrameOnly:YES]];
    self.web=[[WKWebView alloc] initWithFrame:NSMakeRect(0,0,1480,580) configuration:config];
    self.web.navigationDelegate=self;
    [self.web loadRequest:[NSURLRequest requestWithURL:[NSURL URLWithString:@"http://127.0.0.1:8765"]]];
    [split addSubview:monitor]; [split addSubview:self.web]; [split adjustSubviews];
    self.queue=[self.view.device newCommandQueue]; self.flight=dispatch_semaphore_create(1);
    NSString *shader=@"#include <metal_stdlib>\nusing namespace metal;\nstruct V{float4 p [[position]];float2 uv;};\nvertex V vs(uint i [[vertex_id]]){float2 p[3]={float2(-1,-1),float2(3,-1),float2(-1,3)};V o;o.p=float4(p[i],0,1);o.uv=float2((p[i].x+1)*.5,1-(p[i].y+1)*.5);return o;}\nfragment float4 fs(V v [[stage_in]],texture2d<float> t [[texture(0)]]){constexpr sampler s(coord::normalized,address::clamp_to_edge,filter::linear);return float4(t.sample(s,v.uv).rgb,1);}";
    NSError *error=nil;
    id<MTLLibrary> library=[self.view.device newLibraryWithSource:shader options:nil error:&error];
    MTLRenderPipelineDescriptor *desc=[MTLRenderPipelineDescriptor new];
    desc.vertexFunction=[library newFunctionWithName:@"vs"]; desc.fragmentFunction=[library newFunctionWithName:@"fs"];
    desc.colorAttachments[0].pixelFormat=self.view.colorPixelFormat;
    self.pipeline=[self.view.device newRenderPipelineStateWithDescriptor:desc error:&error];
    if(!self.pipeline){ NSLog(@"Metal setup failed: %@",error); [NSApp terminate:nil]; return; }
    [SyphonServerDirectory sharedDirectory];
    [NSTimer scheduledTimerWithTimeInterval:1 target:self selector:@selector(tick:) userInfo:nil repeats:YES];
    [NSTimer scheduledTimerWithTimeInterval:1.0/60 target:self selector:@selector(mouseTick:) userInfo:nil repeats:YES];
    __weak Heart *weakSelf=self;
    self.mouseMonitor=[NSEvent addLocalMonitorForEventsMatchingMask:NSEventMaskAny handler:^NSEvent *(NSEvent *event){
        Heart *h=weakSelf;
        if(!h.mouseLocked) return event;
        if(event.type==NSEventTypeKeyDown && (event.keyCode==53 || (event.modifierFlags & NSEventModifierFlagCommand))){
            [h releaseMouse]; return event.keyCode==53?nil:event;
        }
        switch(event.type){
            case NSEventTypeMouseMoved: case NSEventTypeLeftMouseDragged: case NSEventTypeRightMouseDragged:
                h.mouseX+=event.deltaX; h.mouseY+=event.deltaY; h.mouseFlags=event.modifierFlags; return nil;
            case NSEventTypeLeftMouseDown: case NSEventTypeRightMouseDown: case NSEventTypeOtherMouseDown: return nil;
            case NSEventTypeLeftMouseUp:
                [h.web evaluateJavaScript:@"window.heartPointer?.click()" completionHandler:nil]; return nil;
            case NSEventTypeRightMouseUp: [h releaseMouse]; return nil;
            case NSEventTypeOtherMouseUp: case NSEventTypeScrollWheel: case NSEventTypeMagnify:
            case NSEventTypeRotate: case NSEventTypeSwipe: return nil;
            default: return event;
        }
    }];
    [self.window center]; [self.window makeKeyAndOrderFront:nil]; [NSApp activateIgnoringOtherApps:YES];
}
- (void)releaseMouse {
    if(self.mouseLocked){ CGAssociateMouseAndMouseCursorPosition(true); [NSCursor unhide]; NSLog(@"Pointer released"); }
    self.mouseLocked=NO; self.mouseX=self.mouseY=0;
    [self.web evaluateJavaScript:@"window.heartPointer?.released()" completionHandler:nil];
}
- (void)applicationDidResignActive:(NSNotification *)notification { [self releaseMouse]; }
- (void)windowDidResignKey:(NSNotification *)notification { [self releaseMouse]; }
- (void)webView:(WKWebView *)webView didStartProvisionalNavigation:(WKNavigation *)navigation { [self releaseMouse]; }
- (void)webViewWebContentProcessDidTerminate:(WKWebView *)webView { [self releaseMouse]; }
- (void)userContentController:(WKUserContentController *)controller didReceiveScriptMessage:(WKScriptMessage *)message {
    NSURL *url=message.frameInfo.request.URL;
    if(!message.frameInfo.mainFrame || ![url.host isEqualToString:@"127.0.0.1"] || url.port.integerValue!=8765) return;
    if([message.body isEqual:@"unlock"]){ if(self.mouseLocked) [self releaseMouse]; return; }
    if(![message.body isEqual:@"lock"] || self.mouseLocked) return;
    if(!NSApp.active || !self.window.keyWindow || CGAssociateMouseAndMouseCursorPosition(false)!=kCGErrorSuccess){
        [self.web evaluateJavaScript:@"window.heartPointer?.failed()" completionHandler:nil]; return;
    }
    self.mouseLocked=YES; self.mouseX=self.mouseY=0; [NSCursor hide];
    NSLog(@"Pointer captured");
    [self.web evaluateJavaScript:@"window.heartPointer?.acquired()" completionHandler:^(id value,NSError *error){if(error)[self releaseMouse];}];
}
- (void)mouseTick:(NSTimer *)timer {
    if(!self.mouseLocked || self.mousePending || (!self.mouseX && !self.mouseY)) return;
    NSEventModifierFlags f=self.mouseFlags;
    NSString *js=[NSString stringWithFormat:@"window.heartPointer?.move(%f,%f,%@,%@,%@,%@)",self.mouseX,self.mouseY,
      (f & NSEventModifierFlagShift)?@"true":@"false",(f & NSEventModifierFlagOption)?@"true":@"false",
      (f & NSEventModifierFlagControl)?@"true":@"false",(f & NSEventModifierFlagCommand)?@"true":@"false"];
    self.mouseX=self.mouseY=0; self.mousePending=YES;
    [self.web evaluateJavaScript:js completionHandler:^(id value,NSError *error){self.mousePending=NO;if(error)[self releaseMouse];}];
}
- (NSString *)gpuUsage {
    io_iterator_t iterator=0;
    if(IOServiceGetMatchingServices(kIOMainPortDefault,IOServiceMatching("AGXAccelerator"),&iterator)!=KERN_SUCCESS) return @"GPU —";
    NSNumber *usage=nil; io_service_t service;
    while((service=IOIteratorNext(iterator))){
        NSDictionary *stats=CFBridgingRelease(IORegistryEntryCreateCFProperty(service,CFSTR("PerformanceStatistics"),kCFAllocatorDefault,0));
        id value=stats[@"Device Utilization %"];
        if([value isKindOfClass:NSNumber.class]) usage=value;
        IOObjectRelease(service);
    }
    IOObjectRelease(iterator);
    return usage?[NSString stringWithFormat:@"GPU %.0f%% (Mac)",usage.doubleValue]:@"GPU unavailable";
}
- (void)togglePixels:(id)sender { self.pixelMode=!self.pixelMode; }
- (void)tick:(NSTimer *)timer {
    if(self.client && !self.client.isValid){ [self.client stop]; self.client=nil; }
    if(!self.client){
        // Never silently connect to another app or an arbitrary Arena layer output.
        for(NSDictionary *s in [SyphonServerDirectory sharedDirectory].servers){
            if([s[SyphonServerDescriptionAppNameKey] containsString:@"Arena"] && [s[SyphonServerDescriptionNameKey] isEqualToString:@"Composition"]){
                self.client=[[SyphonMetalClient alloc] initWithServerDescription:s device:self.view.device options:nil newFrameHandler:nil];
                NSLog(@"Connected: %@ / %@",s[SyphonServerDescriptionAppNameKey],s[SyphonServerDescriptionNameKey]); break;
            }
        }
    }
    double age=NSDate.timeIntervalSinceReferenceDate-self.lastFrame;
    double now=NSDate.timeIntervalSinceReferenceDate;
    double fps=self.lastTick ? self.frames/(now-self.lastTick) : 0; self.lastTick=now;
    BOOL visible=(self.window.occlusionState & NSWindowOcclusionStateVisible)!=0;
    NSString *state=!visible?@"PAUSED · window covered":age>1?@"STALE — no new frame":@"LIVE · uncompressed GPU";
    NSString *line=self.client ? [NSString stringWithFormat:@"%@   |   Output %.1f FPS   |   %lu × %lu   |   %@   |   %@",[self gpuUsage],fps,self.width,self.height,self.pixelMode?@"1:1 pixels (crop)":@"Fit",state] : [NSString stringWithFormat:@"%@   |   Waiting for Arena · Composition Syphon output",[self gpuUsage]];
    self.status.stringValue=line; NSLog(@"%@",line); self.frames=0;
}
- (void)mtkView:(MTKView *)view drawableSizeWillChange:(CGSize)size {}
- (void)drawInMTKView:(MTKView *)view {
    if(!(self.window.occlusionState & NSWindowOcclusionStateVisible) || !self.client.isValid) return;
    if(dispatch_semaphore_wait(self.flight,DISPATCH_TIME_NOW)) return;
    BOOL fresh=self.client.hasNewFrame;
    id<MTLTexture> texture=[self.client newFrameImage];
    if(!texture){ dispatch_semaphore_signal(self.flight); return; }
    MTLRenderPassDescriptor *pass=view.currentRenderPassDescriptor;
    id<CAMetalDrawable> drawable=view.currentDrawable;
    if(!pass || !drawable){ dispatch_semaphore_signal(self.flight); return; }
    self.width=texture.width; self.height=texture.height;
    if(fresh){self.frames++; self.lastFrame=NSDate.timeIntervalSinceReferenceDate;}
    double dw=view.drawableSize.width, dh=view.drawableSize.height;
    double scale=self.pixelMode?1:MIN(dw/texture.width,dh/texture.height);
    double w=texture.width*scale,h=texture.height*scale;
    id<MTLCommandBuffer> command=[self.queue commandBuffer];
    id<MTLRenderCommandEncoder> encoder=[command renderCommandEncoderWithDescriptor:pass];
    [encoder setRenderPipelineState:self.pipeline];
    [encoder setViewport:(MTLViewport){(dw-w)/2,(dh-h)/2,w,h,0,1}];
    [encoder setFragmentTexture:texture atIndex:0];
    [encoder drawPrimitives:MTLPrimitiveTypeTriangle vertexStart:0 vertexCount:3];
    [encoder endEncoding];
    dispatch_semaphore_t flight=self.flight;
    [command addCompletedHandler:^(id<MTLCommandBuffer> b){dispatch_semaphore_signal(flight);}];
    [command presentDrawable:drawable]; [command commit];
}
- (BOOL)applicationShouldTerminateAfterLastWindowClosed:(NSApplication *)sender {return YES;}
- (void)applicationWillTerminate:(NSNotification *)notification {[self releaseMouse]; [NSEvent removeMonitor:self.mouseMonitor]; [self.client stop];}
@end
int main(int argc,const char **argv){@autoreleasepool{NSApplication *app=[NSApplication sharedApplication]; Heart *delegate=[Heart new]; app.delegate=delegate; [app run];}return 0;}
