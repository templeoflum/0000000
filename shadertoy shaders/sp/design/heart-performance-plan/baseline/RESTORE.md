# Recovery baseline

The original Documents composition was not overwritten. `live-saved.avc` captures the live state at the beginning of this build; `generative soup_16x9_1920x1080_60fps.avc` is the previously saved original. `Heart Performance.avc` in the parent directory is the working copy with four staged bypassed feedback effects.

`engine/` contains pre-build engine code/settings; `manifest.json` records their hashes. To roll back, stop only Heart, restore the desired engine files/settings from this directory, then launch `sp/start.sh`. Do not copy the baseline directory over running settings indiscriminately: preserve any subsequent user edits first. Open the desired composition through Resolume after the Mac is unlocked and its pending open state has been inspected.

The build saved a diagnostic patch `sp/engine/patches/Connection check.*`; it is not the finished Start patch. Its snapshot-open request timed out while the Mac was locked. Do not treat that timeout as proof of success or retry blindly.
