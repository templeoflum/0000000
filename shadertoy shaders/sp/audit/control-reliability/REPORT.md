# Manual-control reliability repair

Heart manual edits could interleave with clip refresh and motion output. Clip refresh and manual edits now share the existing motion lock. Explicit manual gestures stop the drive, finish the transition, and invalidate the output cache so repeating a value really retries it. No new generator system was introduced.

Evidence: baseline 98/100 live manual changes accepted at the requested native value; both misses persisted after another 0.5 seconds. Direct transport isolation passed 50/50 WebSocket and 50/50 HTTP writes. After the repair and a Heart-only restart, 100/100 live manual changes passed. Arena was not restarted. The full Python suite passed 212 tests, including four new regression checks for refresh ordering, explicit retries, transition completion and stale targets.

This is evidence of improved manual reliability, not exhaustive acceptance of all control paths. Narrow-range configuration after transitions remains a separate follow-up. Raw before/after and transport results are beside this report.
