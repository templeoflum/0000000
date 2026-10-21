# New corpus wrappers — offline crash diagnosis

**Stronger finding: Arena throws `std::range_error("wstring_convert: to_bytes error")` inside libwire during Project Manager work.** This is established from the exact offsets in `Arena-2026-09-09-100233.ips`, statically disassembled from the matching installed `libwire.dylib` (UUID9ea71b68-4454-35b5-be0e-e5b6b0d1811a). No app was launched or attached to.

- `0xda62b4` loads the error string; `0xda62bc` calls the throw helper at`0xb1d584`.
- That helper loads `__ZTISt11range_error` and calls`__cxa_throw`; the recorded return frame is`0xb1d5c0`.
- The log watches Hering's package/resources at10:02:33.296–.297 without registering it. Pinna registers successfully at10:02:33.295 in the same startup. No Café Wall/Fraser entries were found in this retained log. Hering is the strongest implicated package; the other two remain unaccepted, not exonerated.

## What the files establish

Quarantined wrappers parse as JSON, have distinct valid UUIDs, existing resource paths, matching cached and source-header inputs, correct inlet connections and valid input-order references. Bool/integer primitives are correctly typed. Float fields containing integer literals also occur in working Barberpole; that difference is not enough to name a cause.

Every quarantined file decodes as strict UTF-8. Parsed metadata has no surrogate codepoints. Only Hering has non-ASCII metadata (the en dash in `rounds12–180`), but working Pinna also has an en dash and registers successfully. Shared Unicode GLSL comments are identical across these sources and Pinna. Therefore **ordinary Unicode is not proven to be the defect**. The failing converted string could be created internally; the exception alone cannot identify it.

## Concrete validation/fix proposal — not applied

`hering-ascii-metadata-proposal.json` specifies a single-variable change: replace that en dash with an ASCII hyphen in Hering's ISF DESCRIPTION and corresponding wrapper meta.description, preserving shader calculations, inputs, graph and identity. This is a diagnostic normalization, not a confirmed fix. It has not been applied to quarantined, staged or installed files.

For a later controlled validation window owned by the main task:

1. Keep all three originals quarantined and the working scan directory untouched now.
2. Test Hering alone with that metadata-only change in an isolated/recoverable application environment. Acceptance requires completed native registration and repeated clean reopen, then actual output. glslang or offscreen pixels cannot validate this conversion path.
3. If still failing, an identical-header/wrapper fixture with a minimal neutral shader body separates source-body/import processing from graph/metadata. If neutral loads, restore original body in bounded pieces; if neutral fails, compare the same body/header against a working Pinna-derived wrapper with explicit name remapping. Do not claim a production repair from a single successful run.
4. Café Wall and Fraser require individual native acceptance afterward. Bulk reinstatement would lose attribution and recreate startup risk.

No live rollout is proposed during original-content recovery. No Arena/Wire operations, reinstallation, composition changes or shared-engine edits were performed. New files are only this diagnosis, its JSON evidence and the metadata proposal in this recovery folder. Existing recovery README and quarantined packages were untouched.
