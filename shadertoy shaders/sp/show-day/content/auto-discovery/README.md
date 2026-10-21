# Automatic clip parameter discovery

Heart catalogs every occupied clip from its existing full-composition scan (normally every3seconds; sooner on rescan). The on-demand /clip-catalog.json endpoint exposes source parameter names, native types, ranges, options and IDs without adding the full catalog to the15Hz WebSocket payload. Inactive clips are indexed, never instantiated as running modulation controllers.

Active sources exposing supported native parameter types are automatically enrolled without a source-name allowlist. Existing Smart Params and authored defaults remain authoritative; new continuous controls start undriven. New control defaults are saved once per newly discovered source, not once per parameter. Schema replacement continues to rebuild bindings from current native IDs.

Live verification:303clips,2361exposed source parameters,302inactive clips indexed.248Python tests pass, including unregistered-source detection, inactive read-only inventory, schema changes and missing controls. Arena connected after reload. Shader uniforms which are not exposed by Wire/Resolume cannot be discovered here; triggers/toggles are cataloged as discrete controls rather than continuous drives. This does not add new trigger/toggle widgets or activate inactive clips.
