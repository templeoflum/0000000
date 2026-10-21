#import <Foundation/Foundation.h>
#import <ApplicationServices/ApplicationServices.h>
int main(int argc,const char **argv){@autoreleasepool{
 if(argc<2)return 2;NSString *cmd=@(argv[1]);
 if([cmd isEqual:@"windows"]){
  NSArray *ws=CFBridgingRelease(CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly,kCGNullWindowID));NSMutableArray *result=[NSMutableArray new];
  for(NSDictionary *w in ws)if([@[@"Heart",@"Arena"] containsObject:w[(id)kCGWindowOwnerName]])[result addObject:w];
  NSData *data=[NSJSONSerialization dataWithJSONObject:result options:0 error:nil];puts([[NSString alloc]initWithData:data encoding:NSUTF8StringEncoding].UTF8String);return 0;
 }
 if([cmd isEqual:@"click"]&&argc==4){CGPoint p=CGPointMake(atof(argv[2]),atof(argv[3]));
  CGEventRef a=CGEventCreateMouseEvent(NULL,kCGEventLeftMouseDown,p,kCGMouseButtonLeft),b=CGEventCreateMouseEvent(NULL,kCGEventLeftMouseUp,p,kCGMouseButtonLeft);CGEventPost(kCGHIDEventTap,a);CGEventPost(kCGHIDEventTap,b);CFRelease(a);CFRelease(b);return 0;}
 if([cmd isEqual:@"escape"]){CGEventRef a=CGEventCreateKeyboardEvent(NULL,53,true),b=CGEventCreateKeyboardEvent(NULL,53,false);CGEventPost(kCGHIDEventTap,a);CGEventPost(kCGHIDEventTap,b);CFRelease(a);CFRelease(b);return 0;}
 return 2;
}}
