# Idle GPU and Reconnect

Reconnect button added beside connection status. It drops the Arena socket,
clears stale queued writes, and requests fresh parameter discovery. Live check
observed disconnected then connected, with H continuing 24.391 → 24.666.
14 engine checks passed. No clips active during these checks.

System AGX Device Utilization samples: 12 readings at approximately 0.5 s per
condition. Conditions sequential, uncontrolled background activity, occasional
zero readings; differences are not reliable per-process cost estimates.

- Heart open: mean 59.6%, range 51–71.
- Heart closed (engine running): mean 51.3%, range 0–73.
- Wire temporarily paused, Heart open: mean 43%, range 0–49.
- Wire resumed: mean 43.7%, range 0–57.
- Arena temporarily paused: mean 47.4%, range 0–57.
- GOG Galaxy temporarily paused: mean 39.8%, range 0–55.
- All resumed: mean 41.8%, range 0–63.

All temporarily paused processes resumed in finally blocks. Heart reopened.
No active composition clips; non-Transform effects bypassed; Heart queue empty
and engine worst work around 0.1 ms. Significant GPU utilization remains with
Heart closed and with Arena paused. Counter is Mac-wide, not Arena or Heart GPU
usage. Process attribution unresolved; powermetrics requires administrator
access unavailable without a password. No shader-quality changes made.

Feedback Machine reviewed from saved feedback machine_16x9_1080p.avc only.
Not opened over the current composition, and no effects imported. Separate
fill/color/motion/base feedback group, object/background/text processing, and
composition effects. Base layer contains named directional rotate/scale/move
feedback clips, useful candidates for semantic gesture presets in Heart.
