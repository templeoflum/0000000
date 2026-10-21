# Dependency and routing contract v1

September 7, 2026. Implementation: `sp/engine/dependencies.py`. Offline worker scope:
no live calls or native mutations. Root owns integration and live acceptance.

## Integration

- `build_contract(snapshot_path, live_comp=None, layers=patch['layers'])` returns
  a JSON-safe manifest; raises `ContractError` for unsupported or ambiguous evidence.
  Legacy patches may build from their XML alone.
- `validate_contract(contract, snapshot_path, live_comp=None, sources=None,
  effects=None, observed_snapshot_path=None)` returns error strings; an empty list
  means the requested checks passed. Installed `/sources` and `/effects` video
  inventories are required. Without live composition this is **offline** preflight.
- For post-open readiness supply `live_comp` and `observed_snapshot_path`, a
  separately captured fresh native save after upstream launches. Never pass the
  archived input snapshot as purported fresh evidence. Caller owns freshness and
  transport settlement; this pure module cannot attest how a file was obtained.

Checks cover saved active clips, source dimensions, composition dimensions,
scoped ordered video effects on composition/groups/all layers/active clips,
exact required source/effect native identifiers, ordered group membership, layer order, and
serialized router settings including Input Opacity and Input Bypass/Solo.
Inactive library clip plugins are not required. Layer effects remain required even
on currently empty layers: those stacks are retained performance controls.
Duplicate layer names and ambiguous selected clip names fail closed.
Levels, ordinary shader parameter values, and runtime instance/parameter IDs are
not identities and are not compared. This module does not verify drive behavior,
buffer contents, mixer math, arbitrary audio or advanced output routing.

## Evidence and boundaries

Fixtures are `baseline/routing-current.json`, `installed-sources.json`,
`installed-effects.json`, `native-routing-readback.avc`, and the saved
`sp/engine/patches/Feedback shaping.{json,avc}`.

Installed identifier comparisons are exact, except syntactically valid UUID
letters are case-insensitive. No prefixes (including `c_`) are stripped and no
plugins are matched by display name. XML built-in `CompositionRouterVideoSource`
corresponds to installed `COMPOSITION_ROUTER_SRC`; Transform's actual XML
identifier `17122039101699797593` is present verbatim in the effects inventory.
The current Wire IDs also match inventory IDs verbatim.

Current REST readback returns `sourceparams: null` for all four active routers and
has effect display/internal names but no native plugin type identifier. Therefore
REST alone cannot verify live routes or native plugin identity. Fresh native save
comparison supplies those missing facts; REST independently checks dimensions,
order and group membership. If future REST exposes semantic Input options,
selected label comparisons are supported; numeric IDs and ordinal guesses are not.

Saved Feedback Input is `3:2`, sculpt is `1:1`, delay is `3:5`.
The texture/dither router omits its settings entirely: the manifest preserves
native default serialization exactly and never labels a guessed endpoint. This
is serialized configuration equality, not an independent visual proof that an
upstream image reaches the expected downstream instrument. Engine/version changes
or different default behavior require renewed live routing review.

## Tests

21 deterministic tests pass: actual fresh native snapshot equality, wrong route
with unchanged layout, missing group member, changed source dimensions, missing
required Wire plugin, same display name with wrong identifier, live and XML runtime
ID replacement success, semantic route mismatch, effect order, duplicate names,
inactive library exclusion, unavailable inventory, XML-only legacy build and UUID
case normalization. Inactive deck duplicates are ignored; current deck ambiguity and
changed layer order (which could reinterpret route ordinals) fail. No GPU or local inference was used.
