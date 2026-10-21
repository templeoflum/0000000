#import <Cocoa/Cocoa.h>
#import <MetalKit/MetalKit.h>
#import <WebKit/WebKit.h>
#import <Syphon/Syphon.h>
#import <IOKit/IOKitLib.h>

// Static set enclosure; no video filtering, copying or second rendering surface.
@interface HeartTVWindow : NSWindow
@end
@implementation HeartTVWindow
- (BOOL)canBecomeKeyWindow {return YES;}
- (BOOL)canBecomeMainWindow {return NO;}
@end
@interface HeartPhysicalButtonCell : NSButtonCell
@end
@implementation HeartPhysicalButtonCell
- (void)drawBezelWithFrame:(NSRect)frame inView:(NSView *)view {
    CGFloat k=MAX(1,frame.size.height/26.0);BOOL pressed=self.highlighted;
    NSRect socket=NSInsetRect(frame,1,1);
    [[NSColor colorWithWhite:.035 alpha:1] setFill];[[NSBezierPath bezierPathWithRoundedRect:socket xRadius:3*k yRadius:3*k] fill];
    [[NSColor colorWithWhite:.48 alpha:.6] setStroke];NSBezierPath *lip=[NSBezierPath bezierPathWithRoundedRect:socket xRadius:3*k yRadius:3*k];lip.lineWidth=.7;[lip stroke];
    NSRect base=NSInsetRect(socket,2*k,2*k);base.size.height-=2*k;
    [[NSColor colorWithWhite:.08 alpha:1] setFill];[[NSBezierPath bezierPathWithRoundedRect:base xRadius:2*k yRadius:2*k] fill];
    NSRect cap=base;cap.origin.y+=(pressed?4:1)*k;cap.size.height-=3*k;
    NSBezierPath *shape=[NSBezierPath bezierPathWithRoundedRect:cap xRadius:2*k yRadius:2*k];
    NSGradient *plastic=[[NSGradient alloc] initWithStartingColor:[NSColor colorWithWhite:pressed?.20:.36 alpha:1] endingColor:[NSColor colorWithWhite:.14 alpha:1]];[plastic drawInBezierPath:shape angle:90];
    [[NSColor colorWithWhite:pressed?.27:.51 alpha:1] setStroke];shape.lineWidth=.7;[shape stroke];
    // Engraved finger groove on the cap, with the light catching its lower edge.
    CGFloat y=NSMidY(cap);NSBezierPath *groove=[NSBezierPath bezierPath];[groove moveToPoint:NSMakePoint(NSMinX(cap)+7*k,y)];[groove lineToPoint:NSMakePoint(NSMaxX(cap)-7*k,y)];
    [[NSColor colorWithWhite:.07 alpha:1] setStroke];groove.lineWidth=1.2*k;[groove stroke];
    NSAffineTransform *shift=[NSAffineTransform transform];[shift translateXBy:0 yBy:k];[groove transformUsingAffineTransform:shift];[[NSColor colorWithWhite:.40 alpha:1] setStroke];groove.lineWidth=.6*k;[groove stroke];
    if(self.showsFirstResponder){[[NSColor colorWithCalibratedRed:.72 green:.70 blue:.62 alpha:1] setStroke];shape.lineWidth=1;[shape stroke];}
}
- (void)drawInteriorWithFrame:(NSRect)frame inView:(NSView *)view {
    // Labels are engraved above the physical caps on the enclosure, not printed as app buttons.
}
@end
@interface HeartReadout : NSTextField
@end
@implementation HeartReadout
- (void)drawRect:(NSRect)rect {
    if([self.window isKindOfClass:HeartTVWindow.class]){
        NSBezierPath *well=[NSBezierPath bezierPathWithRoundedRect:NSInsetRect(self.bounds,.5,.5) xRadius:2 yRadius:2];
        [[NSColor colorWithWhite:.018 alpha:1] setFill];[well fill];[[NSColor colorWithWhite:.26 alpha:1] setStroke];[well stroke];
    }
    [super drawRect:rect];
}
@end
@interface HeartTVFrame : NSView
@property (weak) id controller;
@property (weak) NSView *screenPanel;
@end
@implementation HeartTVFrame
- (CGFloat)hardwareScale {return MIN(1.55,MAX(1,self.bounds.size.width/320.));}
- (void)drawRect:(NSRect)dirty {
    CGFloat w=self.bounds.size.width,h=self.bounds.size.height,k=self.hardwareScale;
    // Cast feet and a substantial charcoal sidewall establish the depth of the set.
    [[NSColor colorWithWhite:.055 alpha:1] setFill];
    for(NSNumber *x in @[@(23*k),@(w-55*k)])[[NSBezierPath bezierPathWithRoundedRect:NSMakeRect(x.doubleValue,2*k,32*k,13*k) xRadius:3*k yRadius:3*k] fill];
    NSRect shell=NSMakeRect(3*k,8*k,w-6*k,h-11*k);
    NSBezierPath *outer=[NSBezierPath bezierPathWithRoundedRect:shell xRadius:8*k yRadius:8*k];
    NSGradient *body=[[NSGradient alloc] initWithStartingColor:[NSColor colorWithWhite:.24 alpha:1] endingColor:[NSColor colorWithWhite:.065 alpha:1]];[body drawInBezierPath:outer angle:-25];
    [[NSColor colorWithWhite:.34 alpha:1] setStroke];outer.lineWidth=.8;[outer stroke];
    NSRect face=NSInsetRect(shell,5*k,5*k);
    [[NSColor colorWithWhite:.11 alpha:1] setFill];[[NSBezierPath bezierPathWithRoundedRect:face xRadius:4*k yRadius:4*k] fill];
    // Brushed aluminum control plate, separate from the black screen molding.
    NSRect fascia=NSMakeRect(11*k,14*k,w-22*k,56*k);
    NSBezierPath *plate=[NSBezierPath bezierPathWithRoundedRect:fascia xRadius:2*k yRadius:2*k];
    NSGradient *metal=[[NSGradient alloc] initWithColors:@[[NSColor colorWithCalibratedRed:.67 green:.675 blue:.635 alpha:1],[NSColor colorWithCalibratedRed:.52 green:.525 blue:.49 alpha:1],[NSColor colorWithCalibratedRed:.62 green:.625 blue:.59 alpha:1]]];[metal drawInBezierPath:plate angle:-90];
    [NSGraphicsContext saveGraphicsState];[plate addClip];
    for(CGFloat y=NSMinY(fascia)+1;y<NSMaxY(fascia);y+=1.5){CGFloat opacity=((int)(y*13)%7==0)?.12:.035;[[NSColor colorWithWhite:1 alpha:opacity] setStroke];NSBezierPath *grain=[NSBezierPath bezierPath];[grain moveToPoint:NSMakePoint(NSMinX(fascia),y)];[grain lineToPoint:NSMakePoint(NSMaxX(fascia),y)];grain.lineWidth=.45;[grain stroke];}
    [NSGraphicsContext restoreGraphicsState];[[NSColor colorWithWhite:.77 alpha:1] setStroke];plate.lineWidth=.7;[plate stroke];
    // Nested bevels around the original, unfiltered screen.
    NSRect rim=NSMakeRect(11*k,73*k,w-22*k,h-85*k);
    NSBezierPath *rimPath=[NSBezierPath bezierPathWithRoundedRect:rim xRadius:5*k yRadius:5*k];
    NSGradient *trim=[[NSGradient alloc] initWithStartingColor:[NSColor colorWithWhite:.34 alpha:1] endingColor:[NSColor colorWithWhite:.08 alpha:1]];[trim drawInBezierPath:rimPath angle:90];
    [[NSColor colorWithWhite:.025 alpha:1] setFill];[[NSBezierPath bezierPathWithRoundedRect:NSInsetRect(rim,3*k,3*k) xRadius:3*k yRadius:3*k] fill];
    [[NSColor colorWithWhite:.18 alpha:1] setStroke];NSBezierPath *inner=[NSBezierPath bezierPathWithRoundedRect:NSInsetRect(rim,5*k,5*k) xRadius:2*k yRadius:2*k];inner.lineWidth=.8;[inner stroke];
    NSColor *ink=[NSColor colorWithCalibratedRed:.14 green:.145 blue:.13 alpha:1];
    [@"HEART MONITOR" drawAtPoint:NSMakePoint(18*k,51*k) withAttributes:@{NSFontAttributeName:[NSFont systemFontOfSize:8*k weight:NSFontWeightHeavy],NSForegroundColorAttributeName:ink}];
    [@"BOUSTROPHEDON" drawAtPoint:NSMakePoint(18*k,34*k) withAttributes:@{NSFontAttributeName:[NSFont systemFontOfSize:5.7*k weight:NSFontWeightBold],NSForegroundColorAttributeName:ink}];
    [@"INSTRUMENT CO." drawAtPoint:NSMakePoint(18*k,26*k) withAttributes:@{NSFontAttributeName:[NSFont systemFontOfSize:5.7*k weight:NSFontWeightMedium],NSForegroundColorAttributeName:ink}];
    // Canonical three-row directional maker mark, reduced without changing its shape.
    CGFloat ox=103*k,oy=24*k,m=.50*k,buttonsLeft=w;for(NSView *control in self.subviews)if([control isKindOfClass:NSButton.class]&&!control.hidden)buttonsLeft=MIN(buttonsLeft,NSMinX(control.frame));
    if(ox+44*m+4*k<buttonsLeft){[ink setStroke];[ink setFill];
    NSBezierPath *mark=[NSBezierPath bezierPath];
    [mark moveToPoint:NSMakePoint(ox+6*m,oy+28*m)];[mark lineToPoint:NSMakePoint(ox+32*m,oy+28*m)];
    [mark moveToPoint:NSMakePoint(ox+38*m,oy+28*m)];[mark lineToPoint:NSMakePoint(ox+38*m,oy+18*m)];[mark lineToPoint:NSMakePoint(ox+12*m,oy+18*m)];
    [mark moveToPoint:NSMakePoint(ox+6*m,oy+18*m)];[mark lineToPoint:NSMakePoint(ox+6*m,oy+8*m)];[mark lineToPoint:NSMakePoint(ox+32*m,oy+8*m)];mark.lineWidth=.8*k;[mark stroke];
    for(int row=0;row<3;row++){CGFloat y=oy+(28-row*10)*m;BOOL left=row==1;CGFloat x=ox+(left?12:32)*m;NSBezierPath *arrow=[NSBezierPath bezierPath];[arrow moveToPoint:NSMakePoint(x,y+3.6*m)];[arrow lineToPoint:NSMakePoint(x+(left?-6.4:6.4)*m,y)];[arrow lineToPoint:NSMakePoint(x,y-3.6*m)];[arrow closePath];[arrow fill];}
    }
    // Engraved labels live on the metal; the pin lamp is a physical white lens.
    NSDictionary *labels=@{@3:@"FIT",@4:@"RESUME",@5:@"DOCK",@6:@"PIN"};
    for(NSView *control in self.subviews)if([control isKindOfClass:NSButton.class]&&!control.hidden){
        NSButton *button=(NSButton *)control;NSString *label=labels[@(button.tag)];if(!label)continue;
        NSMutableParagraphStyle *center=[NSMutableParagraphStyle new];center.alignment=NSTextAlignmentCenter;
        [label drawInRect:NSMakeRect(control.frame.origin.x,52*k,control.frame.size.width,10*k) withAttributes:@{NSFontAttributeName:[NSFont systemFontOfSize:6.4*k weight:NSFontWeightBold],NSForegroundColorAttributeName:ink,NSParagraphStyleAttributeName:center}];
        if(button.tag==6){NSRect lamp=NSMakeRect(NSMidX(control.frame)-2*k,18*k,4*k,4*k);[[NSColor colorWithWhite:.12 alpha:1] setFill];[[NSBezierPath bezierPathWithOvalInRect:NSInsetRect(lamp,-k,-k)] fill];[[NSColor colorWithWhite:[button.title containsString:@"●"]?.91:.26 alpha:1] setFill];[[NSBezierPath bezierPathWithOvalInRect:lamp] fill];}
    }
    // Small dark screw heads and resize knurl; no extra animated decoration.
    for(NSNumber *x in @[@(15*k),@(w-18*k)]){NSRect screw=NSMakeRect(x.doubleValue,16*k,3*k,3*k);[[NSColor colorWithWhite:.25 alpha:1] setFill];[[NSBezierPath bezierPathWithOvalInRect:screw] fill];}
    [[NSColor colorWithWhite:.36 alpha:1] setStroke];for(int i=0;i<3;i++){NSBezierPath *grip=[NSBezierPath bezierPath];[grip moveToPoint:NSMakePoint(w-(16-i*4)*k,8*k)];[grip lineToPoint:NSMakePoint(w-6*k,(18-i*4)*k)];[grip stroke];}
}
- (void)resizeSubviewsWithOldSize:(NSSize)size {
    CGFloat k=self.hardwareScale,w=self.bounds.size.width,h=self.bounds.size.height;
    self.screenPanel.frame=NSMakeRect(18*k,80*k,MAX(1,w-36*k),MAX(1,h-99*k));
    BOOL resuming=NO;for(NSView *control in self.subviews)if(control.tag==4)resuming=!control.hidden;
    CGFloat bw=34*k,gap=8*k,start=w-18*k-(resuming?4:3)*bw-(resuming?3:2)*gap;
    for(NSView *control in self.subviews){
        NSInteger index=-1;switch(control.tag){case 3:index=0;break;case 5:index=1;break;case 6:index=2;break;case 4:index=3;break;}
        if(index>=0)control.frame=NSMakeRect(start+index*(bw+gap),25*k,bw,26*k);
    }
    self.needsDisplay=YES;
}
- (void)mouseDown:(NSEvent *)event {
    NSPoint p=[self convertPoint:event.locationInWindow fromView:nil];
    if(p.x>self.bounds.size.width-22 && p.y<22){
        NSRect start=self.window.frame;NSPoint mouse=NSEvent.mouseLocation;
        while(YES){NSEvent *next=[self.window nextEventMatchingMask:NSEventMaskLeftMouseDragged|NSEventMaskLeftMouseUp];if(next.type==NSEventTypeLeftMouseUp)break;
            NSPoint now=NSEvent.mouseLocation;CGFloat w=MAX(280,start.size.width+now.x-mouse.x),h=MAX(220,start.size.height-now.y+mouse.y);
            [self.window setFrame:NSMakeRect(start.origin.x,NSMaxY(start)-h,w,h) display:YES];
        }
    }else if(event.clickCount==2){[NSApp sendAction:@selector(expandTV:) to:self.controller from:self];}
    else [self.window performWindowDragWithEvent:event];
}
@end
@interface HeartMonitorPanel : NSView
@property BOOL tvMode;
@property BOOL compactDock;
@end
@implementation HeartMonitorPanel
- (void)mouseDown:(NSEvent *)event {if(self.tvMode)[self.window performWindowDragWithEvent:event];else [super mouseDown:event];}
- (void)resizeSubviewsWithOldSize:(NSSize)size {
    CGFloat w=self.bounds.size.width,h=self.bounds.size.height,footer=(self.tvMode||self.compactDock)?24:56;
    for(NSView *child in self.subviews){
        if([child isKindOfClass:MTKView.class]){child.frame=NSMakeRect(0,footer,w,MAX(1,h-footer));continue;}
        if(self.tvMode||self.compactDock){
            if(child.tag==2)child.frame=NSMakeRect(4,2,MAX(1,w-8),20);
        }else switch(child.tag){
            case 2:child.frame=NSMakeRect(10,31,MAX(1,w-20),20);break;
            case 3:child.frame=NSMakeRect(8,2,130,26);break;
            case 4:child.frame=NSMakeRect(142,2,130,26);break;
            case 5:child.frame=NSMakeRect(MAX(276,w-210),2,100,26);break;
            case 6:child.frame=NSMakeRect(MAX(380,w-106),2,100,26);break;
        }
    }
}
@end

@interface Heart : NSObject <NSApplicationDelegate, MTKViewDelegate, WKScriptMessageHandler, WKNavigationDelegate, NSWindowDelegate>
@property NSWindow *window;
@property WKWebView *web;
@property NSSplitView *split;
@property HeartMonitorPanel *monitorPanel;
@property NSWindow *tvWindow;
@property NSButton *dockButton;
@property NSButton *topButton;
@property BOOL detached;
@property BOOL tvLarge;
@property NSRect tvSmallFrame;
@property NSRect tvLargeFrame;
@property BOOL tvTransition;
@property NSUserDefaults *tvPreferences;
@property CGFloat dockHeight;
@property BOOL modularDock;
@property NSRect dockUnitRect;
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
@property double lastAcquireTime;
@property NSMutableArray<NSNumber *> *frameIntervals;
@property BOOL mouseLocked;
@property NSInteger mouseRequestId;
@property id mouseMonitor;
@property double mouseX;
@property double mouseY;
@property NSEventModifierFlags mouseFlags;
@property BOOL mousePending;
@property BOOL sessionSuspended;
@property BOOL systemSleeping;
@property BOOL displaySleeping;
@property BOOL sessionInactive;
@property NSButton *resumeButton;
@end
@implementation Heart
- (void)applicationDidFinishLaunching:(NSNotification *)notification {
    self.frameIntervals=[NSMutableArray new];
    [NSApp setActivationPolicy:NSApplicationActivationPolicyRegular];
    NSMenu *menu=[NSMenu new], *appMenu=[NSMenu new];
    NSMenuItem *root=[NSMenuItem new]; root.submenu=appMenu; [menu addItem:root];
    [appMenu addItemWithTitle:@"Reload controls" action:@selector(reloadControls:) keyEquivalent:@"r"];
    [appMenu addItemWithTitle:@"Resume after sleep" action:@selector(resumeAfterSleep:) keyEquivalent:@""];
    [appMenu addItemWithTitle:@"Dock / detach TV" action:@selector(toggleTV:) keyEquivalent:@"t"];
    [appMenu addItemWithTitle:@"TV always on top" action:@selector(toggleTop:) keyEquivalent:@""];
    [appMenu addItemWithTitle:@"Quit Heart" action:@selector(terminate:) keyEquivalent:@"q"];
    NSApp.mainMenu=menu;
    self.window=[[NSWindow alloc] initWithContentRect:NSMakeRect(0,0,1480,900) styleMask:NSWindowStyleMaskTitled|NSWindowStyleMaskClosable|NSWindowStyleMaskResizable|NSWindowStyleMaskMiniaturizable backing:NSBackingStoreBuffered defer:NO];
    self.window.title=@"Heart · Live output"; self.window.minSize=NSMakeSize(1100,700);
    self.window.delegate=self; self.window.acceptsMouseMovedEvents=YES;
    self.window.backgroundColor=[NSColor colorWithWhite:.04 alpha:1];
    NSSplitView *split=[[NSSplitView alloc] initWithFrame:self.window.contentView.bounds];
    self.split=split;split.vertical=NO; split.dividerStyle=NSSplitViewDividerStyleThin;
    split.autoresizingMask=NSViewWidthSizable|NSViewHeightSizable;
    [self.window.contentView addSubview:split];
    HeartMonitorPanel *monitor=[[HeartMonitorPanel alloc] initWithFrame:NSMakeRect(0,0,1480,320)];self.monitorPanel=monitor;self.dockHeight=320;
    self.view=[[MTKView alloc] initWithFrame:NSMakeRect(0,30,1480,290) device:MTLCreateSystemDefaultDevice()];
    self.view.autoresizingMask=NSViewWidthSizable|NSViewHeightSizable;
    self.view.colorPixelFormat=MTLPixelFormatBGRA8Unorm; self.view.clearColor=MTLClearColorMake(0,0,0,1);
    self.view.preferredFramesPerSecond=60; self.view.delegate=self;
    CGColorSpaceRef space=CGColorSpaceCreateWithName(kCGColorSpaceSRGB);
    self.view.colorspace=space; CGColorSpaceRelease(space);
    [monitor addSubview:self.view];
    NSClickGestureRecognizer *doubleClick=[[NSClickGestureRecognizer alloc] initWithTarget:self action:@selector(expandTV:)];doubleClick.numberOfClicksRequired=2;[self.view addGestureRecognizer:doubleClick];
    self.status=[HeartReadout labelWithString:@"Waiting for Arena · Composition Syphon output…"];
    self.status.tag=2;self.status.lineBreakMode=NSLineBreakByTruncatingTail;self.status.frame=NSMakeRect(16,6,1150,20); self.status.textColor=NSColor.lightGrayColor;
    self.status.font=[NSFont monospacedSystemFontOfSize:11 weight:NSFontWeightRegular];
    self.status.autoresizingMask=NSViewWidthSizable; [monitor addSubview:self.status];
    NSButton *fit=[NSButton buttonWithTitle:@"Fit / 1:1 pixels" target:self action:@selector(togglePixels:)];
    fit.tag=3;fit.frame=NSMakeRect(1300,2,160,26); fit.autoresizingMask=NSViewMinXMargin; [monitor addSubview:fit];
    self.resumeButton=[NSButton buttonWithTitle:@"Resume monitor" target:self action:@selector(resumeAfterSleep:)];
    self.resumeButton.tag=4;self.resumeButton.frame=NSMakeRect(1130,2,160,26);self.resumeButton.autoresizingMask=NSViewMinXMargin;
    self.resumeButton.hidden=YES;[monitor addSubview:self.resumeButton];
    self.dockButton=[NSButton buttonWithTitle:@"Detach TV" target:self action:@selector(toggleTV:)];self.dockButton.tag=5;[monitor addSubview:self.dockButton];
    self.topButton=[NSButton buttonWithTitle:@"On top: off" target:self action:@selector(toggleTop:)];self.topButton.tag=6;self.topButton.hidden=YES;[monitor addSubview:self.topButton];
    self.dockButton.toolTip=@"Move the output into a separate TV window; close that window to dock again.";
    fit.toolTip=@"Fit the complete output, or display one source pixel per screen pixel (may crop). Double-click the detached picture to enlarge.";
    self.topButton.toolTip=@"Keep the TV above other windows. It can still be minimized and never prevents sleep.";
    [monitor resizeSubviewsWithOldSize:NSZeroSize];
    WKWebViewConfiguration *config=[WKWebViewConfiguration new];
    [config.userContentController addScriptMessageHandler:self name:@"heartPointer"];
    NSString *pointer=[NSString stringWithContentsOfFile:[NSBundle.mainBundle pathForResource:@"pointer" ofType:@"js"] encoding:NSUTF8StringEncoding error:nil];
    if(pointer) [config.userContentController addUserScript:[[WKUserScript alloc] initWithSource:pointer injectionTime:WKUserScriptInjectionTimeAtDocumentStart forMainFrameOnly:YES]];
    self.web=[[WKWebView alloc] initWithFrame:NSMakeRect(0,0,1480,580) configuration:config];
    self.web.navigationDelegate=self;
    [self.web loadRequest:[NSURLRequest requestWithURL:[NSURL URLWithString:@"http://127.0.0.1:8765"]]];
    [split addSubview:monitor]; [split addSubview:self.web]; [split adjustSubviews];
    self.queue=[self.view.device newCommandQueue]; self.flight=dispatch_semaphore_create(1);
    NSNotificationCenter *workspace=NSWorkspace.sharedWorkspace.notificationCenter;
    for(NSString *name in @[NSWorkspaceWillSleepNotification,NSWorkspaceScreensDidSleepNotification,NSWorkspaceSessionDidResignActiveNotification])
        [workspace addObserver:self selector:@selector(suspendForSession:) name:name object:nil];
    for(NSString *name in @[NSWorkspaceDidWakeNotification,NSWorkspaceScreensDidWakeNotification,NSWorkspaceSessionDidBecomeActiveNotification])
        [workspace addObserver:self selector:@selector(sessionReturned:) name:name object:nil];
    // Arena's Syphon image arrives bottom-up. Match the native output orientation
    // in this sample pass; no source, layer Transform, or extra video copy is changed.
    NSString *shader=@"#include <metal_stdlib>\nusing namespace metal;\nstruct V{float4 p [[position]];float2 uv;};\nvertex V vs(uint i [[vertex_id]]){float2 p[3]={float2(-1,-1),float2(3,-1),float2(-1,3)};V o;o.p=float4(p[i],0,1);o.uv=float2((p[i].x+1)*.5,(p[i].y+1)*.5);return o;}\nfragment float4 fs(V v [[stage_in]],texture2d<float> t [[texture(0)]]){constexpr sampler s(coord::normalized,address::clamp_to_edge,filter::linear);return float4(t.sample(s,v.uv).rgb,1);}";
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
            case NSEventTypePressure:
                [h.web evaluateJavaScript:[NSString stringWithFormat:@"window.heartPointer?.pressure(%ld,%ld)",(long)event.stage,(long)h.mouseRequestId] completionHandler:nil]; return nil;
            case NSEventTypeMouseMoved: case NSEventTypeLeftMouseDragged: case NSEventTypeRightMouseDragged:
                h.mouseX+=event.deltaX; h.mouseY+=event.deltaY; h.mouseFlags=event.modifierFlags; return nil;
            case NSEventTypeLeftMouseDown:
                [h.web evaluateJavaScript:[NSString stringWithFormat:@"window.heartPointer?.button(true,%ld)",(long)h.mouseRequestId] completionHandler:nil]; return nil;
            case NSEventTypeRightMouseDown: case NSEventTypeOtherMouseDown: return nil;
            case NSEventTypeLeftMouseUp:
                [h.web evaluateJavaScript:[NSString stringWithFormat:@"window.heartPointer?.button(false,%ld)",(long)h.mouseRequestId] completionHandler:nil]; return nil;
            case NSEventTypeRightMouseUp: [h releaseMouse]; return nil;
            case NSEventTypeScrollWheel: {
                NSEventModifierFlags f=event.modifierFlags;NSInteger requestId=h.mouseRequestId;
                NSString *js=[NSString stringWithFormat:@"window.heartPointer?.wheel(%f,%f,%d,%@,%@,%@,%@,%ld)",
                    -event.scrollingDeltaX,-event.scrollingDeltaY,event.hasPreciseScrollingDeltas?0:1,
                    (f & NSEventModifierFlagShift)?@"true":@"false",(f & NSEventModifierFlagOption)?@"true":@"false",
                    (f & NSEventModifierFlagControl)?@"true":@"false",(f & NSEventModifierFlagCommand)?@"true":@"false",(long)requestId];
                [h.web evaluateJavaScript:js completionHandler:^(id value,NSError *error){if(error && h.mouseRequestId==requestId)[h releaseMouse];}]; return nil;
            }
            case NSEventTypeOtherMouseUp: case NSEventTypeMagnify:
            case NSEventTypeRotate: case NSEventTypeSwipe: return nil;
            default: return event;
        }
    }];
    [self.window center]; [self.window makeKeyAndOrderFront:nil]; [NSApp activateIgnoringOtherApps:YES];
}
- (BOOL)outputVisible {
    return self.view.window && self.view.window.isVisible && !self.view.window.isMiniaturized && (self.view.window.occlusionState & NSWindowOcclusionStateVisible)!=0;
}
- (void)toggleTV:(id)sender {
    [self releaseMouse];
    if(self.detached){
        [self saveTVGeometry];
        for(NSView *control in [self.tvWindow.contentView.subviews copy])if([control isKindOfClass:NSButton.class]){[control removeFromSuperview];[self.monitorPanel addSubview:control];}
        ((HeartTVFrame *)self.tvWindow.contentView).screenPanel=nil;
        [self.monitorPanel removeFromSuperview];
        if(!self.modularDock){
            [self.split addSubview:self.monitorPanel positioned:NSWindowBelow relativeTo:self.web];
            self.monitorPanel.frame=NSMakeRect(0,0,self.split.bounds.size.width,self.dockHeight);
            [self.split adjustSubviews];[self.split setPosition:MIN(self.dockHeight,self.split.bounds.size.height-250) ofDividerAtIndex:0];
        }
        [self.tvWindow orderOut:nil];self.detached=NO;self.dockButton.title=@"Detach TV";self.topButton.hidden=YES;
        [self.window makeKeyAndOrderFront:nil];
    }else{
        self.dockHeight=self.monitorPanel.frame.size.height;
        if(!self.tvWindow){
            self.tvWindow=[[HeartTVWindow alloc] initWithContentRect:NSMakeRect(80,160,320,250) styleMask:NSWindowStyleMaskBorderless backing:NSBackingStoreBuffered defer:NO];
            self.tvWindow.title=@"Heart Monitor";self.tvWindow.minSize=NSMakeSize(280,220);self.tvWindow.opaque=NO;self.tvWindow.backgroundColor=NSColor.clearColor;self.tvWindow.hasShadow=YES;self.tvWindow.level=NSFloatingWindowLevel;self.tvWindow.delegate=self;self.tvWindow.releasedWhenClosed=NO;
            HeartTVFrame *frame=[[HeartTVFrame alloc] initWithFrame:NSMakeRect(0,0,320,250)];frame.controller=self;self.tvWindow.contentView=frame;
            [self loadTVGeometry];
            self.tvTransition=YES;[self.tvWindow setFrame:self.tvSmallFrame display:NO];self.tvTransition=NO;
            // Start in the small mode; its geometry and the independent expanded frame are remembered.
        }
        [self.monitorPanel removeFromSuperview];[self.split adjustSubviews];
        [self.tvWindow.contentView addSubview:self.monitorPanel];((HeartTVFrame *)self.tvWindow.contentView).screenPanel=self.monitorPanel;[self.tvWindow.contentView resizeSubviewsWithOldSize:NSZeroSize];
        self.detached=YES;self.dockButton.title=@"Dock TV";self.topButton.hidden=NO;
        [self.tvWindow makeKeyAndOrderFront:nil];
    }
    self.monitorPanel.tvMode=self.detached;
    self.dockButton.title=self.detached?@"Dock":@"Detach TV";
    self.topButton.title=self.tvWindow.level==NSFloatingWindowLevel?@"Pin ●":@"Pin ○";
    self.resumeButton.title=self.detached?@"Resume":@"Resume monitor";
    for(NSView *child in self.monitorPanel.subviews)if([child isKindOfClass:NSButton.class]){
        NSButton *button=(NSButton *)child;
        NSString *title=button.title;id target=button.target;SEL action=button.action;BOOL enabled=button.enabled;
        button.cell=self.detached?[[HeartPhysicalButtonCell alloc] initTextCell:title]:[[NSButtonCell alloc] initTextCell:title];
        button.target=target;button.action=action;button.enabled=enabled;button.focusRingType=self.detached?NSFocusRingTypeNone:NSFocusRingTypeDefault;[button setButtonType:NSButtonTypeMomentaryPushIn];
        button.controlSize=self.detached?NSControlSizeSmall:NSControlSizeRegular;
        button.font=[NSFont systemFontOfSize:self.detached?10:13 weight:NSFontWeightMedium];
        button.bezelStyle=self.detached?NSBezelStyleSmallSquare:NSBezelStyleRounded;
        if(button.tag==3)button.title=self.detached?@"Fit / 1:1":@"Fit / 1:1 pixels";
    }
    if(self.detached){
        for(NSView *control in [self.monitorPanel.subviews copy])if([control isKindOfClass:NSButton.class]){[control removeFromSuperview];[self.tvWindow.contentView addSubview:control];}
        [self.tvWindow.contentView resizeSubviewsWithOldSize:NSZeroSize];
    }
    [self placeWorkspaceMonitor];
    [self.monitorPanel resizeSubviewsWithOldSize:NSZeroSize];self.lastAcquireTime=0;
    // Reparenting never clears suspension or creates a second render loop.
}
- (void)toggleTop:(id)sender {
    if(!self.detached)return;
    BOOL top=self.tvWindow.level!=NSFloatingWindowLevel;
    self.tvWindow.level=top?NSFloatingWindowLevel:NSNormalWindowLevel;
    self.topButton.title=top?@"Pin ●":@"Pin ○";self.tvWindow.contentView.needsDisplay=YES;
}
- (NSRect)tvVisibleFrame {return (self.tvWindow.screen ?: NSScreen.mainScreen).visibleFrame;}
- (NSArray<NSValue *> *)tvDisplayFrames {
    NSMutableArray *frames=[NSMutableArray new];for(NSScreen *screen in NSScreen.screens)[frames addObject:[NSValue valueWithRect:screen.visibleFrame]];return frames;
}
- (NSRect)reachableTVFrame:(NSRect)frame {
    NSArray<NSValue *> *screens=self.tvDisplayFrames;
    if(!screens.count)return frame;
    for(NSValue *value in screens)if(NSIntersectsRect(frame,value.rectValue))return frame;
    NSRect screen=screens.firstObject.rectValue;
    frame.size.width=MIN(frame.size.width,screen.size.width);frame.size.height=MIN(frame.size.height,screen.size.height);
    frame.origin=NSMakePoint(NSMidX(screen)-frame.size.width/2,NSMidY(screen)-frame.size.height/2);return frame;
}
- (NSUserDefaults *)geometryPreferences {return self.tvPreferences ?: NSUserDefaults.standardUserDefaults;}
- (NSRect)storedTVFrame:(NSString *)key fallback:(NSRect)fallback {
    NSString *value=[self.geometryPreferences stringForKey:key];NSRect frame=value?NSRectFromString(value):fallback;
    if(!isfinite(frame.origin.x)||!isfinite(frame.origin.y)||!isfinite(frame.size.width)||!isfinite(frame.size.height)||frame.size.width<280||frame.size.height<220)frame=fallback;
    return [self reachableTVFrame:frame];
}
- (void)loadTVGeometry {
    NSRect screen=self.tvVisibleFrame;
    self.tvSmallFrame=[self storedTVFrame:@"HeartMonitorSmallFrame" fallback:NSMakeRect(80,160,320,250)];
    self.tvLargeFrame=[self storedTVFrame:@"HeartMonitorLargeFrame" fallback:NSMakeRect(NSMidX(screen)-320,NSMidY(screen)-215,640,430)];
    self.tvLarge=NO;
}
- (void)saveTVGeometry {
    if(!self.detached || self.tvTransition)return;
    if(self.tvLarge)self.tvLargeFrame=self.tvWindow.frame;else self.tvSmallFrame=self.tvWindow.frame;
    if(self.tvSmallFrame.size.width>=280)[self.geometryPreferences setObject:NSStringFromRect(self.tvSmallFrame) forKey:@"HeartMonitorSmallFrame"];
    if(self.tvLargeFrame.size.width>=280)[self.geometryPreferences setObject:NSStringFromRect(self.tvLargeFrame) forKey:@"HeartMonitorLargeFrame"];
}
- (void)windowDidMove:(NSNotification *)notification {if(notification.object==self.tvWindow)[self saveTVGeometry];}
- (void)windowDidResize:(NSNotification *)notification {if(notification.object==self.tvWindow)[self saveTVGeometry];}
- (void)expandTV:(id)sender {
    if(!self.detached)return;
    if(self.tvLargeFrame.size.width<280){NSRect screen=self.tvVisibleFrame;if(screen.size.width<=0)return;self.tvLargeFrame=NSMakeRect(NSMidX(screen)-320,NSMidY(screen)-215,640,430);}
    [self saveTVGeometry];self.tvLarge=!self.tvLarge;
    NSRect destination=[self reachableTVFrame:self.tvLarge?self.tvLargeFrame:self.tvSmallFrame];
    self.tvTransition=YES;[self.tvWindow setFrame:destination display:YES animate:NO];self.tvTransition=NO;
    [self saveTVGeometry];
}
- (BOOL)windowShouldClose:(NSWindow *)sender {
    if(sender==self.tvWindow){if(self.detached)[self toggleTV:nil];return NO;}
    return YES;
}
- (void)windowWillClose:(NSNotification *)notification {
    if(notification.object==self.window){[self releaseMouse];[NSApp terminate:nil];}
}
- (void)releaseMouse {
    NSInteger requestId=self.mouseRequestId;
    if(self.mouseLocked){ CGAssociateMouseAndMouseCursorPosition(true); [NSCursor unhide]; NSLog(@"Pointer released"); }
    self.mouseLocked=NO; self.mouseRequestId=0; self.mouseX=self.mouseY=0;
    [self.web evaluateJavaScript:[NSString stringWithFormat:@"window.heartPointer?.released(%ld)",(long)requestId] completionHandler:nil];
}
- (void)applicationDidResignActive:(NSNotification *)notification { [self releaseMouse]; }
- (void)windowDidResignKey:(NSNotification *)notification { [self releaseMouse]; }
- (void)suspendForSession:(NSNotification *)notification {
    if([notification.name isEqual:NSWorkspaceWillSleepNotification])self.systemSleeping=YES;
    if([notification.name isEqual:NSWorkspaceScreensDidSleepNotification])self.displaySleeping=YES;
    if([notification.name isEqual:NSWorkspaceSessionDidResignActiveNotification])self.sessionInactive=YES;
    self.sessionSuspended=YES; [self releaseMouse]; self.view.paused=YES;
    self.resumeButton.hidden=NO;[self.monitorPanel resizeSubviewsWithOldSize:NSZeroSize];if(self.detached)[self.tvWindow.contentView resizeSubviewsWithOldSize:NSZeroSize];
    [self.client stop]; self.client=nil; self.lastAcquireTime=0;
    [self.web evaluateJavaScript:@"cmd({cmd:'release_all'});cmd({cmd:'hold',on:true})" completionHandler:nil];
    self.status.stringValue=self.detached?@"Paused":@"Monitor paused after sleep · click Resume monitor · motion is held separately";
    [self placeWorkspaceMonitor];
}
- (void)sessionReturned:(NSNotification *)notification {
    if([notification.name isEqual:NSWorkspaceDidWakeNotification])self.systemSleeping=NO;
    if([notification.name isEqual:NSWorkspaceScreensDidWakeNotification])self.displaySleeping=NO;
    if([notification.name isEqual:NSWorkspaceSessionDidBecomeActiveNotification])self.sessionInactive=NO;
    // Never resume GPU work or mouse capture from a wake notification alone.
}
- (void)resumeAfterSleep:(id)sender {
    // An explicit action in the active app is stronger evidence than a missed wake notification.
    if(!NSApp.active)return;
    self.systemSleeping=self.displaySleeping=self.sessionInactive=NO;
    self.sessionSuspended=NO;self.lastAcquireTime=0;self.view.paused=NO;self.resumeButton.hidden=YES;[self.monitorPanel resizeSubviewsWithOldSize:NSZeroSize];if(self.detached)[self.tvWindow.contentView resizeSubviewsWithOldSize:NSZeroSize];[self placeWorkspaceMonitor];
    // Motion remains held until the performer chooses Resume motion.
}
- (void)webView:(WKWebView *)webView didStartProvisionalNavigation:(WKNavigation *)navigation { [self releaseMouse];if(self.modularDock&&!self.detached)self.monitorPanel.hidden=YES; }
- (void)placeWorkspaceMonitor {
    if(self.modularDock && !self.detached){
        if(self.monitorPanel.superview!=self.window.contentView){
            [self.monitorPanel removeFromSuperview];[self.split adjustSubviews];
            [self.window.contentView addSubview:self.monitorPanel positioned:NSWindowAbove relativeTo:self.split];
        }
        NSRect u=self.dockUnitRect,b=self.web.bounds;
        CGFloat y=self.web.isFlipped?u.origin.y*b.size.height:(1-u.origin.y-u.size.height)*b.size.height;
        NSRect rect=NSMakeRect(u.origin.x*b.size.width,y,u.size.width*b.size.width,u.size.height*b.size.height);
        self.monitorPanel.frame=[self.web convertRect:rect toView:self.window.contentView];self.monitorPanel.hidden=NO;
    }
    self.monitorPanel.compactDock=self.modularDock&&!self.detached;
    for(NSView *control in self.monitorPanel.subviews)if([control isKindOfClass:NSButton.class])
        control.hidden=self.monitorPanel.compactDock || (control.tag==4&&!self.sessionSuspended) || (control.tag==6&&!self.detached);
    // Detached controls are owned by the TV's metal housing, including after a dock round trip.
    if(self.detached){for(NSView *control in self.tvWindow.contentView.subviews)if([control isKindOfClass:NSButton.class])control.hidden=control.tag==4&&!self.sessionSuspended;self.monitorPanel.hidden=NO;}
    [self.monitorPanel resizeSubviewsWithOldSize:NSZeroSize];
    NSString *js=[NSString stringWithFormat:@"window.heartMonitorState?.({detached:%@,suspended:%@})",self.detached?@"true":@"false",self.sessionSuspended?@"true":@"false"];
    [self.web evaluateJavaScript:js completionHandler:nil];
}
- (void)webViewWebContentProcessDidTerminate:(WKWebView *)webView { [self releaseMouse]; }
- (void)userContentController:(WKUserContentController *)controller didReceiveScriptMessage:(WKScriptMessage *)message {
    NSURL *url=message.frameInfo.request.URL;
    if(!message.frameInfo.mainFrame || ![url.host isEqualToString:@"127.0.0.1"] || url.port.integerValue!=8765) return;
    NSString *pointerAction=nil;NSInteger pointerRequestId=0;
    if([message.body isKindOfClass:NSDictionary.class]){
        NSDictionary *d=message.body;
        if([d[@"action"] isEqual:@"lock"] || [d[@"action"] isEqual:@"unlock"]){
            if(![d[@"id"] isKindOfClass:NSNumber.class] || [d[@"id"] integerValue]<1)return;
            pointerAction=d[@"action"];pointerRequestId=[d[@"id"] integerValue];
        }else{
        if(![d[@"action"] isEqual:@"monitor-layout"])return;
        for(NSString *key in @[@"x",@"y",@"width",@"height",@"viewportWidth",@"viewportHeight"])
            if(![d[key] isKindOfClass:NSNumber.class] || !isfinite([d[key] doubleValue]))return;
        CGFloat vw=[d[@"viewportWidth"] doubleValue],vh=[d[@"viewportHeight"] doubleValue];
        CGFloat x=[d[@"x"] doubleValue],y=[d[@"y"] doubleValue],w=[d[@"width"] doubleValue],h=[d[@"height"] doubleValue];
        if(vw<1||vh<1||x<0||y<0||w<1||h<1||x+w>vw+1||y+h>vh+1)return;
        self.modularDock=YES;self.dockUnitRect=NSMakeRect(x/vw,y/vh,w/vw,h/vh);[self placeWorkspaceMonitor];return;
        }
    }
    if([message.body isEqual:@"toggle-monitor"]){[self toggleTV:nil];return;}
    if([message.body isEqual:@"dock-monitor"]){if(self.detached)[self toggleTV:nil];return;}
    if([message.body isEqual:@"fit-monitor"]){[self togglePixels:nil];return;}
    // Explicit Resume motion also restores the picture after sleep. Wake alone does not.
    if([message.body isEqual:@"resume"]){ [self resumeAfterSleep:nil]; return; }
    if([pointerAction isEqual:@"unlock"]){ if(self.mouseLocked && self.mouseRequestId==pointerRequestId) [self releaseMouse]; return; }
    if(![pointerAction isEqual:@"lock"] || self.mouseLocked) return;
    if(self.sessionSuspended || !NSApp.active || !self.window.keyWindow || CGAssociateMouseAndMouseCursorPosition(false)!=kCGErrorSuccess){
        [self.web evaluateJavaScript:[NSString stringWithFormat:@"window.heartPointer?.failed(%ld)",(long)pointerRequestId] completionHandler:nil]; return;
    }
    self.mouseLocked=YES; self.mouseRequestId=pointerRequestId; self.mouseX=self.mouseY=0; [NSCursor hide];
    NSLog(@"Pointer captured");
    [self.web evaluateJavaScript:[NSString stringWithFormat:@"window.heartPointer?.acquired(%ld)",(long)pointerRequestId] completionHandler:^(id value,NSError *error){if(error && self.mouseRequestId==pointerRequestId)[self releaseMouse];}];
}
- (void)mouseTick:(NSTimer *)timer {
    if(!self.mouseLocked || self.mousePending || (!self.mouseX && !self.mouseY)) return;
    NSEventModifierFlags f=self.mouseFlags;NSInteger requestId=self.mouseRequestId;
    NSString *js=[NSString stringWithFormat:@"window.heartPointer?.move(%f,%f,%@,%@,%@,%@,%ld)",self.mouseX,self.mouseY,
      (f & NSEventModifierFlagShift)?@"true":@"false",(f & NSEventModifierFlagOption)?@"true":@"false",
      (f & NSEventModifierFlagControl)?@"true":@"false",(f & NSEventModifierFlagCommand)?@"true":@"false",(long)requestId];
    self.mouseX=self.mouseY=0; self.mousePending=YES;
    [self.web evaluateJavaScript:js completionHandler:^(id value,NSError *error){self.mousePending=NO;if(error && self.mouseRequestId==requestId)[self releaseMouse];}];
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
- (void)reloadControls:(id)sender { [self releaseMouse];[self.web reload]; }
- (void)togglePixels:(id)sender { self.pixelMode=!self.pixelMode; }
- (void)tick:(NSTimer *)timer {
    if(self.sessionSuspended){
        self.frames=0;self.lastTick=0;[self.frameIntervals removeAllObjects];
        NSDictionary *metrics=@{@"timestamp":@(NSDate.date.timeIntervalSince1970),@"fps":@0,@"visible":@NO,@"suspended":@YES,@"width":@(self.width),@"height":@(self.height),@"mouse_locked":@(self.mouseLocked),@"intervals_ms":@[]};
        NSData *json=[NSJSONSerialization dataWithJSONObject:metrics options:0 error:nil];
        NSString *path=[[NSBundle.mainBundle.bundlePath stringByDeletingLastPathComponent] stringByAppendingPathComponent:@"telemetry.json"];
        [json writeToFile:path options:NSDataWritingAtomic error:nil];return;
    }
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
    BOOL visible=self.outputVisible;
    NSString *state=!visible?@"PAUSED · window covered":age>1?@"STALE — no new frame":@"LIVE · uncompressed GPU";
    NSString *gpu=self.gpuUsage;
    NSString *line=self.client ? [NSString stringWithFormat:@"%@   |   Output %.1f FPS   |   %lu × %lu   |   %@   |   %@",gpu,fps,self.width,self.height,self.pixelMode?@"1:1 pixels (crop)":@"Fit",state] : [NSString stringWithFormat:@"%@   |   Waiting for Arena · Composition Syphon output",gpu];
    NSString *displayLine=line;
    if(self.detached){
        NSString *compactGPU=[gpu stringByReplacingOccurrencesOfString:@" (Mac)" withString:@""];
        NSString *compactState=!visible?@"PAUSED":age>1?@"STALE":@"LIVE";
        displayLine=self.client ? [NSString stringWithFormat:@"%@ · %.1f FPS · %lu×%lu · %@ · %@",compactGPU,fps,self.width,self.height,self.pixelMode?@"1:1":@"Fit",compactState] : [NSString stringWithFormat:@"%@ · Waiting for Arena",compactGPU];
    }
    if(self.detached && self.monitorPanel.bounds.size.width<440 && self.client){
        displayLine=[NSString stringWithFormat:@"%@ %.0f FPS",!visible?@"PAUSED":age>1?@"STALE":@"●",fps];
    }
    if(self.modularDock&&!self.detached&&self.client)displayLine=[NSString stringWithFormat:@"%@ · %.0f FPS · %lu×%lu · %@",[gpu stringByReplacingOccurrencesOfString:@" (Mac)" withString:@""],fps,self.width,self.height,!visible?@"PAUSED":age>1?@"STALE":self.pixelMode?@"1:1":@"LIVE"];
    self.status.stringValue=displayLine;self.status.toolTip=line; NSLog(@"%@",line);
    NSDictionary *metrics=@{@"timestamp":@(NSDate.date.timeIntervalSince1970),@"fps":@(fps),@"visible":@(visible),@"detached":@(self.detached),@"width":@(self.width),@"height":@(self.height),@"gpu":gpu,@"mouse_locked":@(self.mouseLocked),@"intervals_ms":[self.frameIntervals copy]};
    NSData *json=[NSJSONSerialization dataWithJSONObject:metrics options:0 error:nil];
    NSString *path=[[NSBundle.mainBundle.bundlePath stringByDeletingLastPathComponent] stringByAppendingPathComponent:@"telemetry.json"];
    [json writeToFile:path options:NSDataWritingAtomic error:nil];
    [self.frameIntervals removeAllObjects];self.frames=0;
}
- (void)mtkView:(MTKView *)view drawableSizeWillChange:(CGSize)size {}
- (void)drawInMTKView:(MTKView *)view {
    if(self.sessionSuspended || !self.outputVisible || !self.client.isValid){self.lastAcquireTime=0;return;}
    if(dispatch_semaphore_wait(self.flight,DISPATCH_TIME_NOW)) return;
    BOOL fresh=self.client.hasNewFrame;
    id<MTLTexture> texture=[self.client newFrameImage];
    if(!texture){ dispatch_semaphore_signal(self.flight); return; }
    MTLRenderPassDescriptor *pass=view.currentRenderPassDescriptor;
    id<CAMetalDrawable> drawable=view.currentDrawable;
    if(!pass || !drawable){ dispatch_semaphore_signal(self.flight); return; }
    self.width=texture.width; self.height=texture.height;
    if(fresh){self.frames++; self.lastFrame=NSDate.timeIntervalSinceReferenceDate;
        if(self.lastAcquireTime>0)[self.frameIntervals addObject:@((self.lastFrame-self.lastAcquireTime)*1000.)];self.lastAcquireTime=self.lastFrame;}
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
- (void)applicationWillTerminate:(NSNotification *)notification {[self saveTVGeometry];[NSWorkspace.sharedWorkspace.notificationCenter removeObserver:self]; [self releaseMouse]; [NSEvent removeMonitor:self.mouseMonitor]; [self.client stop];}
@end
int main(int argc,const char **argv){@autoreleasepool{NSApplication *app=[NSApplication sharedApplication]; Heart *delegate=[Heart new]; app.delegate=delegate; [app run];}return 0;}
