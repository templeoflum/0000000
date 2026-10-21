# Using Heart

Double-click **Open Heart** on the Desktop or in ~/Applications. You can drag
Open Heart from Applications to the Dock for permanent access.

Heart is a controller and monitor for Resolume, not a separate renderer:

- Resolume Arena runs the composition, shaders, effects, and final output.
- The Heart engine sends parameter motion and receives composition information
  through Arena's local Web Server (port 8080).
- The native Heart window displays Arena's Composition Syphon output through
  Metal, with the local control page underneath. Video does not pass through the
  web page or a JPEG stream. Fit scales the display; 1:1 shows source pixels.
- A separate trackpad helper reads touch input for the performance controls.

Open Heart starts missing helpers and opens the native window. Reopening it
reuses running helpers, preserving their current motion. On a fresh start it
attempts to launch Arena in the background and waits for its control connection.
Arena must have the desired composition loaded, Web Server enabled on port 8080,
and Composition Syphon output enabled for video. A startup failure shows a dialog.

Closing or quitting the Heart window does not stop Arena or Heart's background
motion engine. Use Hold motion in Heart to freeze parameter motion before closing
if desired. Reopen the launcher to return to the controls.

The launcher uses this project's existing installation, including its Python
runtimes and Syphon framework. It is not a portable standalone app: moving or
renaming the project folder requires updating/reinstalling the launcher.

Implementation: sp/launch.py. sp/start.sh and monitor/Open Heart.command use the
same startup path. The Desktop item is a copy of the launcher with an explicit Finder icon;
~/Applications/Open Heart.app is also installed.
Verified repeated launches keep the existing engine, trackpad helper, and monitor
processes. A full cold start was not tested by stopping the active performance.


After sleep or switching login sessions, Heart releases the pointer and pauses its monitor and parameter motion. Click **Resume motion** in the controller to resume both. **Resume monitor** resumes the picture alone, keeping parameter motion held. Waking the Mac alone does not resume Heart; no wake commands or sleep-prevention settings are installed. Resolume can continue rendering independently.


## Starting and recalling a performance

**Start: Feedback checked** restores the reviewed feedback setup, including its clips, levels, routing, effects and motion relationships. The original patch named Start remains available in the chooser. Select another saved patch and click **Use as Start** to change the Start target without loading it. If the selected Start patch is missing, Heart shows that clearly and disables Start.

**Recall** loads the patch selected in the chooser. Watch the status: checking dependencies, opening, restoring layers, verifying routing, resolving controls, applying motion, then Ready. Wait for Ready before performing. A failed verification reports attention rather than silently accepting the wrong routing. Saving a patch preserves controllable settings; it does not capture live feedback pixels.

**Motion Home** restores the selected instrument's motion settings. **Hold motion** stops Heart's parameter animation; it does not freeze shader time or feedback evolution. **Reset trails** clears the feedback instrument's stored trails. These are separate actions.

The feedback layer includes Invert RGB, Blur and Sharpen plus a linked Blur + Sharpen action. They start bypassed in the checked patch. Their detailed controls are available from the effect's settings button. These output effects are separate from Loop Invert and Loop Detail inside the feedback history.
