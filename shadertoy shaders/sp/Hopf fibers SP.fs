/*{
  "DESCRIPTION": "Hopf fibers \u2014 SMART PARAM v4 (shuffles, locks, no Speed).",
  "CREDIT": "tmst (Shadertoy) / SP port",
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
      "NAME": "a",
      "LABEL": "Orbit",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "aDrive",
      "LABEL": "Orbit Drive",
      "TYPE": "bool",
      "DEFAULT": true
    },
    {
      "NAME": "aLock",
      "LABEL": "Orbit Lock",
      "TYPE": "bool",
      "DEFAULT": false
    },
    {
      "NAME": "aRatio",
      "LABEL": "Orbit Ratio",
      "TYPE": "long",
      "DEFAULT": 2,
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
      "NAME": "aMult",
      "LABEL": "Orbit Mult",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": -16.0,
      "MAX": 16.0
    },
    {
      "NAME": "aOffset",
      "LABEL": "Orbit Offset",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "aShape",
      "LABEL": "Orbit Shape",
      "TYPE": "long",
      "DEFAULT": 0,
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
      "NAME": "aLo",
      "LABEL": "Orbit Lo",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "aHi",
      "LABEL": "Orbit Hi",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "b",
      "LABEL": "Spin",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "bDrive",
      "LABEL": "Spin Drive",
      "TYPE": "bool",
      "DEFAULT": true
    },
    {
      "NAME": "bLock",
      "LABEL": "Spin Lock",
      "TYPE": "bool",
      "DEFAULT": false
    },
    {
      "NAME": "bRatio",
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
      "NAME": "bMult",
      "LABEL": "Spin Mult",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": -16.0,
      "MAX": 16.0
    },
    {
      "NAME": "bOffset",
      "LABEL": "Spin Offset",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "bShape",
      "LABEL": "Spin Shape",
      "TYPE": "long",
      "DEFAULT": 0,
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
      "NAME": "bLo",
      "LABEL": "Spin Lo",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "bHi",
      "LABEL": "Spin Hi",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "c",
      "LABEL": "Axis",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "cDrive",
      "LABEL": "Axis Drive",
      "TYPE": "bool",
      "DEFAULT": true
    },
    {
      "NAME": "cLock",
      "LABEL": "Axis Lock",
      "TYPE": "bool",
      "DEFAULT": false
    },
    {
      "NAME": "cRatio",
      "LABEL": "Axis Ratio",
      "TYPE": "long",
      "DEFAULT": 8,
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
      "NAME": "cMult",
      "LABEL": "Axis Mult",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": -16.0,
      "MAX": 16.0
    },
    {
      "NAME": "cOffset",
      "LABEL": "Axis Offset",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "cShape",
      "LABEL": "Axis Shape",
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
      "NAME": "cLo",
      "LABEL": "Axis Lo",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "cHi",
      "LABEL": "Axis Hi",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "d",
      "LABEL": "Morph",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "dDrive",
      "LABEL": "Morph Drive",
      "TYPE": "bool",
      "DEFAULT": true
    },
    {
      "NAME": "dLock",
      "LABEL": "Morph Lock",
      "TYPE": "bool",
      "DEFAULT": false
    },
    {
      "NAME": "dRatio",
      "LABEL": "Morph Ratio",
      "TYPE": "long",
      "DEFAULT": 3,
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
      "NAME": "dMult",
      "LABEL": "Morph Mult",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": -16.0,
      "MAX": 16.0
    },
    {
      "NAME": "dOffset",
      "LABEL": "Morph Offset",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "dShape",
      "LABEL": "Morph Shape",
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
      "NAME": "dLo",
      "LABEL": "Morph Lo",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "dHi",
      "LABEL": "Morph Hi",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "e",
      "LABEL": "Hue",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "eDrive",
      "LABEL": "Hue Drive",
      "TYPE": "bool",
      "DEFAULT": true
    },
    {
      "NAME": "eLock",
      "LABEL": "Hue Lock",
      "TYPE": "bool",
      "DEFAULT": false
    },
    {
      "NAME": "eRatio",
      "LABEL": "Hue Ratio",
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
      "NAME": "eMult",
      "LABEL": "Hue Mult",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": -16.0,
      "MAX": 16.0
    },
    {
      "NAME": "eOffset",
      "LABEL": "Hue Offset",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "eShape",
      "LABEL": "Hue Shape",
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
      "NAME": "eLo",
      "LABEL": "Hue Lo",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "eHi",
      "LABEL": "Hue Hi",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "f",
      "LABEL": "Density",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "fDrive",
      "LABEL": "Density Drive",
      "TYPE": "bool",
      "DEFAULT": true
    },
    {
      "NAME": "fLock",
      "LABEL": "Density Lock",
      "TYPE": "bool",
      "DEFAULT": false
    },
    {
      "NAME": "fRatio",
      "LABEL": "Density Ratio",
      "TYPE": "long",
      "DEFAULT": 4,
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
      "NAME": "fMult",
      "LABEL": "Density Mult",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": -16.0,
      "MAX": 16.0
    },
    {
      "NAME": "fOffset",
      "LABEL": "Density Offset",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "fShape",
      "LABEL": "Density Shape",
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
      "NAME": "fLo",
      "LABEL": "Density Lo",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "fHi",
      "LABEL": "Density Hi",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "g",
      "LABEL": "Pitch",
      "TYPE": "float",
      "DEFAULT": 0.58,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "gDrive",
      "LABEL": "Pitch Drive",
      "TYPE": "bool",
      "DEFAULT": true
    },
    {
      "NAME": "gLock",
      "LABEL": "Pitch Lock",
      "TYPE": "bool",
      "DEFAULT": false
    },
    {
      "NAME": "gRatio",
      "LABEL": "Pitch Ratio",
      "TYPE": "long",
      "DEFAULT": 5,
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
      "NAME": "gMult",
      "LABEL": "Pitch Mult",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": -16.0,
      "MAX": 16.0
    },
    {
      "NAME": "gOffset",
      "LABEL": "Pitch Offset",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "gShape",
      "LABEL": "Pitch Shape",
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
      "NAME": "gLo",
      "LABEL": "Pitch Lo",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "gHi",
      "LABEL": "Pitch Hi",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "h",
      "LABEL": "FOV",
      "TYPE": "float",
      "DEFAULT": 0.48,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hDrive",
      "LABEL": "FOV Drive",
      "TYPE": "bool",
      "DEFAULT": true
    },
    {
      "NAME": "hLock",
      "LABEL": "FOV Lock",
      "TYPE": "bool",
      "DEFAULT": false
    },
    {
      "NAME": "hRatio",
      "LABEL": "FOV Ratio",
      "TYPE": "long",
      "DEFAULT": 6,
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
      "NAME": "hMult",
      "LABEL": "FOV Mult",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": -16.0,
      "MAX": 16.0
    },
    {
      "NAME": "hOffset",
      "LABEL": "FOV Offset",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hShape",
      "LABEL": "FOV Shape",
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
      "NAME": "hLo",
      "LABEL": "FOV Lo",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hHi",
      "LABEL": "FOV Hi",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "i",
      "LABEL": "Cam Dist",
      "TYPE": "float",
      "DEFAULT": 0.31,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "iDrive",
      "LABEL": "Cam Dist Drive",
      "TYPE": "bool",
      "DEFAULT": true
    },
    {
      "NAME": "iLock",
      "LABEL": "Cam Dist Lock",
      "TYPE": "bool",
      "DEFAULT": false
    },
    {
      "NAME": "iRatio",
      "LABEL": "Cam Dist Ratio",
      "TYPE": "long",
      "DEFAULT": 7,
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
      "NAME": "iMult",
      "LABEL": "Cam Dist Mult",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": -16.0,
      "MAX": 16.0
    },
    {
      "NAME": "iOffset",
      "LABEL": "Cam Dist Offset",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "iShape",
      "LABEL": "Cam Dist Shape",
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
      "NAME": "iLo",
      "LABEL": "Cam Dist Lo",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "iHi",
      "LABEL": "Cam Dist Hi",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "renderQuality",
      "LABEL": "Render Quality",
      "TYPE": "long",
      "DEFAULT": 2,
      "VALUES": [
        0,
        1,
        2
      ],
      "LABELS": [
        "Performance",
        "Balanced",
        "Full"
      ]
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

#define PI 3.14159
#define STEP_D (renderQuality == 0 ? 0.08 : (renderQuality == 1 ? 0.06 : 0.04))
#define GE1 vec3(0.04, 0.0, 0.0)
#define GE2 vec3(0.0, 0.04, 0.0)
#define GE3 vec3(0.0, 0.0, 0.04)

float square_f(float x) { return x * x; }
float rand(vec2 p) { return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453); }
mat3 oProd(vec3 n) { float xy=n.x*n.y, xz=n.x*n.z, yz=n.y*n.z; return mat3(n.x*n.x,xy,xz, xy,n.y*n.y,yz, xz,yz,n.z*n.z); }
mat3 glRotate(vec3 axis, float angle) {
    float c = cos(angle), s = sin(angle); vec3 n = normalize(axis);
    return (1.0 - c) * oProd(n) + mat3(c, s*n.z, -s*n.y, -s*n.z, c, s*n.x, s*n.y, -s*n.x, c);
}
// camera rig: yaw (turns) + pitch (deg) → rotation; replaces raw quaternion sliders
mat3 camRig(float yawTurns, float pitchDeg) {
    return glRotate(vec3(0.0,1.0,0.0), yawTurns*2.0*PI) * glRotate(vec3(1.0,0.0,0.0), -pitchDeg*PI/180.0);
}
vec3 colormap(float t) { return 0.5 + 0.5 * cos(2.0 * PI * (t + vec3(0.0, 0.1, 0.2))); }
vec3 hopf(vec3 p) {
    float psq = dot(p, p);
    vec4 q = vec4(2.0 * p.xyz, -1.0 + psq) / (1.0 + psq);
    return vec3(2.0*(q.y*q.z - q.x*q.w), 1.0 - 2.0*(q.y*q.y + q.w*q.w), 2.0*(q.x*q.y + q.z*q.w));
}
vec4 getV(vec3 p, mat3 m, float phase) {
    vec3 rp = m * hopf(p);
    float theta = atan(-rp.z, rp.x);
    float sdy = square_f(0.5 + 0.5 * cos(rp.y * 5.0 * PI));
    float sdt = 0.5 + 0.5 * sin(theta * 20.0);
    float d1 = max(sdt * sdy, 0.55 * sdy);
    d1 = mix(d1, 0.8 * sdy, phase);
    return vec4(0.5 + 0.5 * rp.y, 0.0, 0.0, d1);
}
vec4 getC(vec3 p, vec3 camPos, mat3 m, float phase, float hue) {
    vec4 data0 = getV(p, m, phase);
    if (data0.a < 0.4) return vec4(0.0);
    vec3 gradA = vec3(getV(p+GE1,m,phase).a - getV(p-GE1,m,phase).a, getV(p+GE2,m,phase).a - getV(p-GE2,m,phase).a, getV(p+GE3,m,phase).a - getV(p-GE3,m,phase).a);
    vec3 normal = -gradA / (length(gradA) + 1e-5);
    vec3 matColor = mix(colormap(data0.r + hue), 0.5 + 0.5 * normal, 0.25);
    vec3 lightPos = camPos + vec3(0.0, 1.0, 0.0);
    vec3 L = normalize(lightPos - p), V = normalize(camPos - p);
    vec3 diffuse = clamp(dot(normal, L), 0.0, 1.0) * matColor;
    vec3 spec = pow(clamp(dot(normal, normalize(L + V)), 0.0, 1.0), 60.0) * vec3(1.0);
    return vec4(0.4 * matColor + 0.6 * (diffuse + spec), pow(data0.w, 3.0));
}
void marchVol(vec3 p, vec3 nv, out vec4 color, float phase, mat3 m, float densMul, float hue) {
    color = vec4(0.0);
    vec2 tRange = vec2(mix(1.0, 2.75, phase), 6.0);
    float t = tRange.s;
    for (int i = 0; i < 250; i++) {
        vec4 cHit = getC(p + t * nv, p, m, phase, hue);
        color += (1.0 - color.a) * vec4(cHit.rgb, 1.0) * ((STEP_D / 0.08) * cHit.a * densMul);
        t += STEP_D;
        if (t > tRange.t || color.a > 0.95) return;
    }
}
void main() {
    float H = TIME * heartRate;
    float A = sp(a, aDrive, aLock, true, H, 0, aRatio, aMult, aOffset, aShape, aLo, aHi);   // camera orbit (turns)
    float B = sp(b, bDrive, bLock, true, H, 1, bRatio, bMult, bOffset, bShape, bLo, bHi);   // object spin (turns)
    float C = sp(c, cDrive, cLock, false, H, 2, cRatio, cMult, cOffset, cShape, cLo, cHi);   // rotation-axis wobble
    float D = sp(d, dDrive, dLock, false, H, 3, dRatio, dMult, dOffset, dShape, dLo, dHi);   // morph phase
    float E = sp(e, eDrive, eLock, true, H, 4, eRatio, eMult, eOffset, eShape, eLo, eHi);   // hue
    float density = sp(f, fDrive, fLock, false, H, 5, fRatio, fMult, fOffset, fShape, fLo, fHi);
    float pitch   = spMap(sp(g, gDrive, gLock, false, H, 6, gRatio, gMult, gOffset, gShape, gLo, gHi), -90.0, 90.0);
    float fov     = spMap(sp(h, hDrive, hLock, false, H, 7, hRatio, hMult, hOffset, hShape, hLo, hHi),  0.5,  3.0);
    float camDist = spMap(sp(i, iDrive, iLock, false, H, 8, iRatio, iMult, iOffset, iShape, iLo, iHi),  1.5,  8.0);

    vec2 uv = (2.0 * gl_FragCoord.xy - RENDERSIZE.xy) / RENDERSIZE.y;
    mat3 camRot = camRig(A, pitch);
    vec3 camPos = camRot * vec3(0.0, 0.0, camDist);
    vec3 nvCamDir = camRot * normalize(vec3(uv, -fov));
    float phase = smoothstep(0.2, 0.8, D);
    mat3 m = glRotate(normalize(vec3(1.0, mix(-1.0, 1.0, C), 1.0)), -(PI + B * 2.0 * PI));
    float densMul = mix(0.3, 2.0, density);
    vec4 objColor;
    marchVol(camPos + rand(gl_FragCoord.xy) * nvCamDir * STEP_D, nvCamDir, objColor, phase, m, densMul, E);
    gl_FragColor = vec4(objColor.rgb, objColor.a);
}
