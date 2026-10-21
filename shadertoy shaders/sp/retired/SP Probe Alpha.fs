/*{
  "DESCRIPTION": "probe: paints the input's alpha as brightness (temporary diagnostic)",
  "CREDIT": "SP",
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
      "NAME": "what",
      "LABEL": "What",
      "TYPE": "long",
      "DEFAULT": 0,
      "VALUES": [
        0,
        1,
        2
      ],
      "LABELS": [
        "alpha",
        "rgb",
        "max rgb minus alpha"
      ]
    }
  ]
}*/

void main() {
    vec4 s = IMG_THIS_PIXEL(inputImage);
    vec3 o = vec3(s.a);
    if (what == 1) o = s.rgb;
    if (what == 2) o = vec3(clamp(max(max(s.r, s.g), s.b) - s.a, 0.0, 1.0));
    gl_FragColor = vec4(o, 1.0);
}
