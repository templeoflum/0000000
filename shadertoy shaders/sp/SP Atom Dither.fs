/*{
  "DESCRIPTION": "SP Atom Dither - texture layer effect: 12 ordered dither patterns (real Bayer matrices, halftone, hex, hatch, rings, noise), Size, luminance / per-channel, Levels, Contrast, Bias, sampled or tinted colour, Cells (downsample); Engine = real console palettes at their native resolutions (authentic / x2), Scan(lines), Spacing, Tint, Key (opaque router feed: dark becomes open), Mix. No drives.",
  "CREDIT": "SP atom; references MTK Ditherx / Retrovision",
  "ISFVSN": "2",
  "CATEGORIES": [
    "Stylize"
  ],
  "INPUTS": [
    {
      "NAME": "inputImage",
      "TYPE": "image"
    },
    {
      "NAME": "pattern",
      "LABEL": "Pattern",
      "TYPE": "long",
      "DEFAULT": 1,
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
        11
      ],
      "LABELS": [
        "bayer 2x2",
        "bayer 4x4",
        "bayer 8x8",
        "halftone dots",
        "halftone lines",
        "checker",
        "noise",
        "hex dots",
        "crosshatch",
        "diamond",
        "rings",
        "value noise"
      ]
    },
    {
      "NAME": "sizev",
      "LABEL": "Size",
      "TYPE": "float",
      "DEFAULT": 4.0,
      "MIN": 1.0,
      "MAX": 40.0
    },
    {
      "NAME": "mode",
      "LABEL": "Mode",
      "TYPE": "long",
      "DEFAULT": 0,
      "VALUES": [
        0,
        1
      ],
      "LABELS": [
        "luminance",
        "per channel"
      ]
    },
    {
      "NAME": "levels",
      "LABEL": "Levels",
      "TYPE": "float",
      "DEFAULT": 2.0,
      "MIN": 2.0,
      "MAX": 16.0
    },
    {
      "NAME": "contrast",
      "LABEL": "Contrast",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.25,
      "MAX": 4.0
    },
    {
      "NAME": "bias",
      "LABEL": "Bias",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": -0.5,
      "MAX": 0.5
    },
    {
      "NAME": "color",
      "LABEL": "Color",
      "TYPE": "long",
      "DEFAULT": 0,
      "VALUES": [
        0,
        1
      ],
      "LABELS": [
        "sampled",
        "tinted"
      ]
    },
    {
      "NAME": "low",
      "LABEL": "Low",
      "TYPE": "color",
      "DEFAULT": [
        0.0,
        0.0,
        0.0,
        1.0
      ]
    },
    {
      "NAME": "high",
      "LABEL": "High",
      "TYPE": "color",
      "DEFAULT": [
        1.0,
        1.0,
        1.0,
        1.0
      ]
    },
    {
      "NAME": "dither",
      "LABEL": "Dither",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "cells",
      "LABEL": "Cells",
      "TYPE": "long",
      "DEFAULT": 0,
      "VALUES": [
        0,
        1
      ],
      "LABELS": [
        "off",
        "on"
      ]
    },
    {
      "NAME": "engine",
      "LABEL": "Engine",
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
        31,
        32
      ],
      "LABELS": [
        "none",
        "NES / Famicom",
        "Game Boy (DMG) - mono green",
        "Game Boy Pocket (MGB) - mono gray",
        "Game Boy Light (MGB-101) - mono warm/backlit",
        "Virtual Boy - mono red",
        "Game Boy Color (classic 16)",
        "Commodore 64",
        "Atari 2600",
        "ZX Spectrum",
        "PICO-8",
        "IBM PC EGA (16)",
        "Sega Master System",
        "SNES / Super Famicom (subset)",
        "Amiga OCS/ECS",
        "Apple II (6-color hi-res)",
        "Apple IIgs",
        "Sega Game Gear",
        "MSX (MSX1 / TMS9918, 16)",
        "Amstrad CPC",
        "TI-99/4A (TMS9918A, 16)",
        "NEC PC-9801 / PC-98",
        "IBM PC CGA",
        "IBM PC VGA (16)",
        "Tandy 1000 / PCjr (TGA 16)",
        "Hercules (amber mono)",
        "Macintosh 1-bit (B/W)",
        "NEC PC-8801 (PC-88, 8)",
        "Sharp X68000",
        "Atari ST",
        "BBC Micro (Mode 2, 8)",
        "PC Engine / TurboGrafx-16",
        "Sega Mega Drive / Genesis"
      ]
    },
    {
      "NAME": "native",
      "LABEL": "Native",
      "TYPE": "long",
      "DEFAULT": 0,
      "VALUES": [
        0,
        1
      ],
      "LABELS": [
        "authentic",
        "x2"
      ]
    },
    {
      "NAME": "scan",
      "LABEL": "Scan",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "spacing",
      "LABEL": "Spacing",
      "TYPE": "float",
      "DEFAULT": 3.0,
      "MIN": 1.0,
      "MAX": 12.0
    },
    {
      "NAME": "tint",
      "LABEL": "Tint",
      "TYPE": "long",
      "DEFAULT": 0,
      "VALUES": [
        0,
        1,
        2,
        3,
        4,
        5,
        6
      ],
      "LABELS": [
        "none",
        "amber",
        "green",
        "blue",
        "sepia",
        "warm lcd",
        "cool lcd"
      ]
    },
    {
      "NAME": "key",
      "LABEL": "Key",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    },
    {
      "NAME": "mixv",
      "LABEL": "Mix",
      "TYPE": "float",
      "DEFAULT": 1.0,
      "MIN": 0.0,
      "MAX": 1.0
    }
  ]
}*/

const vec3 PAL[357] = vec3[357](vec3(0.486,0.486,0.486),vec3(0.000,0.000,0.988),vec3(0.000,0.000,0.737),vec3(0.267,0.157,0.737),vec3(0.580,0.000,0.518),vec3(0.659,0.000,0.125),vec3(0.659,0.063,0.000),vec3(0.533,0.078,0.000),vec3(0.314,0.188,0.000),vec3(0.000,0.471,0.000),vec3(0.000,0.408,0.000),vec3(0.000,0.345,0.000),vec3(0.000,0.251,0.345),vec3(0.000,0.000,0.000),vec3(0.000,0.000,0.000),vec3(0.000,0.000,0.000),vec3(0.737,0.737,0.737),vec3(0.000,0.471,0.973),vec3(0.000,0.345,0.973),vec3(0.408,0.267,0.988),vec3(0.847,0.000,0.800),vec3(0.894,0.000,0.345),vec3(0.973,0.220,0.000),vec3(0.894,0.361,0.063),vec3(0.675,0.486,0.000),vec3(0.000,0.722,0.000),vec3(0.000,0.659,0.000),vec3(0.000,0.659,0.267),vec3(0.000,0.533,0.533),vec3(0.000,0.000,0.000),vec3(0.000,0.000,0.000),vec3(0.000,0.000,0.000),vec3(0.973,0.973,0.973),vec3(0.235,0.737,0.988),vec3(0.408,0.533,0.988),vec3(0.596,0.471,0.973),vec3(0.973,0.471,0.973),vec3(0.973,0.345,0.596),vec3(0.973,0.471,0.345),vec3(0.988,0.627,0.267),vec3(0.973,0.722,0.000),vec3(0.722,0.973,0.094),vec3(0.345,0.847,0.329),vec3(0.345,0.973,0.596),vec3(0.000,0.910,0.847),vec3(0.471,0.471,0.471),vec3(0.000,0.000,0.000),vec3(0.000,0.000,0.000),vec3(0.988,0.988,0.988),vec3(0.643,0.894,0.988),vec3(0.722,0.722,0.973),vec3(0.847,0.722,0.973),vec3(0.973,0.722,0.973),vec3(0.973,0.643,0.753),vec3(0.941,0.816,0.690),vec3(0.988,0.878,0.659),vec3(0.973,0.847,0.471),vec3(0.847,0.973,0.471),vec3(0.722,0.973,0.722),vec3(0.722,0.973,0.847),vec3(0.000,0.988,0.988),vec3(0.973,0.847,0.973),vec3(0.000,0.000,0.000),vec3(0.000,0.000,0.000),vec3(0.059,0.220,0.059),vec3(0.188,0.384,0.188),vec3(0.545,0.675,0.059),vec3(0.608,0.737,0.059),vec3(0.094,0.094,0.094),vec3(0.290,0.318,0.220),vec3(0.549,0.573,0.420),vec3(0.773,0.792,0.643),vec3(0.000,0.310,0.227),vec3(0.000,0.412,0.290),vec3(0.000,0.604,0.439),vec3(0.000,0.710,0.510),vec3(0.000,0.000,0.000),vec3(0.333,0.000,0.000),vec3(0.643,0.000,0.000),vec3(0.937,0.000,0.000),vec3(0.000,0.000,0.000),vec3(1.000,1.000,1.000),vec3(0.482,1.000,0.192),vec3(0.000,0.388,0.773),vec3(1.000,0.518,0.518),vec3(0.580,0.227,0.227),vec3(1.000,0.678,0.388),vec3(0.518,0.192,0.000),vec3(0.322,1.000,0.000),vec3(1.000,0.259,0.000),vec3(0.388,0.647,1.000),vec3(0.000,0.000,1.000),vec3(1.000,1.000,0.000),vec3(1.000,0.000,0.000),vec3(0.647,0.647,0.647),vec3(0.322,0.322,0.322),vec3(0.000,0.000,0.000),vec3(1.000,1.000,1.000),vec3(0.408,0.216,0.169),vec3(0.439,0.643,0.698),vec3(0.435,0.239,0.525),vec3(0.345,0.553,0.263),vec3(0.208,0.157,0.475),vec3(0.722,0.780,0.435),vec3(0.435,0.310,0.145),vec3(0.263,0.224,0.000),vec3(0.604,0.404,0.349),vec3(0.267,0.267,0.267),vec3(0.424,0.424,0.424),vec3(0.604,0.824,0.518),vec3(0.424,0.369,0.710),vec3(0.584,0.584,0.584),vec3(0.000,0.000,0.000),vec3(0.310,0.310,0.310),vec3(0.620,0.620,0.620),vec3(0.929,0.929,0.929),vec3(0.329,0.173,0.024),vec3(0.737,0.384,0.059),vec3(0.941,0.604,0.294),vec3(0.973,0.831,0.702),vec3(0.329,0.286,0.024),vec3(0.737,0.643,0.059),vec3(0.941,0.851,0.294),vec3(0.973,0.937,0.702),vec3(0.259,0.329,0.024),vec3(0.576,0.737,0.059),vec3(0.784,0.941,0.294),vec3(0.910,0.973,0.702),vec3(0.141,0.329,0.024),vec3(0.318,0.737,0.059),vec3(0.541,0.941,0.294),vec3(0.804,0.973,0.702),vec3(0.024,0.329,0.024),vec3(0.059,0.737,0.059),vec3(0.294,0.941,0.294),vec3(0.702,0.973,0.702),vec3(0.024,0.329,0.141),vec3(0.059,0.737,0.318),vec3(0.294,0.941,0.541),vec3(0.702,0.973,0.804),vec3(0.024,0.329,0.259),vec3(0.059,0.737,0.576),vec3(0.294,0.941,0.784),vec3(0.702,0.973,0.910),vec3(0.024,0.286,0.329),vec3(0.059,0.643,0.737),vec3(0.294,0.851,0.941),vec3(0.702,0.937,0.973),vec3(0.024,0.173,0.329),vec3(0.059,0.384,0.737),vec3(0.294,0.604,0.941),vec3(0.702,0.831,0.973),vec3(0.024,0.055,0.329),vec3(0.059,0.125,0.737),vec3(0.294,0.361,0.941),vec3(0.702,0.729,0.973),vec3(0.110,0.024,0.329),vec3(0.247,0.059,0.737),vec3(0.475,0.294,0.941),vec3(0.776,0.702,0.973),vec3(0.227,0.024,0.329),vec3(0.506,0.059,0.737),vec3(0.722,0.294,0.941),vec3(0.882,0.702,0.973),vec3(0.329,0.024,0.318),vec3(0.737,0.059,0.710),vec3(0.941,0.294,0.914),vec3(0.973,0.702,0.965),vec3(0.329,0.024,0.204),vec3(0.737,0.059,0.451),vec3(0.941,0.294,0.671),vec3(0.973,0.702,0.859),vec3(0.329,0.024,0.086),vec3(0.737,0.059,0.192),vec3(0.941,0.294,0.424),vec3(0.973,0.702,0.757),vec3(0.000,0.000,0.000),vec3(0.000,0.000,0.843),vec3(0.843,0.000,0.000),vec3(0.843,0.000,0.843),vec3(0.000,0.843,0.000),vec3(0.000,0.843,0.843),vec3(0.843,0.843,0.000),vec3(0.843,0.843,0.843),vec3(0.000,0.000,0.000),vec3(0.000,0.000,1.000),vec3(1.000,0.000,0.000),vec3(1.000,0.000,1.000),vec3(0.000,1.000,0.000),vec3(0.000,1.000,1.000),vec3(1.000,1.000,0.000),vec3(1.000,1.000,1.000),vec3(0.000,0.000,0.000),vec3(0.114,0.169,0.325),vec3(0.494,0.145,0.325),vec3(0.000,0.529,0.318),vec3(0.671,0.322,0.212),vec3(0.373,0.341,0.310),vec3(0.761,0.765,0.780),vec3(1.000,0.945,0.910),vec3(1.000,0.000,0.302),vec3(1.000,0.639,0.000),vec3(1.000,0.925,0.153),vec3(0.000,0.894,0.212),vec3(0.161,0.678,1.000),vec3(0.514,0.463,0.612),vec3(1.000,0.467,0.659),vec3(1.000,0.800,0.667),vec3(0.000,0.000,0.000),vec3(0.000,0.000,0.667),vec3(0.000,0.667,0.000),vec3(0.000,0.667,0.667),vec3(0.667,0.000,0.000),vec3(0.667,0.000,0.667),vec3(0.667,0.333,0.000),vec3(0.667,0.667,0.667),vec3(0.333,0.333,0.333),vec3(0.333,0.333,1.000),vec3(0.333,1.000,0.333),vec3(0.333,1.000,1.000),vec3(1.000,0.333,0.333),vec3(1.000,0.333,1.000),vec3(1.000,1.000,0.333),vec3(1.000,1.000,1.000),vec3(0.000,0.000,0.000),vec3(0.808,0.176,1.000),vec3(0.192,0.824,0.000),vec3(1.000,0.337,0.000),vec3(0.000,0.663,1.000),vec3(1.000,1.000,1.000),vec3(0.000,0.000,0.000),vec3(0.000,0.000,0.000),vec3(0.251,0.718,0.290),vec3(0.459,0.812,0.494),vec3(0.349,0.333,0.871),vec3(0.251,0.592,0.937),vec3(0.722,0.373,0.318),vec3(0.400,0.859,0.933),vec3(0.851,0.400,0.353),vec3(0.992,0.541,0.494),vec3(0.800,0.765,0.376),vec3(0.871,0.816,0.533),vec3(0.231,0.631,0.259),vec3(0.714,0.404,0.706),vec3(0.800,0.800,0.800),vec3(1.000,1.000,1.000),vec3(0.000,0.000,0.000),vec3(0.000,0.000,0.502),vec3(0.000,0.000,1.000),vec3(0.502,0.000,0.000),vec3(0.502,0.000,0.502),vec3(0.502,0.000,1.000),vec3(1.000,0.000,0.000),vec3(1.000,0.000,0.502),vec3(1.000,0.000,1.000),vec3(0.000,0.502,0.000),vec3(0.000,0.502,0.502),vec3(0.000,0.502,1.000),vec3(0.502,0.502,0.000),vec3(0.502,0.502,0.502),vec3(0.502,0.502,1.000),vec3(1.000,0.502,0.000),vec3(1.000,0.502,0.502),vec3(1.000,0.502,1.000),vec3(0.000,1.000,0.000),vec3(0.000,1.000,0.502),vec3(0.000,1.000,1.000),vec3(0.502,1.000,0.000),vec3(0.502,1.000,0.502),vec3(0.502,1.000,1.000),vec3(1.000,1.000,0.000),vec3(1.000,1.000,0.502),vec3(1.000,1.000,1.000),vec3(0.000,0.000,0.000),vec3(0.000,0.000,0.000),vec3(0.129,0.784,0.259),vec3(0.369,0.863,0.471),vec3(0.329,0.333,0.929),vec3(0.490,0.463,0.988),vec3(0.831,0.322,0.302),vec3(0.259,0.922,0.961),vec3(0.988,0.333,0.329),vec3(1.000,0.475,0.471),vec3(0.831,0.757,0.329),vec3(0.902,0.808,0.502),vec3(0.129,0.690,0.231),vec3(0.788,0.357,0.729),vec3(0.800,0.800,0.800),vec3(1.000,1.000,1.000),vec3(0.000,0.000,0.000),vec3(0.000,0.000,0.667),vec3(0.000,0.667,0.000),vec3(0.000,0.667,0.667),vec3(0.667,0.000,0.000),vec3(0.667,0.000,0.667),vec3(0.667,0.333,0.000),vec3(0.667,0.667,0.667),vec3(0.333,0.333,0.333),vec3(0.333,0.333,1.000),vec3(0.333,1.000,0.333),vec3(0.333,1.000,1.000),vec3(1.000,0.333,0.333),vec3(1.000,0.333,1.000),vec3(1.000,1.000,0.333),vec3(1.000,1.000,1.000),vec3(0.000,0.000,0.000),vec3(0.000,0.000,0.667),vec3(0.000,0.667,0.000),vec3(0.000,0.667,0.667),vec3(0.667,0.000,0.000),vec3(0.667,0.000,0.667),vec3(0.667,0.333,0.000),vec3(0.667,0.667,0.667),vec3(0.333,0.333,0.333),vec3(0.333,0.333,1.000),vec3(0.333,1.000,0.333),vec3(0.333,1.000,1.000),vec3(1.000,0.333,0.333),vec3(1.000,0.333,1.000),vec3(1.000,1.000,0.333),vec3(1.000,1.000,1.000),vec3(0.000,0.000,0.000),vec3(0.000,0.000,0.667),vec3(0.000,0.667,0.000),vec3(0.000,0.667,0.667),vec3(0.667,0.000,0.000),vec3(0.667,0.000,0.667),vec3(0.667,0.333,0.000),vec3(0.667,0.667,0.667),vec3(0.333,0.333,0.333),vec3(0.333,0.333,1.000),vec3(0.333,1.000,0.333),vec3(0.333,1.000,1.000),vec3(1.000,0.333,0.333),vec3(1.000,0.333,1.000),vec3(1.000,1.000,0.333),vec3(1.000,1.000,1.000),vec3(0.000,0.000,0.000),vec3(1.000,0.690,0.000),vec3(0.000,0.000,0.000),vec3(1.000,1.000,1.000),vec3(0.000,0.000,0.000),vec3(0.000,0.000,1.000),vec3(1.000,0.000,0.000),vec3(1.000,0.000,1.000),vec3(0.000,1.000,0.000),vec3(0.000,1.000,1.000),vec3(1.000,1.000,0.000),vec3(1.000,1.000,1.000),vec3(0.000,0.000,0.000),vec3(1.000,0.000,0.000),vec3(0.000,1.000,0.000),vec3(1.000,1.000,0.000),vec3(0.000,0.000,1.000),vec3(1.000,0.000,1.000),vec3(0.000,1.000,1.000),vec3(1.000,1.000,1.000));
const int ENG_KIND[33] = int[33](0,1,1,1,1,1,1,1,1,1,1,1,2,2,2,1,2,2,1,1,1,2,1,1,1,1,1,1,2,2,1,2,2);
const int ENG_START[33] = int[33](0,0,64,68,72,76,80,96,112,176,192,208,0,0,0,224,0,0,230,246,273,0,289,305,321,337,339,341,0,0,349,0,0);
const int ENG_COUNT[33] = int[33](0,64,4,4,4,4,16,16,64,16,16,16,0,0,0,6,0,0,16,27,16,0,16,16,16,2,2,8,0,0,8,0,0);
const int ENG_BITS[33] = int[33](0,0,0,0,0,0,0,0,0,0,0,0,2,5,4,0,4,4,0,0,0,4,0,0,0,0,0,0,5,3,0,3,3);
const vec2 ENG_RES[33] = vec2[33](vec2(0,0),vec2(256,240),vec2(160,144),vec2(160,144),vec2(160,144),vec2(384,224),vec2(160,144),vec2(320,200),vec2(160,192),vec2(256,192),vec2(128,128),vec2(320,200),vec2(256,192),vec2(256,224),vec2(320,256),vec2(280,192),vec2(320,200),vec2(160,144),vec2(256,192),vec2(160,200),vec2(256,192),vec2(640,400),vec2(320,200),vec2(320,200),vec2(320,200),vec2(720,348),vec2(512,342),vec2(640,200),vec2(256,256),vec2(320,200),vec2(160,256),vec2(256,224),vec2(320,224));
const int NE = 33;

float h21(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float vnoise(vec2 p) { vec2 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f);
    return mix(mix(h21(i), h21(i + vec2(1, 0)), f.x), mix(h21(i + vec2(0, 1)), h21(i + vec2(1, 1)), f.x), f.y); }
// Bayer by bit interleaving: the exact recursive matrix, any power of two
float bayer(vec2 p, int n) {
    int x = int(mod(p.x, float(n))), y = int(mod(p.y, float(n))); float v = 0.0, s = 0.5;
    for (int i = 0; i < 3; i++) {
        if (i >= (n == 2 ? 1 : (n == 4 ? 2 : 3))) break;
        int xb = (x >> i) & 1, yb = (y >> i) & 1;
        v += float(xb ^ yb) * s; s *= 0.5; v += float(yb) * s; s *= 0.5;
    }
    return v + s;                                            // centre of the cell's slot: (index + 0.5) / n²
}
// the threshold in (0,1) for pixel p (in pattern pixels): the 12 patterns
float threshold(vec2 p, int pat) {
    if (pat == 0) return bayer(p, 2);
    if (pat == 1) return bayer(p, 4);
    if (pat == 2) return bayer(p, 8);
    vec2 c = fract(p / 6.0) - 0.5;                           // a 6-px cell for the analytic patterns
    if (pat == 3) return clamp(length(c) / 0.7071, 0.0, 1.0);                         // halftone dots: grow from the centre
    if (pat == 4) return abs(fract(p.y / 6.0) - 0.5) * 2.0;                             // halftone lines: grow from the row centre
    if (pat == 5) return mod(floor(p.x) + floor(p.y), 2.0) * 0.5 + 0.25;                // checker: two levels
    if (pat == 6) return h21(floor(p));                                                 // noise ordered: white-noise threshold
    if (pat == 7) { vec2 q = p / 6.0; vec2 r = vec2(1.0, 1.732); vec2 a = mod(q, r) - r * 0.5, b = mod(q - r * 0.5, r) - r * 0.5;   // hex dots
                    return clamp(min(length(a), length(b)) / 0.6, 0.0, 1.0); }
    if (pat == 8) { float l1 = abs(fract((p.x + p.y) / 6.0) - 0.5) * 2.0, l2 = abs(fract((p.x - p.y) / 6.0) - 0.5) * 2.0; return min(l1, l2); }   // crosshatch
    if (pat == 9) return clamp((abs(c.x) + abs(c.y)) / 0.7, 0.0, 1.0);                  // diamond: L1 distance
    if (pat == 10) return fract(length(p - 0.5 * RENDERSIZE.xy / max(sizev, 1.0)) / 4.0);   // rings: concentric from the frame centre
    return vnoise(p / 3.0);                                                              // value noise ordered
}
vec3 quantLevels(vec3 v, float t, float Q) { return floor(v * (Q - 1.0) + t) / (Q - 1.0); }
// nearest palette entry, by a perceptual distance (luma-weighted channels), as a real palette match would be judged
vec3 nearestPal(vec3 v, int start, int count) {
    vec3 best = vec3(0.0); float bd = 1e9; const vec3 W = vec3(0.30, 0.59, 0.11) * 3.0;
    for (int i = 0; i < 64; i++) { if (i >= count) break; vec3 c = PAL[start + i]; vec3 e = (v - c) * W; float d = dot(e, e); if (d < bd) { bd = d; best = c; } }
    return best;
}
// ordered dither against an arbitrary palette: the nearest entry, and the entry on the far side of the value; the threshold
// picks between them by where the value sits on the line joining them. A value beyond the palette's end never dithers.
vec3 ditherPal(vec3 v, float t, float amt, int start, int count) {
    vec3 c1 = nearestPal(v, start, count);
    vec3 c2 = nearestPal(clamp(v + (v - c1) * amt, 0.0, 1.0), start, count);
    vec3 d = c2 - c1; float l2 = dot(d, d); if (l2 < 1e-6) return c1;
    float f = clamp(dot(v - c1, d) / l2, 0.0, 1.0);
    return (t < f) ? c2 : c1;
}
void main() {
    vec2 px = gl_FragCoord.xy;
    int eng = int(clamp(float(engine), 0.0, float(NE - 1)));
    int kind = ENG_KIND[eng];
    // ── cells: the sampling grid. An engine's native resolution sets it (true cell-block scaling); else Size; x2 halves the cell ──
    vec2 cellPx = vec2(sizev);
    if (kind > 0) { vec2 res = ENG_RES[eng]; float sc = max(RENDERSIZE.y / res.y, 1.0); if (native == 1) sc *= 0.5; cellPx = vec2(sc); }
    vec2 cell = floor(px / cellPx);
    vec2 samp = (cells == 1 || kind > 0) ? (cell + 0.5) * cellPx : px;      // downsample: one sample per cell
    vec4 src = IMG_NORM_PIXEL(inputImage, samp / RENDERSIZE.xy);
    float a = src.a;
    if (a <= 0.002) { gl_FragColor = vec4(0.0); return; }    // nothing there stays nothing
    vec3 v = src.rgb / a;                                    // the router hands us premultiplied pixels: work on the colour itself
    v = (v - 0.5) * contrast + 0.5 + bias;
    // ── the dither threshold, in pattern pixels = cells ──
    float t = threshold(cell, pattern);
    float td = mix(0.5, t, dither);                          // Dither: 0 = plain quantize, 1 = the full pattern
    vec3 outc;
    if (kind == 0) {
        float Q = floor(levels + 0.5);
        if (mode == 0) { float l = dot(v, vec3(0.299, 0.587, 0.114)); float q = quantLevels(vec3(l), td, Q).x;
            outc = (color == 1) ? mix(low.rgb, high.rgb, q) : clamp(v * (q / max(l, 1e-4)), 0.0, 1.0); }
        else { vec3 q = quantLevels(v, td, Q); outc = (color == 1) ? mix(low.rgb, high.rgb, q) : q; }
    } else if (kind == 2) {                                  // rgb-bit hardware: each channel to its levels, dithered
        float Q = float(1 << ENG_BITS[eng]); outc = quantLevels(clamp(v, 0.0, 1.0), td, Q);
    } else {                                                 // fixed hardware palette: dither toward the nearest entry
        outc = ditherPal(clamp(v, 0.0, 1.0), t, dither, ENG_START[eng], ENG_COUNT[eng]);
    }
    // ── scanlines: darken every 'spacing' rows, by 'scan' ──
    float sl = 1.0 - scan * 0.9 * (0.5 + 0.5 * cos(6.2831853 * px.y / max(spacing, 1.0)));
    outc *= sl;
    // ── tint: a phosphor / LCD cast on the result's luminance ──
    if (tint > 0) { float l = dot(outc, vec3(0.299, 0.587, 0.114)); vec3 tc = vec3(1.0);
        if (tint == 1) tc = vec3(1.0, 0.69, 0.0); else if (tint == 2) tc = vec3(0.2, 1.0, 0.3); else if (tint == 3) tc = vec3(0.35, 0.55, 1.0);
        else if (tint == 4) tc = vec3(1.0, 0.85, 0.62); else if (tint == 5) tc = vec3(0.61, 0.73, 0.06) * 1.3; else tc = vec3(0.55, 0.75, 0.85) * 1.15;
        outc = tc * l; }
    vec3 res = mix(src.rgb / a, clamp(outc, 0.0, 1.0), mixv);
    // Key: a Video Router hands over an opaque frame (measured: alpha 1 everywhere), so the black it carries is not
    // transparency. Key makes it so: alpha follows the RESULT's brightness, dark to Key's threshold becomes open.
    // At 0 alpha is untouched. With a dither the pattern itself becomes the mask, and what is beneath shows through the dots.
    if (key > 0.001) { float l = max(max(res.r, res.g), res.b); a *= smoothstep(0.0, key, l); }
    gl_FragColor = vec4(res * a, a);                         // premultiplied out
}
