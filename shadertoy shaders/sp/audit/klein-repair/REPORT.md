# Heart Klein Bottle

New copy installed in Figure L5C71; original Klein Bottle (3D) L5C52 and its files are preserved. The Heart copies bank includes the replacement.

Fixed quaternion component ordering and zero-norm handling. Camera and FOV are fixed; rendering uses the short resolution dimension. Removed the original unused Speed input. Exposed wall thickness and exposure. Replaced the out-of-range light attenuation with bounded Fresnel attenuation and a small fill contribution; applied display gamma after exposure. Refraction uses normalized incident rays, an air-to-material index ratio, face-forward normals and reflection fallback for zero transmitted rays. This remains the source's simplified multi-bounce appearance, not a physically complete glass model.

Validation: 14/14 manual targets across seven controls passed in live Heart/Resolume. Driven Quat Y native values varied and paired actual-output captures were visually reviewed. Six final local cases (wide/tall/square, zero quaternion and strong orientation/thickness) are nonempty with zero edge alpha. Fixed-view refraction endpoints produce different pixels, but the difference is subtle (mean summed RGBA difference 0.01067 on 0–255 scale). Do not describe Refraction as a large visual macro. These checks are sampled, not exhaustive containment or smoothness certification. Home/Settle profile remains unverified.

Primary practical controls: orientation, wall thickness and exposure. Framing leaves room for the shared Figure Transform and creative effects. The source is not yet added to the engine's proven-bound registry; shared guards therefore remain conservative pending a stronger bound analysis.
