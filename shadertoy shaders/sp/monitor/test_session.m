// Exercise notification handling without putting the Mac to sleep or waking it.
#define main heart_application_main
#import "Heart.m"
#undef main
#include <assert.h>
int main(void) { @autoreleasepool {
    Heart *h=[Heart new];
    [h suspendForSession:[NSNotification notificationWithName:NSWorkspaceWillSleepNotification object:nil]];
    assert(h.sessionSuspended && h.systemSleeping && !h.mouseLocked && !h.client);
    [h suspendForSession:[NSNotification notificationWithName:NSWorkspaceSessionDidResignActiveNotification object:nil]];
    [h sessionReturned:[NSNotification notificationWithName:NSWorkspaceDidWakeNotification object:nil]];
    assert(!h.systemSleeping && h.sessionInactive && h.sessionSuspended);
    [h resumeAfterSleep:nil]; assert(h.sessionSuspended);
    [h sessionReturned:[NSNotification notificationWithName:NSWorkspaceSessionDidBecomeActiveNotification object:nil]];
    assert(!h.sessionInactive && h.sessionSuspended);
    [h suspendForSession:[NSNotification notificationWithName:NSWorkspaceScreensDidSleepNotification object:nil]];
    [h sessionReturned:[NSNotification notificationWithName:NSWorkspaceScreensDidWakeNotification object:nil]];
    assert(!h.displaySleeping && h.sessionSuspended);
    puts("Session checks passed: release, suspend, independent wake flags, no automatic resume.");
} return 0; }
