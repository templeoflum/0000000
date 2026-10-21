// Hidden AppKit ownership test: no Syphon client, Metal device, visible windows, or wake actions.
#define main heart_application_main
#import "Heart.m"
#undef main
#include <assert.h>
@interface QuietHeart : Heart
@end
@implementation QuietHeart
- (NSRect)tvVisibleFrame {return NSMakeRect(0,0,1920,1080);}
- (NSArray<NSValue *> *)tvDisplayFrames {return @[[NSValue valueWithRect:self.tvVisibleFrame]];}
@end
@interface QuietWindow : HeartTVWindow
@end
@implementation QuietWindow
// Never load or save user geometry, even if production starts calling these on injected windows.
- (BOOL)setFrameAutosaveName:(NSWindowFrameAutosaveName)name {return NO;}
- (void)saveFrameUsingName:(NSWindowFrameAutosaveName)name {}
- (BOOL)setFrameUsingName:(NSWindowFrameAutosaveName)name {return NO;}
- (BOOL)setFrameUsingName:(NSWindowFrameAutosaveName)name force:(BOOL)force {return NO;}
- (NSRect)constrainFrameRect:(NSRect)frame toScreen:(NSScreen *)screen {return frame;}
- (void)makeKeyAndOrderFront:(id)sender {}
- (void)orderOut:(id)sender {}
- (void)setFrame:(NSRect)frame display:(BOOL)display animate:(BOOL)animate {[super setFrame:frame display:NO];}
- (BOOL)isVisible {return YES;}
- (NSWindowOcclusionState)occlusionState {return NSWindowOcclusionStateVisible;}
@end
@interface QuietControls : NSView
- (void)evaluateJavaScript:(NSString *)script completionHandler:(id)handler;
@end
@implementation QuietControls
- (void)evaluateJavaScript:(NSString *)script completionHandler:(id)handler {}
@end
int main(void){@autoreleasepool{
    [NSApplication sharedApplication];
    NSString *suite=[@"HeartMonitorTest." stringByAppendingString:NSUUID.UUID.UUIDString];
    NSUserDefaults *preferences=[[NSUserDefaults alloc] initWithSuiteName:suite];
    Heart *h=[QuietHeart new];h.tvPreferences=preferences;
    h.window=[[QuietWindow alloc] initWithContentRect:NSMakeRect(0,0,1200,800) styleMask:NSWindowStyleMaskTitled backing:NSBackingStoreBuffered defer:YES];
    h.tvWindow=[[QuietWindow alloc] initWithContentRect:NSMakeRect(0,0,320,250) styleMask:NSWindowStyleMaskTitled backing:NSBackingStoreBuffered defer:YES];
    h.window.restorable=NO;h.tvWindow.restorable=NO;
    assert(h.window.frameAutosaveName.length==0 && h.tvWindow.frameAutosaveName.length==0);
    [h loadTVGeometry];assert(h.tvSmallFrame.size.width==320 && h.tvLargeFrame.size.width==640);
    h.tvWindow.contentView=[[HeartTVFrame alloc] initWithFrame:NSMakeRect(0,0,320,250)];
    h.split=[[NSSplitView alloc] initWithFrame:h.window.contentView.bounds];h.split.vertical=NO;[h.window.contentView addSubview:h.split];
    h.monitorPanel=[[HeartMonitorPanel alloc] initWithFrame:NSMakeRect(0,0,1200,320)];
    // A plain NSView tests window ownership without initializing GPU resources.
    h.view=(MTKView *)[[NSView alloc] initWithFrame:NSMakeRect(0,0,1200,264)];[h.monitorPanel addSubview:h.view];
    h.web=(WKWebView *)[[QuietControls alloc] initWithFrame:NSMakeRect(0,0,1200,480)];
    [h.split addSubview:h.monitorPanel];[h.split addSubview:h.web];
    h.dockButton=[NSButton new];h.dockButton.tag=5;h.topButton=[NSButton new];h.topButton.tag=6;
    h.resumeButton=[NSButton new];h.resumeButton.tag=4;h.resumeButton.hidden=YES;
    NSButton *fit=[NSButton new];fit.tag=3;fit.target=h;fit.action=@selector(togglePixels:);
    for(NSButton *button in @[h.dockButton,h.topButton,h.resumeButton,fit])[h.monitorPanel addSubview:button];
    NSRect initialGeometry=h.tvWindow.frame;
    NSView *original=h.view;h.sessionSuspended=YES;
    [h toggleTV:nil];
    assert(h.tvWindow.canBecomeKeyWindow && !h.tvWindow.canBecomeMainWindow);
    assert(h.monitorPanel.tvMode);
    for(NSButton *button in @[h.dockButton,h.topButton,h.resumeButton,fit])assert(button.superview==h.tvWindow.contentView);
    assert(fit.target==h && fit.action==@selector(togglePixels:) && fit.focusRingType==NSFocusRingTypeNone);
    assert(NSEqualRects(initialGeometry,h.tvWindow.frame));
    assert(h.detached && h.view==original && h.view.window==h.tvWindow && h.outputVisible);
    assert(h.sessionSuspended && !h.client && h.split.subviews.count==1);
    [h toggleTop:nil];assert(h.tvWindow.level==NSFloatingWindowLevel);
    [h toggleTop:nil];assert(h.tvWindow.level==NSNormalWindowLevel);
    NSRect small=h.tvWindow.frame;
    [h expandTV:nil];assert(h.tvLarge && NSEqualRects(h.tvSmallFrame,small));
    assert(h.tvWindow.frame.size.width>=small.size.width);
    [h expandTV:nil];assert(!h.tvLarge && NSEqualRects(h.tvWindow.frame,small));
    assert(h.sessionSuspended && h.view==original);
    [h expandTV:nil];
    NSRect customLarge=NSMakeRect(140,80,777,444);[h.tvWindow setFrame:customLarge display:NO animate:NO];
    [h expandTV:nil];assert(!h.tvLarge && NSEqualRects(h.tvWindow.frame,small));
    [h expandTV:nil];assert(h.tvLarge && NSEqualRects(h.tvWindow.frame,customLarge));
    [h expandTV:nil];NSRect customSmall=NSMakeRect(600,300,340,260);[h.tvWindow setFrame:customSmall display:NO animate:NO];
    [h saveTVGeometry];
    Heart *reload=[QuietHeart new];reload.tvPreferences=preferences;[reload loadTVGeometry];
    assert(NSEqualRects(reload.tvSmallFrame,customSmall) && NSEqualRects(reload.tvLargeFrame,customLarge));
    assert(NSEqualRects([reload reachableTVFrame:customSmall],customSmall));
    NSRect recovered=[reload reachableTVFrame:NSMakeRect(9000,9000,340,260)];assert(NSIntersectsRect(recovered,reload.tvVisibleFrame));
    [h toggleTV:nil];
    NSRect docked=h.tvWindow.frame;[h expandTV:nil];assert(NSEqualRects(h.tvWindow.frame,docked));
    assert(!h.monitorPanel.tvMode);
    for(NSButton *button in @[h.dockButton,h.topButton,h.resumeButton,fit])assert(button.superview==h.monitorPanel);
    assert(fit.focusRingType==NSFocusRingTypeDefault);
    NSRect beforeRedetach=h.tvWindow.frame;[h toggleTV:nil];
    assert(((HeartTVFrame *)h.tvWindow.contentView).screenPanel==h.monitorPanel && fit.superview==h.tvWindow.contentView);
    assert(NSEqualRects(beforeRedetach,h.tvWindow.frame));[h toggleTV:nil];
    assert(!h.detached && h.view==original && h.view.window==h.window && h.outputVisible);
    assert(h.sessionSuspended && !h.client && h.split.subviews.count==2);
    assert([h windowShouldClose:h.tvWindow]==NO);
    assert(h.split.subviews.firstObject==h.monitorPanel && h.split.subviews.lastObject==h.web);
    h.modularDock=YES;h.dockUnitRect=NSMakeRect(.25,.20,.40,.35);
    [h placeWorkspaceMonitor];
    assert(h.monitorPanel.superview==h.window.contentView && h.split.subviews.count==1);
    assert(h.monitorPanel.compactDock && h.view==original && fit.hidden);
    assert(h.monitorPanel.frame.size.width>0 && h.monitorPanel.frame.size.width<h.window.contentView.bounds.size.width);
    [h toggleTV:nil];assert(h.detached && !fit.hidden && fit.superview==h.tvWindow.contentView);
    [h toggleTV:nil];assert(!h.detached && h.monitorPanel.superview==h.window.contentView && h.monitorPanel.compactDock);
    assert(h.view==original && h.sessionSuspended && fit.hidden);
    [preferences removePersistentDomainForName:suite];
    puts("TV checks passed: single view moved and docked, visibility follows its window, on-top toggles, independent saved geometries, offscreen recovery, enlarge/restore, docked double-click ignored, suspension preserved.");
}return 0;}
