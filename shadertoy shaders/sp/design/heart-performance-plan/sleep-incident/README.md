# Sleep/wake incident — September 7, 2026

Live performance testing paused after user reported lid-close/reopen failure requiring remote force-quit of ChatGPT and restart.

## Verified evidence

- Power log records 58 full Sleep entries with reason `Thermal Emergency Sleep` between 15:48:26 and 15:54:02 CDT. Additional DarkWake entries accompany them. Several full wakes lasted only two seconds.
- ChatGPT PID 97783 held an Electron NoIdleSleepAssertion during the incident. Arena held NDI idle-sleep and intermittent JUCE display-sleep assertions. These identify requests, not per-process heat or causality.
- A five-second caffeinate UserIsActive request at 15:52:42 expired at 15:52:48. A second short request appears at 15:53:01 and expired at 15:53:03. Thermal sleep began before both. One explicit five-second command was issued by this assistant after black screenshots; the second request's initiator is not established by this log.
- CUA's automatic unlock failed and reported a locked Mac; that report was insufficient to diagnose the actual thermal sleep loop.
- Reboot occurred at approximately 15:55:02. Post-restart ChatGPT still holds an Electron idle-sleep assertion. No caffeinate assertion remained in the captured current assertions.
- Current thermal status could not be read through pmset; do not infer a temperature or hardware failure.

## Assessment

Immediate sleep reason is confirmed; underlying cause is unresolved. Possibilities include sustained workload/heat and power-management or sensor behavior. Killing ChatGPT helping recovery makes it relevant but does not alone establish it as the source. No evidence establishes that Heart mouse capture caused the sleep loop.

## Session operating rule, effective immediately

Do not issue wake commands or automatic screen-control retries after unexpected display loss, lid close, or thermal-sleep evidence. Pause live GPU tests and local model jobs. Read power logs before diagnosing a lock. Resume interactive tests only after the user confirms the machine is stable. Do not alter macOS sleep/security/thermal protection settings to work around this failure.

Before continuing release testing, audit Heart sleep/session-inactive handling and ensure input capture releases and rendering/control work suspends appropriately. This is a required follow-up, not a completed fix. App keep-awake configuration and safe transport procedure also need review. Preserve these local logs for a support report; nothing has been sent externally.
