# Heart native monitor

Open `Heart.app` with the Heart engine and Arena running, or run `Open Heart.command` to rebuild and open it. `sp/start.sh` now opens this window when starting the controller. The existing browser controller still works, but the GPU monitor lives in the native window.

The upper pane receives Arena's **Composition** Syphon output. Drag the divider to change its height. Fit preserves the aspect ratio; 1:1 maps source pixels to physical display pixels and crops the center when the pane is smaller than the source. The full source texture is received in either mode. Expand the window/pane to inspect more of the image. The lower pane is the existing Heart controller, with faders ordered from Arena's top layer to its bottom layer.

Frames go from Syphon's Metal texture through one GPU draw into the window. There is no JPEG encoding, CPU image readback, network video stream, or reduced-resolution intermediate. At most one monitor GPU command is in flight, so an overloaded monitor skips opportunities instead of building a queue of old frames. Source textures remain retained by the submitted command until it finishes. The monitor targets 60 Hz for the current 60 fps composition; it cannot recover frames Arena fails to produce or override the display refresh rate.

The counter measures newly acquired source frames per elapsed second, not Arena's internal FPS or display presentation timing. LIVE, STALE, and PAUSED distinguish new frames, interrupted delivery, and a fully covered/minimized window. Covered windows stop drawing. Disconnected clients are retried every second. Only Arena / Composition is selected, never another application's output.

The status bar labels that counter **Output FPS**. **GPU % (Mac)** is total device utilization across all applications, read once a second directly from the Apple GPU driver's registry statistics. It is not Arena-only utilization. If the driver does not expose this counter, the display says unavailable.

Mouse faders and parameter scrubs now use native pointer capture in this window. Click to grab; move to adjust; click again or press Escape to release. Capture prevents cursor movement across other controls and consumes clicks before they reach those controls. The trackpad FADERS/VARIATIONS grabs retain their existing Escape-to-release behavior. Switching apps/windows, navigating, or quitting releases capture as well. Capture failures cancel the gesture instead of leaving a false lock. Mouse movement is coalesced at 60 Hz with only one pending web delivery. This uses an application-local event monitor, with no global keyboard listener or new Accessibility permission.

Validation: native capture/release logged; Escape release checked; a click over the monitor Fit button while captured released the fader without activating Fit. Adapter regression checks cover acknowledgement, routing, release, late cancellation, and failure (`node sp/monitor/test_pointer.cjs`).

Initial visible-window checks on this machine received 1920 × 1080, usually 58–60 new frames/s (one observed one-second interval at 53). No end-to-end latency measurement or long show soak has been completed. Zero latency, guaranteed 60 fps under every shader load, HDR fidelity, and a colorimeter-verified match are not claimed. Fit necessarily resamples for the pane; use 1:1 for pixel inspection. The current renderer uses an SDR sRGB window and opaque RGB output for the current 8-bit composition.

Keep Arena running with Composition Syphon output enabled. Closing Heart does not quit Arena or stop the engine. Arena is still needed for composition editing and output configuration.

Build uses the installed Apple compiler and the Syphon framework already inside `sp/preview/.venv`. The app currently links to that local framework, so keep that environment in place; this is a local app, not a portable distribution.

References: [Syphon GPU sharing](https://syphon.info/) and [Apple MTKView](https://developer.apple.com/documentation/MetalKit/MTKView).
