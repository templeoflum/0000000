#import <Foundation/Foundation.h>
#import <CoreMIDI/CoreMIDI.h>
int main(){@autoreleasepool{for(ItemCount i=0;i<MIDIGetNumberOfSources();i++){MIDIEndpointRef e=MIDIGetSource(i);CFStringRef n=NULL;MIDIObjectGetStringProperty(e,kMIDIPropertyDisplayName,&n);printf("MIDI source %lu: %s\n",(unsigned long)i,n?[(__bridge NSString*)n UTF8String]:"unknown");if(n)CFRelease(n);}printf("Sources: %lu\n",(unsigned long)MIDIGetNumberOfSources());}return 0;}
