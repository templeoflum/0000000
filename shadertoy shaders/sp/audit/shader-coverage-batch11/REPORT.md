# Coverage batch 11

Remaining Field coverage completed: 18 continuous-control samples and 3 choice-control samples. No shader files edited or clip placement changed.

36/36 initial manual targets passed; all 18 native drives varied. Six discrete selections passed across the two Gradient clips and Static. Full output captures reviewed. SP Field stays white; Color Wheel goes black during warp. Other continuous samples show visible differences, including full-white Lines at one sampled setting.

Checkered was probed manually at actual counts 8 and 32. Both read back correctly. Driven samples exceeded that requested range during short config transitions; do not interpret this as passing settled range behavior.

| Clip | Source | Probe | Follow-up |
|---|---|---|---|
| L3C1 | SP Atom Ground | Scale | Further parameter audit |
| L3C2 | SP Atom Room | Scale | Further parameter audit |
| L3C3 | SP Atom Void | Density | Further parameter audit |
| L3C8 | SP Field | Scale | Both captures solid white despite Scale readback changes; visible response not verified. |
| L3C92 | Gentle Rings SP | Ring | Further parameter audit |
| L3C94 | Color Wheel | warp | Warp test transitions from visible color wheel to black capture; useful range/setup needs investigation. |
| L3C95 | Sine Wave | Amplitude | Further parameter audit |
| L3C96 | Gentle Rings SP | Ring | Further parameter audit |
| L3C97 | Checkered | Num X | 8 and 32 cells accepted manually; driven samples exceeded requested 8–32 range. Config transition/range behavior not certified. |
| L3C98 | Spiral | Distortion | Further parameter audit |
| L3C99 | Lines | Width | Width test fills output white in second frame; useful range needs tuning. |
| L3C101 | Lines | Width | Width test fills output white in second frame; useful range needs tuning. |
| L3C102 | Rings | Spacing | Further parameter audit |
| L3C103 | Spiral | Distortion | Further parameter audit |
| L3C104 | Checkered | Num X | 8 and 32 cells accepted manually; driven samples exceeded requested 8–32 range. Config transition/range behavior not certified. |
| L3C105 | Sine Wave | Amplitude | Further parameter audit |
| L3C107 | Checkered | Num X | 8 and 32 cells accepted manually; driven samples exceeded requested 8–32 range. Config transition/range behavior not certified. |
| L3C108 | Spiral | Distortion | Further parameter audit |
| L3C93 | Gradient | Type (choice) | Choice-only sample |
| L3C100 | Gradient | Type (choice) | Choice-only sample |
| L3C106 | Static | Mode (choice) | Choice-only sample |

Test drives stopped and probed values returned to prior values. Choice selections restored; Spiral L3C108 remains selected. Other layer opacities and amount-controlled creative effects were settled out for isolation. Native time animation continues.

Evidence: live-results.json, choices.json, full output PNGs and derived contact sheets. No retries required this round. Sampling is not full acceptance.


Audit correction: the SP Atom Grain / SP Field white-output assessment was invalid because the contact sheet discarded alpha. Correctly composited original captures show visible signal and changes. See ../white-output/REPORT.md. Other flags remain pending individual review.
