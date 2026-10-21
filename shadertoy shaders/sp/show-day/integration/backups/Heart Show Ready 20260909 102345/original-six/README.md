# Original shader performance batch

Six existing Field sources: live Home targets, two driven parameters, bounded sampled values, Home recovery (drives off + target values), and actual Home/Open output reviewed. No shader/wrapper installation or modification. Factory Home/Open profiles live in the existing sweetspots.json mechanism.

Use Field → All sources and search the name. Normal Home can respect a user-saved Home; factory recovery was tested explicitly. Home is a settled visual state; source-internal clocks may still run.

|Source|Column|Open motion|
|---|---:|---|
|Cuadricula rect|17|warp, rotate|
|data blocks|18|shift, density|
|RailroadTracks|28|curve1, intensity|
|RetroTechnicolorComputer|31|hue, saturation|
|SmoothXORi|32|intensity, tint|
|TruchetDualLevelSpin|33|thickness, glow|

Validation: six live cycles passed; contact.jpg shows actual Arena output, not only thumbnails. Brief motion samples do not certify sustained frame rate or every possible setting. The source-specific Open helper regression tests passed. New corpus wrappers remain quarantined separately.
