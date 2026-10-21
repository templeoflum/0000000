/*{
  "CREDIT": "by mojovideotech",
  "CATEGORIES": [
    "generator"
  ],
  "INPUTS": [
    {
      "NAME": "radialDensity",
      "TYPE": "float",
      "DEFAULT": 25.0,
      "MIN": 3.0,
      "MAX": 45.0
    },
    {
      "NAME": "angularDensity",
      "TYPE": "float",
      "DEFAULT": 16.0,
      "MIN": 2.0,
      "MAX": 28.0
    },
    {
      "NAME": "blendThreshold",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.1,
      "MAX": 0.9
    },
    {
      "NAME": "blendWidth",
      "TYPE": "float",
      "DEFAULT": 0.5,
      "MIN": 0.05,
      "MAX": 0.8
    },
    {
      "NAME": "phase",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 6.283185
    },
    {
      "NAME": "hue",
      "TYPE": "float",
      "DEFAULT": 0.0,
      "MIN": 0.0,
      "MAX": 1.0
    }
  ],
  "DESCRIPTION": "Heart control-ready Field copy; original preserved. "
}*/
float safeMod(float x,float y){float d=abs(y)<0.00001?(y<0.0?-0.00001:0.00001):y;return mod(x,d);}


// oncentrip by mojovideotech
// based on:
// glslsandbox.com/e#15230.2

#ifdef GL_ES
precision mediump float;
#endif

#define pi 3.14159265358
#define p 0.15915494309
#define threshold blendThreshold
#define overlap blendWidth

vec3 rgbFromHSV(float H, float S, float V) 
{
	H = fract(H + hue);
 float R; float G; float B;
	if ( S == 0. ) 
	{
		R = V; G = V; B = V;
	}
	else 
	{
		float var_h = H * 6.;
		if( var_h == 6. ) var_h = 0.;
		float var_i = floor( var_h );
		float var_1 = V * ( 1. - S );
		float var_2 = V * ( 1. - S * ( var_h - var_i ) );
		float var_3 = V * ( 1. - S * ( 1. - ( var_h - var_i ) ) );
		if	( var_i == 0. )	{ R = V     ; 	G = var_3 ; 	B = var_1	; }
		else if	( var_i == 1. )	{ R = var_2 ; 	G = V     ; 	B = var_1	; }
		else if	( var_i == 2. )	{ R = var_1 ; 	G = V     ; 	B = var_3	; }
		else if	( var_i == 3. )	{ R = var_1 ; 	G = var_2 ; 	B = V		; }
		else if	( var_i == 4. )	{ R = var_3 ; 	G = var_1 ; 	B = V		; }
		else			{ R = V     ; 	G = var_1 ; 	B = var_2	; }

	}
	return vec3(R,G,B);
}

void main( void ) 
{
	vec2 position = ( gl_FragCoord.xy / RENDERSIZE.x );
	float n = 2.0*atan(-position.y+0.25,position.x-0.5)*p+0.5;
	float a = pow(distance(position.yx+0.125,position.xy-0.125),cos(position.y*sin(p)));
	float l = length(position-vec2(cos(1.25-safeMod(p,(TIME+phase))),sin(0.5-safeMod(p,(TIME+phase)))));
	vec3 color1 = vec3(mod(a+l*radialDensity-(TIME+phase),1.0))*vec3(0.3,0.5,1.0);
	vec3 color2 = vec3(mod(a+l*radialDensity+(TIME+phase),1.0))*vec3(0.5,0.5,0.0);
		 color1 += vec3(safeMod(n/max(a,0.00001)*angularDensity-(TIME+phase),atan(sin((TIME+phase)+cos(p)))))*rgbFromHSV(2.0*l, 1.0, 0.5)-0.25;
		 color2 += vec3(safeMod(n/max(a,0.00001)*angularDensity+(TIME+phase),atan(sin((TIME+phase)+sin(p)))))*rgbFromHSV(2.0*l, 1.0, 0.5)+0.25;
	float factor = smoothstep(threshold-overlap, threshold+overlap, a);
	gl_FragColor = vec4(mix(color1, color2, vec3(factor)), 1.0);
}