/*{
  "DESCRIPTION": "SP Figure \u2014 one grayscale silhouette probe. SMART PARAM v4.",
  "CREDIT": "SP probe",
  "ISFVSN": "2",
  "CATEGORIES": [
    "Generator"
  ],
  "INPUTS": [
    {
      "NAME": "heartRate",
      "LABEL": "Heart Rate (turns/s)",
      "TYPE": "float",
      "DEFAULT": 0.1,
      "MIN": 0.0,
      "MAX": 2.0
    },
    {
      "NAME": "pattern",
      "LABEL": "Pattern",
      "TYPE": "long",
      "DEFAULT": 11,
      "VALUES": [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18
      ],
      "LABELS": [
        "per-slot",
        "unison",
        "near-unison",
        "harmonic",
        "just intonation",
        "septimal",
        "undecimal",
        "powers of 2",
        "powers of 3",
        "cross-base 2v3",
        "pendulum wave",
        "fibonacci",
        "lucas",
        "coprime primes",
        "prime stacks",
        "CF approximants",
        "metallic",
        "near-phi",
        "irrationals"
      ]
    },
    {
      "NAME": "seed",
      "LABEL": "Seed",
      "TYPE": "long",
      "DEFAULT": 0,
      "VALUES": [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23,
        24,
        25,
        26,
        27,
        28,
        29,
        30,
        31
      ],
      "LABELS": [
        "0",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "10",
        "11",
        "12",
        "13",
        "14",
        "15",
        "16",
        "17",
        "18",
        "19",
        "20",
        "21",
        "22",
        "23",
        "24",
        "25",
        "26",
        "27",
        "28",
        "29",
        "30",
        "31"
      ]
    },
    {
      "NAME": "spread",
      "LABEL": "Spread",
      "TYPE": "long",
      "DEFAULT": 1,
      "VALUES": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8
      ],
      "LABELS": [
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8"
      ]
    },
    {
      "NAME": "depth",
      "LABEL": "Depth",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "fm",
      "LABEL": "FM",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "shufTiming",
      "LABEL": "Shuffle Timing",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 9999.0
    },
    {
      "NAME": "shufPattern",
      "LABEL": "Shuffle Pattern",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 9999.0
    },
    {
      "NAME": "shufMotion",
      "LABEL": "Shuffle Motion",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 9999.0
    },
    {
      "NAME": "shufRange",
      "LABEL": "Shuffle Range",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 9999.0
    },
    {
      "NAME": "shufDrives",
      "LABEL": "Shuffle Drives",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 9999.0
    },
    {
      "NAME": "shufLook",
      "LABEL": "Shuffle Look",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 9999.0
    },
    {
      "NAME": "shufAll",
      "LABEL": "Shuffle All",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 9999.0
    },
    {
      "NAME": "gSize",
      "LABEL": "Size",
      "TYPE": "float",
      "DEFAULT": 0.4,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "gSizeDrive",
      "LABEL": "Size Drive",
      "TYPE": "bool",
      "DEFAULT": true
    },
    {
      "NAME": "gSizeLock",
      "LABEL": "Size Lock",
      "TYPE": "bool",
      "DEFAULT": false
    },
    {
      "NAME": "gSizeRatio",
      "LABEL": "Size Ratio",
      "TYPE": "long",
      "DEFAULT": 0,
      "VALUES": [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15
      ],
      "LABELS": [
        "1:1",
        "1:2",
        "1:4",
        "2:3",
        "3:4",
        "4:5",
        "5:6",
        "3:5",
        "1/phi",
        "1/sqrt2",
        "1/pi",
        "1:3",
        "2:5",
        "5:8",
        "8:13",
        "3:2"
      ]
    },
    {
      "NAME": "gSizeMult",
      "LABEL": "Size Mult",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": -16.0,
      "MAX": 16.0
    },
    {
      "NAME": "gSizeOffset",
      "LABEL": "Size Offset",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "gSizeShape",
      "LABEL": "Size Shape",
      "TYPE": "long",
      "DEFAULT": 1,
      "VALUES": [
        0,
        1
      ],
      "LABELS": [
        "triangle",
        "cosine"
      ]
    },
    {
      "NAME": "gSizeLo",
      "LABEL": "Size Lo",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "gSizeHi",
      "LABEL": "Size Hi",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "gX",
      "LABEL": "X",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "gXDrive",
      "LABEL": "X Drive",
      "TYPE": "bool",
      "DEFAULT": true
    },
    {
      "NAME": "gXLock",
      "LABEL": "X Lock",
      "TYPE": "bool",
      "DEFAULT": false
    },
    {
      "NAME": "gXRatio",
      "LABEL": "X Ratio",
      "TYPE": "long",
      "DEFAULT": 0,
      "VALUES": [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15
      ],
      "LABELS": [
        "1:1",
        "1:2",
        "1:4",
        "2:3",
        "3:4",
        "4:5",
        "5:6",
        "3:5",
        "1/phi",
        "1/sqrt2",
        "1/pi",
        "1:3",
        "2:5",
        "5:8",
        "8:13",
        "3:2"
      ]
    },
    {
      "NAME": "gXMult",
      "LABEL": "X Mult",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": -16.0,
      "MAX": 16.0
    },
    {
      "NAME": "gXOffset",
      "LABEL": "X Offset",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "gXShape",
      "LABEL": "X Shape",
      "TYPE": "long",
      "DEFAULT": 1,
      "VALUES": [
        0,
        1
      ],
      "LABELS": [
        "triangle",
        "cosine"
      ]
    },
    {
      "NAME": "gXLo",
      "LABEL": "X Lo",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "gXHi",
      "LABEL": "X Hi",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "gY",
      "LABEL": "Y",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "gYDrive",
      "LABEL": "Y Drive",
      "TYPE": "bool",
      "DEFAULT": true
    },
    {
      "NAME": "gYLock",
      "LABEL": "Y Lock",
      "TYPE": "bool",
      "DEFAULT": false
    },
    {
      "NAME": "gYRatio",
      "LABEL": "Y Ratio",
      "TYPE": "long",
      "DEFAULT": 0,
      "VALUES": [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15
      ],
      "LABELS": [
        "1:1",
        "1:2",
        "1:4",
        "2:3",
        "3:4",
        "4:5",
        "5:6",
        "3:5",
        "1/phi",
        "1/sqrt2",
        "1/pi",
        "1:3",
        "2:5",
        "5:8",
        "8:13",
        "3:2"
      ]
    },
    {
      "NAME": "gYMult",
      "LABEL": "Y Mult",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": -16.0,
      "MAX": 16.0
    },
    {
      "NAME": "gYOffset",
      "LABEL": "Y Offset",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "gYShape",
      "LABEL": "Y Shape",
      "TYPE": "long",
      "DEFAULT": 1,
      "VALUES": [
        0,
        1
      ],
      "LABELS": [
        "triangle",
        "cosine"
      ]
    },
    {
      "NAME": "gYLo",
      "LABEL": "Y Lo",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "gYHi",
      "LABEL": "Y Hi",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "gTurn",
      "LABEL": "Turn",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "gTurnDrive",
      "LABEL": "Turn Drive",
      "TYPE": "bool",
      "DEFAULT": true
    },
    {
      "NAME": "gTurnLock",
      "LABEL": "Turn Lock",
      "TYPE": "bool",
      "DEFAULT": false
    },
    {
      "NAME": "gTurnRatio",
      "LABEL": "Turn Ratio",
      "TYPE": "long",
      "DEFAULT": 0,
      "VALUES": [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15
      ],
      "LABELS": [
        "1:1",
        "1:2",
        "1:4",
        "2:3",
        "3:4",
        "4:5",
        "5:6",
        "3:5",
        "1/phi",
        "1/sqrt2",
        "1/pi",
        "1:3",
        "2:5",
        "5:8",
        "8:13",
        "3:2"
      ]
    },
    {
      "NAME": "gTurnMult",
      "LABEL": "Turn Mult",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": -16.0,
      "MAX": 16.0
    },
    {
      "NAME": "gTurnOffset",
      "LABEL": "Turn Offset",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "gTurnShape",
      "LABEL": "Turn Shape",
      "TYPE": "long",
      "DEFAULT": 1,
      "VALUES": [
        0,
        1
      ],
      "LABELS": [
        "rotate",
        "sway"
      ]
    },
    {
      "NAME": "gTurnLo",
      "LABEL": "Turn Lo",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "gTurnHi",
      "LABEL": "Turn Hi",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "gLine",
      "LABEL": "Outline",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "gLineDrive",
      "LABEL": "Outline Drive",
      "TYPE": "bool",
      "DEFAULT": false
    },
    {
      "NAME": "gLineLock",
      "LABEL": "Outline Lock",
      "TYPE": "bool",
      "DEFAULT": false
    },
    {
      "NAME": "gLineRatio",
      "LABEL": "Outline Ratio",
      "TYPE": "long",
      "DEFAULT": 0,
      "VALUES": [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15
      ],
      "LABELS": [
        "1:1",
        "1:2",
        "1:4",
        "2:3",
        "3:4",
        "4:5",
        "5:6",
        "3:5",
        "1/phi",
        "1/sqrt2",
        "1/pi",
        "1:3",
        "2:5",
        "5:8",
        "8:13",
        "3:2"
      ]
    },
    {
      "NAME": "gLineMult",
      "LABEL": "Outline Mult",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": -16.0,
      "MAX": 16.0
    },
    {
      "NAME": "gLineOffset",
      "LABEL": "Outline Offset",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "gLineShape",
      "LABEL": "Outline Shape",
      "TYPE": "long",
      "DEFAULT": 1,
      "VALUES": [
        0,
        1
      ],
      "LABELS": [
        "triangle",
        "cosine"
      ]
    },
    {
      "NAME": "gLineLo",
      "LABEL": "Outline Lo",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "gLineHi",
      "LABEL": "Outline Hi",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "gMat",
      "LABEL": "Material",
      "TYPE": "float",
      "DEFAULT": 0.8,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "gMatDrive",
      "LABEL": "Material Drive",
      "TYPE": "bool",
      "DEFAULT": false
    },
    {
      "NAME": "gMatLock",
      "LABEL": "Material Lock",
      "TYPE": "bool",
      "DEFAULT": false
    },
    {
      "NAME": "gMatRatio",
      "LABEL": "Material Ratio",
      "TYPE": "long",
      "DEFAULT": 0,
      "VALUES": [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15
      ],
      "LABELS": [
        "1:1",
        "1:2",
        "1:4",
        "2:3",
        "3:4",
        "4:5",
        "5:6",
        "3:5",
        "1/phi",
        "1/sqrt2",
        "1/pi",
        "1:3",
        "2:5",
        "5:8",
        "8:13",
        "3:2"
      ]
    },
    {
      "NAME": "gMatMult",
      "LABEL": "Material Mult",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": -16.0,
      "MAX": 16.0
    },
    {
      "NAME": "gMatOffset",
      "LABEL": "Material Offset",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "gMatShape",
      "LABEL": "Material Shape",
      "TYPE": "long",
      "DEFAULT": 1,
      "VALUES": [
        0,
        1
      ],
      "LABELS": [
        "triangle",
        "cosine"
      ]
    },
    {
      "NAME": "gMatLo",
      "LABEL": "Material Lo",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "gMatHi",
      "LABEL": "Material Hi",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "gFlt",
      "LABEL": "Float",
      "TYPE": "float",
      "DEFAULT": 0.25,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "gFltDrive",
      "LABEL": "Float Drive",
      "TYPE": "bool",
      "DEFAULT": false
    },
    {
      "NAME": "gFltLock",
      "LABEL": "Float Lock",
      "TYPE": "bool",
      "DEFAULT": false
    },
    {
      "NAME": "gFltRatio",
      "LABEL": "Float Ratio",
      "TYPE": "long",
      "DEFAULT": 0,
      "VALUES": [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15
      ],
      "LABELS": [
        "1:1",
        "1:2",
        "1:4",
        "2:3",
        "3:4",
        "4:5",
        "5:6",
        "3:5",
        "1/phi",
        "1/sqrt2",
        "1/pi",
        "1:3",
        "2:5",
        "5:8",
        "8:13",
        "3:2"
      ]
    },
    {
      "NAME": "gFltMult",
      "LABEL": "Float Mult",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": -16.0,
      "MAX": 16.0
    },
    {
      "NAME": "gFltOffset",
      "LABEL": "Float Offset",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "gFltShape",
      "LABEL": "Float Shape",
      "TYPE": "long",
      "DEFAULT": 1,
      "VALUES": [
        0,
        1
      ],
      "LABELS": [
        "triangle",
        "cosine"
      ]
    },
    {
      "NAME": "gFltLo",
      "LABEL": "Float Lo",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "gFltHi",
      "LABEL": "Float Hi",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "gSpn",
      "LABEL": "Spin",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "gSpnDrive",
      "LABEL": "Spin Drive",
      "TYPE": "bool",
      "DEFAULT": true
    },
    {
      "NAME": "gSpnLock",
      "LABEL": "Spin Lock",
      "TYPE": "bool",
      "DEFAULT": false
    },
    {
      "NAME": "gSpnRatio",
      "LABEL": "Spin Ratio",
      "TYPE": "long",
      "DEFAULT": 0,
      "VALUES": [
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15
      ],
      "LABELS": [
        "1:1",
        "1:2",
        "1:4",
        "2:3",
        "3:4",
        "4:5",
        "5:6",
        "3:5",
        "1/phi",
        "1/sqrt2",
        "1/pi",
        "1:3",
        "2:5",
        "5:8",
        "8:13",
        "3:2"
      ]
    },
    {
      "NAME": "gSpnMult",
      "LABEL": "Spin Mult",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": -16.0,
      "MAX": 16.0
    },
    {
      "NAME": "gSpnOffset",
      "LABEL": "Spin Offset",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "gSpnShape",
      "LABEL": "Spin Shape",
      "TYPE": "long",
      "DEFAULT": 1,
      "VALUES": [
        0,
        1
      ],
      "LABELS": [
        "rotate",
        "sway"
      ]
    },
    {
      "NAME": "gSpnLo",
      "LABEL": "Spin Lo",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "gSpnHi",
      "LABEL": "Spin Hi",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 1.0
    }
  ]
}*/
// ─────────────────────────────────────────────────────────────────────────────
// sp.glsl v3 — SMART PARAM for ISF. Paste verbatim below the ISF header.
// Law (kit ratio.js):  φ = fract(H · m · r + o)
//   H heart turns · r ratio · m mult (sign = direction) · o offset · shape saw/cos.
// v3: the RATIO comes from a PATTERN — a catalog family as a GENERATOR of terms
//   (slot i gets term k = i·spread + seed). Families ordered tightest-sync → never-syncs.
//   depth crossfades manual↔driven (live fader). fm phase-modulates the phase (organic).
// Requires uniforms: pattern, seed, spread, depth, fm, shufTiming, shufPattern, shufMotion, shufRange, shufDrives, shufLook, shufAll.
// Precision: H split into whole+fraction; rationals use mod-q arithmetic → exact for days.
// ─────────────────────────────────────────────────────────────────────────────
#define SP_PHI 1.6180339887498949
#define SP_PI  3.1415926535897932
#define SP_E   2.7182818284590452

const float SP_PRIMES[32] = float[](2.,3.,5.,7.,11.,13.,17.,19.,23.,29.,31.,37.,41.,43.,47.,53.,59.,61.,67.,71.,73.,79.,83.,89.,97.,101.,103.,107.,109.,113.,127.,131.);

// per-slot library (pattern 0 = "per-slot": each slot's own Ratio dropdown)
//  0 1:1  1 1:2  2 1:4  3 2:3  4 3:4  5 4:5  6 5:6  7 3:5  8 1/φ  9 1/√2  10 1/π  11 1:3  12 2:5  13 5:8  14 8:13  15 3:2
vec2 spRatio(int i) {
    if (i == 1)  return vec2(1.0, 2.0);   if (i == 2)  return vec2(1.0, 4.0);   if (i == 3)  return vec2(2.0, 3.0);
    if (i == 4)  return vec2(3.0, 4.0);   if (i == 5)  return vec2(4.0, 5.0);   if (i == 6)  return vec2(5.0, 6.0);
    if (i == 7)  return vec2(3.0, 5.0);   if (i == 8)  return vec2(1.0/SP_PHI, -1.0); if (i == 9) return vec2(0.70710678118654752, -1.0);
    if (i == 10) return vec2(1.0/SP_PI, -1.0); if (i == 11) return vec2(1.0, 3.0); if (i == 12) return vec2(2.0, 5.0);
    if (i == 13) return vec2(5.0, 8.0);   if (i == 14) return vec2(8.0, 13.0);  if (i == 15) return vec2(3.0, 2.0);
    return vec2(1.0, 1.0);
}

// ── THE CATALOG as generators. family f, term k → (p,q); q<0 marks an irrational (p = value).
//  1 unison        2 near-unison (n+1):n     3 harmonic 1:n        4 just intonation   5 septimal
//  6 undecimal     7 powers of 2             8 powers of 3         9 cross-base 2^a/3^b 10 pendulum (8+k):8
// 11 fibonacci    12 lucas                  13 coprime primes 1:p 14 prime stacks p:p' 15 CF approximants
// 16 metallic 1/δn 17 near-φ cluster        18 pure irrationals
vec2 spTerm(int f, int k) {
    k = max(k, 0);
    if (f == 1) return vec2(1.0, 1.0);
    if (f == 2) { float n = 8.0 + float(k); return vec2(n + 1.0, n); }
    if (f == 3) return vec2(1.0, float(k + 1));
    if (f == 4) { int j = k - 12 * (k / 12);
        if (j==0) return vec2(1.,1.);   if (j==1) return vec2(16.,15.); if (j==2) return vec2(9.,8.);  if (j==3) return vec2(6.,5.);
        if (j==4) return vec2(5.,4.);   if (j==5) return vec2(4.,3.);   if (j==6) return vec2(45.,32.); if (j==7) return vec2(3.,2.);
        if (j==8) return vec2(8.,5.);   if (j==9) return vec2(5.,3.);   if (j==10) return vec2(15.,8.); return vec2(2.,1.); }
    if (f == 5) { int j = k - 10 * (k / 10);
        if (j==0) return vec2(7.,6.);   if (j==1) return vec2(7.,5.);   if (j==2) return vec2(7.,4.);  if (j==3) return vec2(8.,7.);
        if (j==4) return vec2(9.,7.);   if (j==5) return vec2(10.,7.);  if (j==6) return vec2(12.,7.); if (j==7) return vec2(14.,9.);
        if (j==8) return vec2(21.,16.); return vec2(49.,48.); }
    if (f == 6) { int j = k - 10 * (k / 10);
        if (j==0) return vec2(11.,8.);  if (j==1) return vec2(11.,6.);  if (j==2) return vec2(11.,7.); if (j==3) return vec2(11.,9.);
        if (j==4) return vec2(11.,10.); if (j==5) return vec2(13.,8.);  if (j==6) return vec2(13.,12.); if (j==7) return vec2(13.,7.);
        if (j==8) return vec2(13.,9.);  return vec2(13.,11.); }
    if (f == 7) return vec2(1.0, pow(2.0, float(k - 12 * (k / 12))));
    if (f == 8) return vec2(1.0, pow(3.0, float(k - 8 * (k / 8))));
    if (f == 9) { int a = 1 + k - 4 * (k / 4), b = 1 + (k / 4) - 3 * ((k / 4) / 3); return vec2(pow(2.0, float(a)), pow(3.0, float(b))); }
    if (f == 10) return vec2(8.0 + float(k), 8.0);
    if (f == 11) { float a = 1.0, b = 1.0; for (int n = 0; n < 24; n++) { if (n >= k) break; float c = a + b; a = b; b = c; } return vec2(a, b); }
    if (f == 12) { float a = 2.0, b = 1.0; for (int n = 0; n < 24; n++) { if (n >= k) break; float c = a + b; a = b; b = c; } return vec2(a, b); }
    if (f == 13) return vec2(1.0, SP_PRIMES[k - 32 * (k / 32)]);
    if (f == 14) { int j = k - 31 * (k / 31); return vec2(SP_PRIMES[j], SP_PRIMES[j + 1]); }
    if (f == 15) { int j = k - 10 * (k / 10);   // continued-fraction approximants of √2 and π (alternating)
        if (j==0) return vec2(3.,2.);   if (j==1) return vec2(22.,7.);  if (j==2) return vec2(7.,5.);   if (j==3) return vec2(333.,106.);
        if (j==4) return vec2(17.,12.); if (j==5) return vec2(355.,113.); if (j==6) return vec2(41.,29.); if (j==7) return vec2(103993.,33102.);
        if (j==8) return vec2(99.,70.); return vec2(239.,169.); }
    if (f == 16) { float n = 1.0 + float(k); float d = (n + sqrt(n * n + 4.0)) * 0.5; return vec2(1.0 / d, -1.0); }
    if (f == 17) return vec2((1.0 / SP_PHI) * (1.0 + 0.013 * float(k)), -1.0);
    if (f == 18) { int j = k - 9 * (k / 9);
        float v = 1.0 / SP_PHI; if (j==1) v = 0.70710678; if (j==2) v = 1.0 / SP_PI; if (j==3) v = 1.0 / SP_E; if (j==4) v = 0.57735027;
        if (j==5) v = 0.44721360; if (j==6) v = SP_PI / 4.0; if (j==7) v = SP_E / SP_PI; if (j==8) v = SP_PI / SP_E; return vec2(v, -1.0); }
    return vec2(1.0, 1.0);
}

// phase at heart H for ratio r=(p,q), mult m, offset o
float spPhase(float H, vec2 r, float m, float o) {
    float mm = (abs(m) < 1.0) ? sign(m + 1e-9) : m;
    float Hi = floor(H), Hf = H - Hi;
    if (r.y > 0.0) {   // rational: exact mod-q arithmetic for the whole-turn part
        float mi = floor(abs(mm) + 0.5); float mf = abs(mm) - mi;
        float whole = mod(Hi * mi * r.x, r.y) / r.y;
        float rest  = fract((Hi * mf + Hf * abs(mm)) * r.x / r.y);
        return fract(sign(mm) * (whole + rest) + o);
    }
    return fract(H * mm * r.x + o);   // irrational: free-running
}
float spShape(float ph, int shape) { return (shape == 1) ? 0.5 - 0.5 * cos(ph * 2.0 * SP_PI) : ph; }

// ── SHUFFLE: each category has a seed (a Counter bumped by a button; 0 = manual). Deterministic hashes → recallable.
float spHash(float seed, int slot, float salt) {
    return fract(sin(seed * 12.9898 + float(slot) * 78.233 + salt * 37.719) * 43758.5453);
}
float spCat(float cat) { return cat + 1000.0 * shufAll; }   // Shuffle All folds into every category

// THE smart param v4. lock = exclude this slot from all shuffles.
float sp(float manual, bool drive, bool lock, bool cyc, float H, int i, int ri, float m, float o, int shape, float lo, float hi) {
    // ── effective config (shuffles override unless locked / seed 0) ──
    int   pat = pattern;  int sd = seed;  int spr = spread;
    float sT = spCat(shufTiming), sP = spCat(shufPattern), sM = spCat(shufMotion), sR = spCat(shufRange), sD = spCat(shufDrives), sL = spCat(shufLook);
    if (sP > 0.0) pat = 1 + int(floor(spHash(sP, 0, 1.0) * 18.0));
    if (sT > 0.0) { sd = int(floor(spHash(sT, 0, 2.0) * 32.0)); spr = 1 + int(floor(spHash(sT, 0, 3.0) * 4.0)); }
    if (!lock) {
        if (sL > 0.0) manual = spHash(sL, i, 4.0);
        if (sD > 0.0) drive = drive && (spHash(sD, i, 5.0) > 0.45);
        if (sM > 0.0) {
            float hm = spHash(sM, i, 6.0);
            m = (hm < 0.35) ? 1.0 : (hm < 0.6) ? 2.0 : (hm < 0.75) ? 3.0 : (hm < 0.85) ? 4.0 : (hm < 0.95) ? -1.0 : -2.0;
            shape = (spHash(sM, i, 7.0) > 0.5) ? 1 : 0;
            o = spHash(sM, i, 8.0);
        }
        if (sR > 0.0) { lo = spHash(sR, i, 9.0) * 0.5; hi = min(1.0, lo + 0.3 + spHash(sR, i, 10.0) * 0.7); }
    }
    if (!drive) return manual;
    int k = i * spr + sd;
    vec2 r = (pat == 0) ? spRatio(ri) : spTerm(pat, k);
    float ph = spPhase(H, r, m, o);
    if (fm > 0.0) {
        vec2 rf = (pat == 0) ? spRatio(ri) : spTerm(pat, k + 1);
        float phf = spPhase(H, rf, 1.0, 0.37 * float(i));
        ph = fract(ph + fm * 0.25 * (0.5 - 0.5 * cos(phf * 2.0 * SP_PI)));
    }
    if (cyc) {
        if (shape == 0) return fract(manual + ph);
        return fract(manual + depth * (hi - lo) * (0.5 - 0.5 * cos(ph * 2.0 * SP_PI)));
    }
    float s = (shape == 0) ? 1.0 - abs(2.0 * ph - 1.0) : 0.5 - 0.5 * cos(ph * 2.0 * SP_PI);
    return mix(manual, mix(lo, hi, s), depth);
}
float spMap(float s, float outMin, float outMax) { return outMin + s * (outMax - outMin); }

float sdCapsule2(vec2 p, float L, float r) {
    p.x -= clamp(p.x, -L, L);
    return length(p) - r;
}
float spFlat(vec2 p, mat2 R, float L, float r) {
    return sdCapsule2(R * p, L, r);
}
vec3 spPlaneMap(vec2 sq, vec3 uu, vec3 vv, vec3 nn, float dU) {   // eye-ray ∩ rotated plane → material coords
    vec3 D = vec3(sq, dU);
    float den = dot(nn, D);
    if (abs(den) < 1e-4) return vec3(1e6, 1e6, 0.0);
    float t = (dU * nn.z) / den;
    if (t <= 0.0) return vec3(1e6, 1e6, 0.0);
    vec3 Xp = vec3(0.0, 0.0, -dU) + t * D;
    return vec3(dot(uu, Xp), dot(vv, Xp), 1.0);
}
void main() {
    float H = TIME * heartRate;                 // pilot convention: heart in-shader; Wire-side later

    float SZ = sp(gSize, gSizeDrive, gSizeLock, false, H, 0, gSizeRatio, gSizeMult, gSizeOffset, gSizeShape, gSizeLo, gSizeHi);       // presence — the fundamental
    float X  = sp(gX, gXDrive, gXLock, false, H, 1, gXRatio, gXMult, gXOffset, gXShape, gXLo, gXHi);
    float Y  = sp(gY, gYDrive, gYLock, false, H, 2, gYRatio, gYMult, gYOffset, gYShape, gYLo, gYHi);
    float TN = sp(gTurn, gTurnDrive, gTurnLock, true, H, 3, gTurnRatio, gTurnMult, gTurnOffset, gTurnShape, gTurnLo, gTurnHi);       // cyclic in-plane rotation (2D's one plane)
    float OL = sp(gLine, gLineDrive, gLineLock, false, H, 4, gLineRatio, gLineMult, gLineOffset, gLineShape, gLineLo, gLineHi);       // 0 solid — 1 open ring
    float MT = sp(gMat, gMatDrive, gMatLock, false, H, 5, gMatRatio, gMatMult, gMatOffset, gMatShape, gMatLo, gMatHi);        // MATERIAL: fog → soft pillow → hard inked solid
    float FLT = sp(gFlt, gFltDrive, gFltLock, false, H, 6, gFltRatio, gFltMult, gFltOffset, gFltShape, gFltLo, gFltHi);       // FLOAT: grounded → seated → airborne
    float SPN = sp(gSpn, gSpnDrive, gSpnLock, true, H, 7, gSpnRatio, gSpnMult, gSpnOffset, gSpnShape, gSpnLo, gSpnHi);       // SPIN: cyclic plane tumble on the diagonal axis
    // ── the folds: three macros drive the old internals on taste curves ──
    float ED = pow(MT, 0.7);                                    // edge hardens with material
    float EM = smoothstep(0.05, 0.6, MT);                       // relief arrives early
    float ST = smoothstep(0.55, 1.0, MT) * 0.8;                 // ink only on hard material
    float SH = smoothstep(0.05, 0.35, FLT) * (1.0 - smoothstep(0.5, 0.95, FLT));   // contact: rises, then lifts away
    float DR = smoothstep(0.35, 1.0, FLT);                      // throw grows with altitude

    vec2 uv = gl_FragCoord.xy / RENDERSIZE.xy - 0.5;
    float asp = RENDERSIZE.x / RENDERSIZE.y;
    uv.x *= asp;

    // ── containment law: the figure may NEVER touch the frame edge (cloners repeat edges) ──
    float rad = 0.02 + SZ * 0.34;                               // bounding radius incl. rotation
    float m = 0.03;
    vec2 hf2 = vec2(0.5 * asp, 0.5);
    vec2 c = (vec2(X, Y) - 0.5) * 2.0 * max(hf2 - rad * 1.6 - m, vec2(0.0));   // travel shrinks as size grows (slab+shadows margin)

    float a = TN * 2.0 * SP_PI;
    mat2 R = mat2(cos(a), sin(a), -sin(a), cos(a));

    // ── in-shader perspective plane rotation (Transform's trick, but containment-safe) ──
    float axr = SPN * 2.0 * SP_PI;                              // one Spin phase, both planes:
    float ayr = SPN * 2.0 * SP_PI;                              // a tumble about the diagonal axis
    float ca_ = cos(axr), sa_ = sin(axr), cb_ = cos(ayr), sb_ = sin(ayr);
    vec3 uu = vec3(cb_, 0.0, -sb_);
    vec3 vv = vec3(sa_ * sb_, ca_, sa_ * cb_);
    vec3 nn = vec3(ca_ * sb_, -sa_, ca_ * cb_);
    float dU = 4.0;
    float kNow = dU / (dU - min(length(nn.xy), 0.95));          // adaptive shrink: near edge can never escape
    vec2 s2 = (uv - c) / rad;
    float edgeGuard = 1.0 - smoothstep(0.985, 1.0, length(s2)); // containment safety feather
    vec3 mm = spPlaneMap(s2 * kNow, uu, vv, nn, dU);
    vec2 p = mm.xy * rad;                                       // the flat drawing, seen in perspective
    float r = rad * 0.45;                                       // capsule: length 2·rad, width 0.9·rad
    float L = rad - r;
    vec2 q = R * p;
    vec2 qq = vec2(q.x - clamp(q.x, -L, L), q.y);
    float ql = length(qq);
    float sd0 = ql - r;                                         // the silhouette
    vec2 gsd = (ql > 1e-6) ? (qq / ql) * R : vec2(0.0, 1.0);    // SDF gradient, back in screen space

    float sd = sd0;
    float e = mix(r * 0.9, 0.003, ED);
    float w = mix(r * 1.30, max(0.008, rad * 0.08), OL);        // hollow: real closed dwell at low OL, then opens along the spine
    float vTop = smoothstep(0.0, -e, sd) - smoothstep(0.0, -e, sd + w);
    float v = vTop;

    // ── Stroke: ink riding the VISIBLE silhouette (the mid-fade contour), not the static
    //    capsule — it follows Edge dynamically. Ink softness breathes with Edge too. ──
    float sw = ST * r * 0.09;
    float top = min(-0.5 * e + 0.5 * sw, 0.0);
    float bot = top - sw;
    float ia = max(0.0035, e * 0.15);
    float stroke = smoothstep(top + ia, top - ia, sd0) * (1.0 - smoothstep(bot + ia, bot - ia, sd0));
    // inner rim: ink the hollow's visible contour too (depth: a hole through a solid, not missing
    // paint) — but ONLY while the aperture is actually open, so the full capsule returns clean
    float lvl2 = -(w + 0.5 * e);                                // mid-fade of the inner edge
    float top2 = lvl2 + 0.5 * sw;
    float bot2 = lvl2 - 0.5 * sw;
    float inner = smoothstep(top2 + ia, top2 - ia, sd) * (1.0 - smoothstep(bot2 + ia, bot2 - ia, sd));
    float gateAp = smoothstep(0.0, r * 0.08, r - w);            // aperture-open gate
    inner *= gateAp;                                            // fades in as the hollow opens
    stroke = max(stroke, inner);

    // ── the ink IS the boundary: with any real stroke, no body material renders beyond it
    //    (kills the translucent "jacket" the outer half of a soft fade would otherwise wear) ──
    float bodyCut = mix(1.0, smoothstep(top + ia, top - ia, sd0), clamp(ST * 8.0, 0.0, 1.0));
    vTop *= bodyCut; v *= bodyCut;

    // ── Emboss: dome relief over a wide band from the SDF gradient (probes have SDFs;
    //    adapted shaders without one fall back to luminance-gradient). Light = the comp's
    //    one implied sun, same as the 3D figure. ──
    float t = clamp(-sd / r, 0.0, 1.0);                         // full dome: 0 at rim → 1 only at the spine
    float tilt = cos(t * 1.5708) * EM * 2.2;                    // no plateau — the solid reads as one pillow
    vec3 n = normalize(vec3(gsd * tilt, 1.0));
    vec3 Ld = normalize(vec3(-0.4, 0.55, 1.15));  // same sun azimuth, brought frontal: crown lit, edges fall away
    float lam = max(0.0, dot(n, Ld));
    float spec = pow(max(0.0, dot(reflect(-Ld, n), vec3(0.0, 0.0, 1.0))), 20.0);
    float shade = mix(1.0, 0.30 + 0.80 * lam, EM);
    vec3 col = vec3(vTop * shade + vTop * spec * EM);

    // ── corpus pass (field.visual-perception) ──
    float strokeOn = clamp(ST * 8.0, 0.0, 1.0);
    // Cornsweet shoulders: the body brightens toward its ink — reads as lighter material for free
    float cw = r * 0.35;
    float shO = smoothstep(top - cw, top, sd0);
    float shI = smoothstep(top2 + cw, top2, sd) * gateAp;
    col *= 1.0 + 0.20 * strokeOn * max(shO, shI);
    // Pinna bright line: a hairline light contour inside the dark ink — luminance spreads across the body
    float hw = max(0.004, sw * 0.5);
    float hl  = smoothstep(bot + ia, bot - ia, sd0) * (1.0 - smoothstep(bot - hw + ia, bot - hw - ia, sd0));
    float hl2 = (smoothstep(top2 - ia, top2 + ia, sd) * (1.0 - smoothstep(top2 + hw - ia, top2 + hw + ia, sd))) * gateAp;
    col += vec3(0.30) * strokeOn * max(hl, hl2) * v;
    // Crater pit: the aperture's inner wall shaded INVERTED to the dome — same sun, hole reads sunken
    float pw = r * 0.18;
    float pband = (smoothstep(bot2 + ia, bot2 - ia, sd) - smoothstep(bot2 - pw + ia, bot2 - pw - ia, sd)) * gateAp;
    pband = max(pband, 0.0) * clamp((sd - (bot2 - pw)) / pw, 0.0, 1.0);
    vec2 gN = normalize(gsd + vec2(1e-5));
    float pitLit = max(0.0, dot(-gN, normalize(Ld.xy)));
    col += vec3(0.10 + 0.40 * pitLit) * pband;

    float ink = stroke * 0.85;                                  // drawn line, not a void
    col *= (1.0 - ink);
    float aFig = max(max(v, ink), pband * 0.85);

    // ── Shadow: soft dark cast toward lower-right (the sun sits upper-left), under the figure ──
    float aSh = 0.0;
    if (SH > 0.001) {
        vec3 mS = spPlaneMap((s2 - vec2(0.11, -0.13) * SH) * kNow, uu, vv, nn, dU);
        float sdSh = spFlat(mS.xy * rad, R, L, r);
        aSh = SH * 0.55 * smoothstep(rad * 0.10, -rad * 0.10, sdSh) * (1.0 - aFig);
    }
    if (DR > 0.001) {
        vec3 mD = spPlaneMap((s2 - vec2(0.30, -0.34) * DR) * kNow, uu, vv, nn, dU);
        float sdD = spFlat(mD.xy * rad, R, L, r);
        float aD = DR * 0.40 * smoothstep(rad * 0.24, -rad * 0.24, sdD) * (1.0 - aFig);
        aSh = max(aSh, aD);
    }
    gl_FragColor = vec4(min(col, vec3(1.0)) * edgeGuard, min(1.0, aFig + aSh) * edgeGuard);   // real alpha: contained, always
}
