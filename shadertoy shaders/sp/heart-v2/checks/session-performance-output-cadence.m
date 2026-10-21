#import <Foundation/Foundation.h>
#import <Metal/Metal.h>
#import <Syphon/Syphon.h>
#import <mach/mach_time.h>

static double monotonic(void) {
    static mach_timebase_info_data_t info;
    if (!info.denom) mach_timebase_info(&info);
    return mach_continuous_time() * (double)info.numer / info.denom / 1e9;
}
static void service(double until) {
    while (monotonic() < until)
        [[NSRunLoop mainRunLoop] runUntilDate:[NSDate dateWithTimeIntervalSinceNow:0.01]];
}
static double percentile(NSArray<NSNumber *> *values, double q) {
    if (!values.count) return 0;
    double index=(values.count-1)*q; NSUInteger lo=(NSUInteger)floor(index), hi=(NSUInteger)ceil(index);
    return values[lo].doubleValue + (values[hi].doubleValue-values[lo].doubleValue)*(index-lo);
}
int main(int argc, const char **argv) {
    @autoreleasepool {
        double duration=argc>1?atof(argv[1]):20.0;
        double warmup=argc>2?atof(argv[2]):2.0;
        if(duration<1 || duration>3600 || warmup<0 || warmup>60) { fprintf(stderr,"usage: output-cadence [seconds 1..3600] [warmup 0..60]\n"); return 2; }
        SyphonServerDirectory *directory=[SyphonServerDirectory sharedDirectory];
        NSDictionary *server=nil;
        double timeout=monotonic()+5;
        while (!server && monotonic()<timeout) {
            for (NSDictionary *s in directory.servers)
                if ([s[SyphonServerDescriptionAppNameKey] containsString:@"Arena"] && [s[SyphonServerDescriptionNameKey] isEqualToString:@"Composition"]) { server=s; break; }
            if (!server) service(monotonic()+.05);
        }
        if (!server) { fprintf(stderr,"No Arena Composition Syphon server found. No native settings changed.\n"); return 3; }
        id<MTLDevice> device=MTLCreateSystemDefaultDevice();
        if (!device) { fprintf(stderr,"No Metal device available.\n"); return 4; }
        NSLock *lock=[NSLock new]; NSMutableArray<NSNumber *> *times=[NSMutableArray new];
        __block double start=0, end=0; __block NSUInteger callbacks=0, nilTextures=0, width=0, height=0;
        SyphonMetalClient *client=[[SyphonMetalClient alloc] initWithServerDescription:server device:device options:nil newFrameHandler:^(SyphonMetalClient *c) {
            @autoreleasepool {
                double now=monotonic();
                // Acquire the shared texture handle only. No output pixel copy, draw, or GPU submission.
                id<MTLTexture> texture=[c newFrameImage];
                [lock lock];
                if (start && now>=start && now<end) {
                    callbacks++;
                    if (texture) { [times addObject:@(now-start)]; width=texture.width; height=texture.height; }
                    else nilTextures++;
                }
                [lock unlock];
            }
        }];
        if (!client || !client.isValid) { fprintf(stderr,"Arena Composition Syphon client is invalid.\n"); return 5; }
        service(monotonic()+warmup);
        [lock lock]; start=monotonic(); end=start+duration; [lock unlock];
        service(end);
        [client stop];
        [lock lock]; NSArray<NSNumber *> *recorded=[times copy]; [lock unlock];
        NSMutableArray<NSNumber *> *intervals=[NSMutableArray new], *bins=[NSMutableArray new];
        for (NSUInteger i=1;i<recorded.count;i++) [intervals addObject:@((recorded[i].doubleValue-recorded[i-1].doubleValue)*1000)];
        for (int i=0;i<(int)floor(duration);i++) {
            NSUInteger count=0; for (NSNumber *t in recorded) if (t.doubleValue>=i && t.doubleValue<i+1) count++;
            [bins addObject:@(count)];
        }
        NSArray<NSNumber *> *sorted=[intervals sortedArrayUsingSelector:@selector(compare:)];
        NSArray<NSNumber *> *sortedBins=[bins sortedArrayUsingSelector:@selector(compare:)];
        NSUInteger over25=0, over34=0, over50=0, over100=0;
        for (NSNumber *i in intervals) { double v=i.doubleValue; if(v>25)over25++; if(v>34)over34++; if(v>50)over50++; if(v>100)over100++; }
        NSDictionary *report=@{
          @"method":@"Syphon new-frame notifications with shared Metal texture acquisition; no pixel readback or GPU draw",
          @"server":@{@"app":server[SyphonServerDescriptionAppNameKey]?:@"", @"name":server[SyphonServerDescriptionNameKey]?:@""},
          @"timestamp_utc":[NSISO8601DateFormatter.new stringFromDate:NSDate.date], @"duration_s":@(duration), @"warmup_s":@(warmup),
          @"width":@(width), @"height":@(height), @"frames":@(recorded.count), @"callbacks":@(callbacks), @"nil_textures":@(nilTextures),
          @"fps":@(recorded.count/duration), @"one_second_fps":bins,
          @"one_second_fps_min":sortedBins.firstObject?:@0, @"one_second_fps_p05":@(percentile(sortedBins,.05)),
          @"interval_ms":@{@"median":@(percentile(sorted,.5)), @"p95":@(percentile(sorted,.95)), @"p99":@(percentile(sorted,.99)), @"max":sorted.lastObject?:@0},
          @"gaps_over_ms":@{@"25":@(over25), @"34":@(over34), @"50":@(over50), @"100":@(over100)},
          @"frame_times_s":recorded,
          @"limits":@"Measures published composition frame cadence, including Syphon delivery scheduling. Does not count repeated pixels, isolate GPU render cost, or verify projector/display presentation."
        };
        NSData *data=[NSJSONSerialization dataWithJSONObject:report options:NSJSONWritingPrettyPrinted|NSJSONWritingSortedKeys error:nil];
        fwrite(data.bytes,1,data.length,stdout); fputc('\n',stdout);
        return recorded.count?0:6;
    }
}
