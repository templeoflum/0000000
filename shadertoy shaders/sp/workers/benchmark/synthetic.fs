/*{
 "INPUTS": [
  {"NAME":"scale","LABEL":"Scale","TYPE":"float","MIN":0,"MAX":1},
  {"NAME":"speed","LABEL":"Speed","TYPE":"float","MIN":0,"MAX":2},
  {"NAME":"mode","LABEL":"Mode","TYPE":"long","VALUES":[0,1],"LABELS":["circle","stripes"]},
  {"NAME":"brightness","LABEL":"Brightness","TYPE":"float","MIN":0,"MAX":1}
 ]
}*/
// Synthetic benchmark, authored solely for public-cloud testing. No project shader code.
void main() {
 vec2 uv = isf_FragNormCoord - vec2(0.5);
 float phase = TIME * speed;
 float radius = 0.1 + scale * 0.4;
 float circle = 1.0 - smoothstep(radius, radius + 0.01, length(uv));
 float stripes = step(0.5, fract(uv.x * 10.0 + phase));
 float pattern = mode == 0 ? circle : stripes;
 gl_FragColor = vec4(vec3(pattern * brightness), 1.0);
}
