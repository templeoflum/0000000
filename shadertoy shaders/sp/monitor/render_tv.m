// Offline static rendering only: no application delegate launch, Metal device, Syphon client,
// visible window, preferences, timer, or live UI action.
#define main heart_application_main
#import "Heart.m"
#undef main
#include <assert.h>
@interface MockPicture : NSView
@end
@implementation MockPicture
// Reuse production panel geometry without constructing an MTKView/device.
- (BOOL)isKindOfClass:(Class)cls {return cls==MTKView.class || [super isKindOfClass:cls];}
- (void)drawRect:(NSRect)rect {
    [[NSColor blackColor] setFill];NSRectFill(self.bounds);
    CGFloat w=self.bounds.size.width,h=self.bounds.size.height;
    NSRect picture=NSMakeRect(0,0,w,w*9/16.);if(picture.size.height>h){picture.size.height=h;picture.size.width=h*16/9.;}picture.origin=NSMakePoint((w-picture.size.width)/2,(h-picture.size.height)/2);
    [NSGraphicsContext saveGraphicsState];NSRectClip(picture);
    [[NSColor colorWithWhite:.13 alpha:1] setFill];NSRectFill(picture);
    [[NSColor colorWithWhite:.27 alpha:1] setStroke];
    for(int i=0;i<14;i++){CGFloat x=picture.origin.x+picture.size.width*i/13.;NSBezierPath *line=[NSBezierPath bezierPath];[line moveToPoint:NSMakePoint(x,picture.origin.y)];[line lineToPoint:NSMakePoint(x,NSMaxY(picture))];[line stroke];}
    for(int i=0;i<9;i++){CGFloat y=picture.origin.y+picture.size.height*i/8.;NSBezierPath *line=[NSBezierPath bezierPath];[line moveToPoint:NSMakePoint(picture.origin.x,y)];[line lineToPoint:NSMakePoint(NSMaxX(picture),y)];[line stroke];}
    CGFloat d=picture.size.height*.65;
    NSBezierPath *circle=[NSBezierPath bezierPathWithOvalInRect:NSMakeRect(NSMidX(picture)-d/2,NSMidY(picture)-d/2,d,d)];[[NSColor colorWithWhite:.8 alpha:1] setStroke];circle.lineWidth=1.4;[circle stroke];
    [NSGraphicsContext restoreGraphicsState];
}
@end
static void render(NSSize size, NSString *path, BOOL pressed, BOOL resuming){
    HeartTVWindow *window=[[HeartTVWindow alloc] initWithContentRect:(NSRect){NSZeroPoint,size} styleMask:NSWindowStyleMaskBorderless backing:NSBackingStoreBuffered defer:YES];window.releasedWhenClosed=NO;window.restorable=NO;
    window.appearance=[NSAppearance appearanceNamed:NSAppearanceNameDarkAqua];
    HeartTVFrame *frame=[[HeartTVFrame alloc] initWithFrame:(NSRect){NSZeroPoint,size}];window.contentView=frame;
    HeartMonitorPanel *panel=[[HeartMonitorPanel alloc] initWithFrame:NSZeroRect];panel.tvMode=YES;frame.screenPanel=panel;[frame addSubview:panel];
    [panel addSubview:[[MockPicture alloc] initWithFrame:NSZeroRect]];
    HeartReadout *readout=[HeartReadout labelWithString:size.width<440?@"● 60 FPS":@"GPU 42% · 60.0 FPS · 1920×1080 · Fit · LIVE"];
    readout.tag=2;readout.font=[NSFont monospacedSystemFontOfSize:11 weight:NSFontWeightRegular];readout.textColor=[NSColor colorWithCalibratedRed:.90 green:.89 blue:.84 alpha:1];readout.lineBreakMode=NSLineBreakByTruncatingTail;[panel addSubview:readout];
    NSArray *titles=@[@"Fit / 1:1",@"Resume",@"Dock",@"Pin ●"];
    for(NSUInteger i=0;i<titles.count;i++){
        NSButton *button=[NSButton new];button.tag=i+3;button.cell=[[HeartPhysicalButtonCell alloc] initTextCell:titles[i]];[button setButtonType:NSButtonTypeMomentaryPushIn];button.bezelStyle=NSBezelStyleSmallSquare;button.focusRingType=NSFocusRingTypeNone;button.hidden=i==1&&!resuming;button.cell.highlighted=pressed&&i==0;[frame addSubview:button];
    }
    [frame resizeSubviewsWithOldSize:NSZeroSize];[panel resizeSubviewsWithOldSize:NSZeroSize];[frame layoutSubtreeIfNeeded];
    NSBitmapImageRep *bitmap=[[NSBitmapImageRep alloc] initWithBitmapDataPlanes:NULL pixelsWide:size.width*2 pixelsHigh:size.height*2 bitsPerSample:8 samplesPerPixel:4 hasAlpha:YES isPlanar:NO colorSpaceName:NSDeviceRGBColorSpace bytesPerRow:0 bitsPerPixel:0];bitmap.size=size;
    [frame cacheDisplayInRect:frame.bounds toBitmapImageRep:bitmap];
    assert([[bitmap representationUsingType:NSBitmapImageFileTypePNG properties:@{}] writeToFile:path atomically:YES]);
    printf("%s\n",path.UTF8String);
}
int main(int argc,const char **argv){@autoreleasepool{[NSApplication sharedApplication];BOOL pressed=NO,resuming=NO;
    for(int i=1;i<argc;i++){pressed|=!strcmp(argv[i],"pressed");resuming|=!strcmp(argv[i],"resume");}
    NSString *suffix=resuming?@"-resume":pressed?@"-pressed":@"";
    render(NSMakeSize(320,250),[NSString stringWithFormat:@"/tmp/heart-monitor-small%@.png",suffix],pressed,resuming);
    render(NSMakeSize(640,430),[NSString stringWithFormat:@"/tmp/heart-monitor-large%@.png",suffix],pressed,resuming);
    if(resuming)render(NSMakeSize(280,220),@"/tmp/heart-monitor-min-resume.png",NO,YES);
}return 0;}
