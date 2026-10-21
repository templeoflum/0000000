# Heart workshop progress

Open http://localhost:8765/progress while Heart is running. Read-only, same existing Heart server, no separate service or performance websocket. Fetches progress.json every five seconds while visible; does not repaint unchanged work data. Search and status filters stay selected across updates. Disconnected state retains the last successful update, with the actual work timestamp visible.

Source files: sp/engine/progress.html and progress.json. Dashboard routes are explicitly allowlisted in Heart; no general file browsing.

Update during work with the publisher:

    sp/engine/.venv/bin/python sp/audit/shader-progress/update.py 'What is happening now' --phase 'Working'

A record uses the exact census identity, e.g. --record '{"id":"D1 L5C20","status":"Blocked","sampled":true,"note":"Scale clips the frame; needs source adaptation."}'. Allowed UI statuses: Untested, Checking, Sampled, Blocked. Blocked means that clip needs work for the intended role, not that the whole project has stopped. Set sampled true only after actual rendered review. Enrollment and testing remain separate. Do not mark untested duplicates as tested. Append new clip entries to the canonical coverage.json before publishing them.

Publisher reads the batch1 coverage ledger and preserves explicit per-clip overrides. It writes atomically. Update at check start, after real findings, and at the end of a work session; use a truthful phase such as 'Batch complete' instead of leaving 'Working' after stopping. This is a progress display, not an autonomous scheduler.

Checked live in the Codex browser: page rendered all 282 initial rows, correct 208 enrolled / 9 sampled counts, work timestamp, current activity, and filter/search controls. Current corpus grows as adapted copies are added.
