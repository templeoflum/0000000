// METADATA: template-shader
// TAGS: template, example
// PARAMS: param1(0.0, 1.0, 0.5), param2(0.0, 10.0, 1.0)

#ifdef GL_ES
precision highp float;
#endif

// Built-in uniforms (automatically provided by viewer)
uniform float u_time;        // Time in seconds since start
uniform vec2 u_resolution;   // Canvas resolution (width, height)

// Custom uniforms (exposed as sliders in GUI)
uniform float param1;
uniform float param2;

// Main shader function
// gl_FragCoord: current pixel position
// gl_FragColor: output color (RGBA, 0-1 range)
void main() {
    // Normalize coordinates to [0, 1]
    vec2 uv = gl_FragCoord.xy / u_resolution.xy;
    
    // Center coordinates around (0, 0)
    vec2 st = uv * 2.0 - 1.0;
    st.x *= u_resolution.x / u_resolution.y; // Correct aspect ratio
    
    // Example: animated pattern
    float d = length(st);
    float t = u_time * param2;
    
    float pattern = sin(d * 10.0 - t) * 0.5 + 0.5;
    pattern *= param1;
    
    // Output color
    vec3 color = vec3(pattern);
    gl_FragColor = vec4(color, 1.0);
}

/*
IMPLEMENTATION NOTES:

This is a template shader showing the basic structure.

Standard uniforms:
- u_time: Use for animation
- u_resolution: Use for aspect ratio correction

Coordinate systems:
- uv: [0,1] normalized screen space
- st: [-1,1] centered, aspect-corrected space

Common patterns:
- length(st): distance from center
- atan(st.y, st.x): angle from center
- fract(): for tiling/repetition
- mix(): for smooth transitions
- step()/smoothstep(): for sharp/smooth edges

Physics shader tips:
- Use u_time for temporal evolution
- Map physical parameters to shader uniforms
- Discretize differential equations in the shader
- Use texture samplers for state that needs history
*/
