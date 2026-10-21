/*{
  "DESCRIPTION": "SP Figure 3D \u2014 the torus carrying the 2D laws: quaternion tumble, arc, wire, toon ink. SMART PARAM v4.",
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
      "NAME": "hSize",
      "LABEL": "Size",
      "TYPE": "float",
      "DEFAULT": 0.4,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hSizeDrive",
      "LABEL": "Size Drive",
      "TYPE": "bool",
      "DEFAULT": true
    },
    {
      "NAME": "hSizeLock",
      "LABEL": "Size Lock",
      "TYPE": "bool",
      "DEFAULT": false
    },
    {
      "NAME": "hSizeRatio",
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
      "NAME": "hSizeMult",
      "LABEL": "Size Mult",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": -16.0,
      "MAX": 16.0
    },
    {
      "NAME": "hSizeOffset",
      "LABEL": "Size Offset",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hSizeShape",
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
      "NAME": "hSizeLo",
      "LABEL": "Size Lo",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hSizeHi",
      "LABEL": "Size Hi",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hX",
      "LABEL": "X",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hXDrive",
      "LABEL": "X Drive",
      "TYPE": "bool",
      "DEFAULT": true
    },
    {
      "NAME": "hXLock",
      "LABEL": "X Lock",
      "TYPE": "bool",
      "DEFAULT": false
    },
    {
      "NAME": "hXRatio",
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
      "NAME": "hXMult",
      "LABEL": "X Mult",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": -16.0,
      "MAX": 16.0
    },
    {
      "NAME": "hXOffset",
      "LABEL": "X Offset",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hXShape",
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
      "NAME": "hXLo",
      "LABEL": "X Lo",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hXHi",
      "LABEL": "X Hi",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hY",
      "LABEL": "Y",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hYDrive",
      "LABEL": "Y Drive",
      "TYPE": "bool",
      "DEFAULT": true
    },
    {
      "NAME": "hYLock",
      "LABEL": "Y Lock",
      "TYPE": "bool",
      "DEFAULT": false
    },
    {
      "NAME": "hYRatio",
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
      "NAME": "hYMult",
      "LABEL": "Y Mult",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": -16.0,
      "MAX": 16.0
    },
    {
      "NAME": "hYOffset",
      "LABEL": "Y Offset",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hYShape",
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
      "NAME": "hYLo",
      "LABEL": "Y Lo",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hYHi",
      "LABEL": "Y Hi",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hTum",
      "LABEL": "Tumble",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hTumDrive",
      "LABEL": "Tumble Drive",
      "TYPE": "bool",
      "DEFAULT": true
    },
    {
      "NAME": "hTumLock",
      "LABEL": "Tumble Lock",
      "TYPE": "bool",
      "DEFAULT": false
    },
    {
      "NAME": "hTumRatio",
      "LABEL": "Tumble Ratio",
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
      "NAME": "hTumMult",
      "LABEL": "Tumble Mult",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": -16.0,
      "MAX": 16.0
    },
    {
      "NAME": "hTumOffset",
      "LABEL": "Tumble Offset",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hTumShape",
      "LABEL": "Tumble Shape",
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
      "NAME": "hTumLo",
      "LABEL": "Tumble Lo",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hTumHi",
      "LABEL": "Tumble Hi",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hAxis",
      "LABEL": "Axis",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hAxisDrive",
      "LABEL": "Axis Drive",
      "TYPE": "bool",
      "DEFAULT": true
    },
    {
      "NAME": "hAxisLock",
      "LABEL": "Axis Lock",
      "TYPE": "bool",
      "DEFAULT": false
    },
    {
      "NAME": "hAxisRatio",
      "LABEL": "Axis Ratio",
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
      "NAME": "hAxisMult",
      "LABEL": "Axis Mult",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": -16.0,
      "MAX": 16.0
    },
    {
      "NAME": "hAxisOffset",
      "LABEL": "Axis Offset",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hAxisShape",
      "LABEL": "Axis Shape",
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
      "NAME": "hAxisLo",
      "LABEL": "Axis Lo",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hAxisHi",
      "LABEL": "Axis Hi",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hEdge",
      "LABEL": "Edge",
      "TYPE": "float",
      "DEFAULT": 0.8,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hEdgeDrive",
      "LABEL": "Edge Drive",
      "TYPE": "bool",
      "DEFAULT": false
    },
    {
      "NAME": "hEdgeLock",
      "LABEL": "Edge Lock",
      "TYPE": "bool",
      "DEFAULT": false
    },
    {
      "NAME": "hEdgeRatio",
      "LABEL": "Edge Ratio",
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
      "NAME": "hEdgeMult",
      "LABEL": "Edge Mult",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": -16.0,
      "MAX": 16.0
    },
    {
      "NAME": "hEdgeOffset",
      "LABEL": "Edge Offset",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hEdgeShape",
      "LABEL": "Edge Shape",
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
      "NAME": "hEdgeLo",
      "LABEL": "Edge Lo",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hEdgeHi",
      "LABEL": "Edge Hi",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hLine",
      "LABEL": "Outline",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hLineDrive",
      "LABEL": "Outline Drive",
      "TYPE": "bool",
      "DEFAULT": false
    },
    {
      "NAME": "hLineLock",
      "LABEL": "Outline Lock",
      "TYPE": "bool",
      "DEFAULT": false
    },
    {
      "NAME": "hLineRatio",
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
      "NAME": "hLineMult",
      "LABEL": "Outline Mult",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": -16.0,
      "MAX": 16.0
    },
    {
      "NAME": "hLineOffset",
      "LABEL": "Outline Offset",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hLineShape",
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
      "NAME": "hLineLo",
      "LABEL": "Outline Lo",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hLineHi",
      "LABEL": "Outline Hi",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hEmb",
      "LABEL": "Emboss",
      "TYPE": "float",
      "DEFAULT": 0.9,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hEmbDrive",
      "LABEL": "Emboss Drive",
      "TYPE": "bool",
      "DEFAULT": false
    },
    {
      "NAME": "hEmbLock",
      "LABEL": "Emboss Lock",
      "TYPE": "bool",
      "DEFAULT": false
    },
    {
      "NAME": "hEmbRatio",
      "LABEL": "Emboss Ratio",
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
      "NAME": "hEmbMult",
      "LABEL": "Emboss Mult",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": -16.0,
      "MAX": 16.0
    },
    {
      "NAME": "hEmbOffset",
      "LABEL": "Emboss Offset",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hEmbShape",
      "LABEL": "Emboss Shape",
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
      "NAME": "hEmbLo",
      "LABEL": "Emboss Lo",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hEmbHi",
      "LABEL": "Emboss Hi",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hStk",
      "LABEL": "Stroke",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hStkDrive",
      "LABEL": "Stroke Drive",
      "TYPE": "bool",
      "DEFAULT": false
    },
    {
      "NAME": "hStkLock",
      "LABEL": "Stroke Lock",
      "TYPE": "bool",
      "DEFAULT": false
    },
    {
      "NAME": "hStkRatio",
      "LABEL": "Stroke Ratio",
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
      "NAME": "hStkMult",
      "LABEL": "Stroke Mult",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": -16.0,
      "MAX": 16.0
    },
    {
      "NAME": "hStkOffset",
      "LABEL": "Stroke Offset",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hStkShape",
      "LABEL": "Stroke Shape",
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
      "NAME": "hStkLo",
      "LABEL": "Stroke Lo",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hStkHi",
      "LABEL": "Stroke Hi",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hShd",
      "LABEL": "Shadow",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hShdDrive",
      "LABEL": "Shadow Drive",
      "TYPE": "bool",
      "DEFAULT": false
    },
    {
      "NAME": "hShdLock",
      "LABEL": "Shadow Lock",
      "TYPE": "bool",
      "DEFAULT": false
    },
    {
      "NAME": "hShdRatio",
      "LABEL": "Shadow Ratio",
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
      "NAME": "hShdMult",
      "LABEL": "Shadow Mult",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": -16.0,
      "MAX": 16.0
    },
    {
      "NAME": "hShdOffset",
      "LABEL": "Shadow Offset",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hShdShape",
      "LABEL": "Shadow Shape",
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
      "NAME": "hShdLo",
      "LABEL": "Shadow Lo",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hShdHi",
      "LABEL": "Shadow Hi",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hDrop",
      "LABEL": "Drop",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hDropDrive",
      "LABEL": "Drop Drive",
      "TYPE": "bool",
      "DEFAULT": false
    },
    {
      "NAME": "hDropLock",
      "LABEL": "Drop Lock",
      "TYPE": "bool",
      "DEFAULT": false
    },
    {
      "NAME": "hDropRatio",
      "LABEL": "Drop Ratio",
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
      "NAME": "hDropMult",
      "LABEL": "Drop Mult",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": -16.0,
      "MAX": 16.0
    },
    {
      "NAME": "hDropOffset",
      "LABEL": "Drop Offset",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hDropShape",
      "LABEL": "Drop Shape",
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
      "NAME": "hDropLo",
      "LABEL": "Drop Lo",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hDropHi",
      "LABEL": "Drop Hi",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hMic",
      "LABEL": "Micro",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hMicDrive",
      "LABEL": "Micro Drive",
      "TYPE": "bool",
      "DEFAULT": false
    },
    {
      "NAME": "hMicLock",
      "LABEL": "Micro Lock",
      "TYPE": "bool",
      "DEFAULT": false
    },
    {
      "NAME": "hMicRatio",
      "LABEL": "Micro Ratio",
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
      "NAME": "hMicMult",
      "LABEL": "Micro Mult",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": -16.0,
      "MAX": 16.0
    },
    {
      "NAME": "hMicOffset",
      "LABEL": "Micro Offset",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hMicShape",
      "LABEL": "Micro Shape",
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
      "NAME": "hMicLo",
      "LABEL": "Micro Lo",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "hMicHi",
      "LABEL": "Micro Hi",
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

vec3 spRotAA(vec3 p, vec3 ax, float th) {                 // Rodrigues, inverse rotation
    float c = cos(th), s = sin(th);
    return p * c + cross(ax, p) * s + ax * dot(ax, p) * (1.0 - c);
}
float spH3(vec3 p) { return fract(sin(dot(p, vec3(127.1, 311.7, 74.7))) * 43758.5453); }
float spN3(vec3 p) {
    vec3 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f);
    return mix(mix(mix(spH3(i), spH3(i + vec3(1, 0, 0)), f.x), mix(spH3(i + vec3(0, 1, 0)), spH3(i + vec3(1, 1, 0)), f.x), f.y),
               mix(mix(spH3(i + vec3(0, 0, 1)), spH3(i + vec3(1, 0, 1)), f.x), mix(spH3(i + vec3(0, 1, 1)), spH3(i + vec3(1, 1, 1)), f.x), f.y), f.z);
}
float spTorusS(vec3 p, float ra, float rb) { vec2 q = vec2(length(p.xy) - ra, p.z); return length(q) - rb; }
float spTorusW(vec3 p, float ra, float rb, float wr) {    // the wire lattice ON the torus surface
    vec2 q = vec2(length(p.xy) - ra, p.z);
    float dsh = abs(length(q) - rb);                       // distance to the shell
    float at = atan(p.y, p.x);
    float ap = atan(q.y, q.x);
    float st = 6.2831853 / 10.0;                           // 10 spokes around the ring
    float sp = 6.2831853 / 6.0;                            // 6 rings around the tube
    float gt = abs(fract(at / st + 0.5) - 0.5) * st * ra;
    float gp = abs(fract(ap / sp + 0.5) - 0.5) * sp * rb;
    float dg = min(gt, gp);
    return sqrt(dsh * dsh + dg * dg) - wr;
}
float spMapT(vec3 p, vec3 ax, float th, float ra, float rb, float W, float wr) {
    vec3 q = spRotAA(p, ax, th);
    q = q.xzy;
    float ds = spTorusS(q, ra, rb);
    if (W <= 0.001) return ds;
    return mix(ds, spTorusW(q, ra, rb, wr), W);            // the surface DEGRADES into its wires
}
float spSilT(vec3 ro, vec3 ax, float th, float ra, float rb, float W, float wr) {
    float t = 0.0, mind = 9.0;                             // soft silhouette mask for shadows
    for (int i = 0; i < 20; i++) {
        float d = spMapT(ro + vec3(0.0, 0.0, t), ax, th, ra, rb, W, wr);
        mind = min(mind, d);
        if (d < 0.004 || t > 3.6) break;
        t += d * 0.85;
    }
    return 1.0 - smoothstep(0.0, 0.12, mind);
}
void main() {
    float H = TIME * heartRate;

    float SZ = sp(hSize, hSizeDrive, hSizeLock, false, H, 0, hSizeRatio, hSizeMult, hSizeOffset, hSizeShape, hSizeLo, hSizeHi);   // presence — the fundamental
    float X  = sp(hX, hXDrive, hXLock, false, H, 1, hXRatio, hXMult, hXOffset, hXShape, hXLo, hXHi);
    float Y  = sp(hY, hYDrive, hYLock, false, H, 2, hYRatio, hYMult, hYOffset, hYShape, hYLo, hYHi);
    float TM = sp(hTum, hTumDrive, hTumLock, true, H, 3, hTumRatio, hTumMult, hTumOffset, hTumShape, hTumLo, hTumHi);    // rotation phase about the precessing axis
    float AX = sp(hAxis, hAxisDrive, hAxisLock, true, H, 4, hAxisRatio, hAxisMult, hAxisOffset, hAxisShape, hAxisLo, hAxisHi);   // axis precession phase — Tumble:Axis ratio = the character
    float ED = sp(hEdge, hEdgeDrive, hEdgeLock, false, H, 5, hEdgeRatio, hEdgeMult, hEdgeOffset, hEdgeShape, hEdgeLo, hEdgeHi);
    float OL = sp(hLine, hLineDrive, hLineLock, false, H, 6, hLineRatio, hLineMult, hLineOffset, hLineShape, hLineLo, hLineHi);
    float EM = sp(hEmb, hEmbDrive, hEmbLock, false, H, 7, hEmbRatio, hEmbMult, hEmbOffset, hEmbShape, hEmbLo, hEmbHi);
    float ST = sp(hStk, hStkDrive, hStkLock, false, H, 8, hStkRatio, hStkMult, hStkOffset, hStkShape, hStkLo, hStkHi);
    float SH = sp(hShd, hShdDrive, hShdLock, false, H, 9, hShdRatio, hShdMult, hShdOffset, hShdShape, hShdLo, hShdHi);
    float DR = sp(hDrop, hDropDrive, hDropLock, false, H, 10, hDropRatio, hDropMult, hDropOffset, hDropShape, hDropLo, hDropHi);
    float MC = sp(hMic, hMicDrive, hMicLock, false, H, 11, hMicRatio, hMicMult, hMicOffset, hMicShape, hMicLo, hMicHi);   // 0 clean chrome — 1 fuzzy noisy SEM chrome

    vec2 uv = gl_FragCoord.xy / RENDERSIZE.xy - 0.5;
    float asp = RENDERSIZE.x / RENDERSIZE.y;
    uv.x *= asp;

    // ── containment law ──
    float rad = 0.03 + SZ * 0.33;
    float m = 0.03;
    vec2 hf2 = vec2(0.5 * asp, 0.5);
    vec2 c = (vec2(X, Y) - 0.5) * 2.0 * max(hf2 - rad * 1.6 - m, vec2(0.0));
    vec2 s = (uv - c) / rad;

    // ── quaternion-style tumble: axis precesses on a cone, body rotates about it ──
    float psi = AX * 2.0 * SP_PI;
    vec3 ax = normalize(vec3(cos(psi) * 0.62, sin(psi) * 0.62, 0.78));
    float th = TM * 2.0 * SP_PI;

    // ── Outline: closed dwell → surface degrades to WIREFRAME → wires thin (the vanish beat) ──
    float ra = 0.60, rb = 0.24;
    float W = smoothstep(0.10, 0.60, OL);
    float wr = mix(0.055, 0.012, smoothstep(0.60, 1.0, OL));

    float strokeOn = clamp(ST * 8.0, 0.0, 1.0);
    float e3 = mix(0.30, 0.008, ED);

    vec3 col = vec3(0.0);
    float aOut = 0.0;
    if (dot(s, s) < 1.1) {
        vec3 ro = vec3(s, -2.0);
        float t = 0.0, mind = 9.0; bool hit = false; vec3 p = ro;
        for (int i = 0; i < 56; i++) {
            p = ro + vec3(0.0, 0.0, t);
            float d = spMapT(p, ax, th, ra, rb, W, wr);
            mind = min(mind, d);
            if (d < 0.0025) { hit = true; break; }
            t += d * 0.85;
            if (t > 4.0) break;
        }
        if (hit) {
            vec2 h = vec2(mix(0.005, 0.0018, W), 0.0);     // finer normals on thin wires
            vec3 n = normalize(vec3(
                spMapT(p + h.xyy, ax, th, ra, rb, W, wr) - spMapT(p - h.xyy, ax, th, ra, rb, W, wr),
                spMapT(p + h.yxy, ax, th, ra, rb, W, wr) - spMapT(p - h.yxy, ax, th, ra, rb, W, wr),
                spMapT(p + h.yyx, ax, th, ra, rb, W, wr) - spMapT(p - h.yyx, ax, th, ra, rb, W, wr)));
            // ── Micro: fuzzy noisy chrome — noise lives in OBJECT space, rides the tumble ──
            if (MC > 0.001) {
                vec3 po = spRotAA(p, ax, th) * 26.0;
                vec2 e2 = vec2(0.05, 0.0);
                vec3 g3 = vec3(spN3(po + e2.xyy) - spN3(po - e2.xyy),
                               spN3(po + e2.yxy) - spN3(po - e2.yxy),
                               spN3(po + e2.yyx) - spN3(po - e2.yyx));
                n = normalize(n + g3 * MC * 0.55);
            }
            vec3 Ld = normalize(vec3(-0.5, 0.7, -0.6));    // the one sun
            float lam = max(0.0, dot(n, Ld));
            float rimL = pow(1.0 - max(0.0, dot(n, vec3(0.0, 0.0, -1.0))), 2.0);
            float spec = pow(max(0.0, dot(reflect(-Ld, n), vec3(0.0, 0.0, -1.0))), 24.0);
            float vol = 0.14 + 0.72 * lam + 0.30 * rimL * (1.0 + 0.8 * MC) + spec * (0.35 + 0.95 * W + 0.8 * MC);
            if (MC > 0.001) {                              // SEM detector grain, strongest on slopes
                float gn = spN3(spRotAA(p, ax, th) * 90.0);
                vol *= 1.0 + MC * 0.30 * (gn - 0.5) * (0.5 + rimL);
            }
            float body = mix(0.92, vol, EM);               // Emboss 0 = flat silhouette: bistable tumble

            float rim = 1.0 - abs(n.z);                    // toon silhouette measure
            float th2 = 1.0 - mix(0.5, 0.10, ST);
            float inkM = strokeOn * 0.85 * smoothstep(th2 - 0.03, th2 + 0.03, rim);
            float shoulder = smoothstep(th2 - 0.30, th2, rim);          // Cornsweet: brighten toward the ink
            float pinna = smoothstep(th2 - 0.09, th2 - 0.03, rim) * (1.0 - smoothstep(th2 - 0.03, th2, rim));
            body *= 1.0 + 0.20 * strokeOn * shoulder;
            body += 0.30 * strokeOn * pinna;
            col = vec3(body) * (1.0 - inkM);
            aOut = 1.0;
        } else {
            float halo = (1.0 - smoothstep(0.0, e3, mind)) * 0.85;      // Edge: near-miss glow
            halo *= (1.0 - strokeOn);                                   // the ink is the boundary
            col = vec3(halo);
            aOut = halo;
            if (SH > 0.001) {
                float sm = spSilT(vec3(s - vec2(0.26, -0.30) * SH, -2.0), ax, th, ra, rb, W, wr);
                aOut = max(aOut, SH * 0.55 * sm * (1.0 - halo));
            }
            if (DR > 0.001) {
                float dm = spSilT(vec3(s - vec2(0.72, -0.80) * DR, -2.0), ax, th, ra, rb, W, wr);
                aOut = max(aOut, DR * 0.40 * dm * (1.0 - halo));
            }
        }
    }
    gl_FragColor = vec4(min(col, vec3(1.0)), aOut);        // object only, transparent world
}
