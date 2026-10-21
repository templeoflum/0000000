# Development Roadmap

> Phased plan for building out the Optical Illusions Research Repository from
> its current scaffolded state (277 illusions indexed, 0 reports written) to a
> comprehensive, peer-review-depth reference with visual demonstrations.
>
> **Last updated:** 2026-03-04

---

## Current State

| Asset | Status |
|-------|--------|
| Taxonomy (categories, mechanisms, aliases, dedup) | Complete |
| Templates (report, checklist, demo manifest) | Complete |
| Master index (277 illusions) | Complete |
| Assets/demo infrastructure | Complete |
| Report files | 277 / 277 (all stub) |
| Visual demonstrations | 0 |

---

## Phase 0 — Foundation (COMPLETE)

Everything listed under "Current State" above. The repo is fully scaffolded and
ready for content production.

---

## Phase 1 — Stub Generation (COMPLETE)

**Goal:** Create a stub report for every illusion so the repository has 277
populated files with correct frontmatter and abstracts.

### Scope

- Generate `reports/{slug}.md` for all 277 illusions
- Each file gets fully populated YAML frontmatter (title, slug, aliases,
  primary/secondary categories, mechanisms, discovery metadata, empty
  `related_illusions`)
- Each file gets a 150–250 word abstract
- Status set to `stub`; master index updated

### Strategy

Work in **category batches** — complete one full category before moving to the
next. This keeps context focused and lets cross-references within a category
form naturally. Suggested order (most well-studied categories first):

| Batch | Category | Count | Rationale |
|-------|----------|-------|-----------|
| 1a | `geometric-size-length` | 39 | Largest category; classic illusions with deep literature |
| 1b | `brightness-lightness-contrast` | 22 | Well-studied; strong overlap with geometric |
| 1c | `color` | 17 | Distinct mechanisms; moderate size |
| 1d | `motion-movement` | 38 | Second-largest; many modern discoveries |
| 1e | `ambiguous-bistable-multistable` | 24 | Historically important; good demo candidates |
| 1f | `impossible-objects-paradox` | 14 | Small; tightly related group |
| 1g | `depth-3d-stereoscopic` | 21 | Mixed classical and modern |
| 1h | `aftereffect-adaptation` | 15 | Mechanistically coherent group |
| 1i | `contour-shape-completion` | 10 | Small; strong Gestalt theme |
| 1j | `atmospheric-natural` | 21 | Physical optics; different research style |
| 1k | `pareidolia-pattern-recognition` | 7 | Smallest; cognitive focus |
| 1l | `persistence-temporal` | 7 | Small; historical devices |
| 1m | `op-art-artistic` | 10 | Art-focused; less experimental literature |
| 1n | `cognitive-higher-order` | 16 | Broad; bridges to cognitive psychology |
| 1o | `miscellaneous-specialized` | 18 | Heterogeneous; finish last |

**Note:** Counts above reflect primary-category assignments. Illusions appearing
as secondary in another category are not double-counted — they already have their
file from their primary batch.

### Deliverables

- [x] 277 stub reports in `reports/`
- [x] Master index updated: all entries show `stub`
- [x] Spot-check: frontmatter validates against taxonomy YAML files

### Exit Criteria

Every illusion in the master index has a corresponding stub report file with
valid frontmatter and a substantive abstract.

---

## Phase 2 — Cornerstone Drafts

**Goal:** Develop ~40 high-priority illusions to full `draft` status (all 11
sections substantive, ~10+ references each).

### Selection Criteria

"Cornerstone" illusions are chosen for:

1. **Pedagogical importance** — commonly taught in perception courses
2. **Research depth** — extensive published literature available
3. **Category coverage** — at least 2 per category so no category is empty
4. **Demo potential** — strong candidates for visual demonstrations

### Proposed Cornerstone Set (~40 illusions)

**Geometric / Size / Length:**
- Muller-Lyer Illusion
- Ebbinghaus Illusion
- Ponzo Illusion
- Poggendorff Illusion
- Zollner Illusion
- Cafe Wall Illusion
- Moon Illusion
- Hering Illusion

**Brightness / Lightness / Contrast:**
- Hermann Grid Illusion
- Checker Shadow Illusion
- Simultaneous Contrast Illusion
- Mach Bands
- White's Illusion
- Cornsweet Illusion

**Color:**
- The Dress Illusion
- Chromatic Adaptation Illusion
- Benham's Top
- Neon Color Spreading

**Motion / Movement:**
- Rotating Snakes Illusion
- Motion Aftereffect
- Peripheral Drift Illusion
- Barberpole Illusion
- Wagon Wheel Effect
- Apparent Motion

**Ambiguous / Bistable / Multistable:**
- Necker Cube
- Rubin's Vase
- Duck-Rabbit Illusion
- My Wife and My Mother-in-Law
- Silhouette Illusion

**Impossible Objects / Paradox:**
- Penrose Triangle
- Penrose Stairs
- Impossible Trident

**Depth / 3D / Stereoscopic:**
- Ames Room
- Hollow-Face Illusion
- Random Dot Stereogram

**Aftereffect / Adaptation:**
- McCollough Effect
- Tilt Aftereffect
- Troxler's Fading

**Contour / Shape / Completion:**
- Kanizsa Triangle
- Illusory Contours

**Atmospheric / Natural:**
- Fata Morgana
- Rainbow
- Green Flash

**Pareidolia / Pattern Recognition:**
- Face Pareidolia

**Persistence / Temporal:**
- Persistence of Vision
- Phi Phenomenon

**Op Art / Artistic:**
- Trompe-l'oeil

**Cognitive / Higher-Order:**
- Stroop Effect
- Change Blindness
- McGurk Effect
- Rubber Hand Illusion

**Miscellaneous / Specialized:**
- Thatcher Illusion
- Hybrid Images

### Scope Per Report

- All 11 body sections written with substantive content
- ~10+ references (primary sources preferred)
- `related_illusions` populated with obvious connections
- Status advanced to `draft`

### Deliverables

- [ ] ~40 reports at `draft` status
- [ ] `related_illusions` populated (not yet required to be bidirectional)
- [ ] Master index reflects updated statuses

### Exit Criteria

All cornerstone reports have substantive content in every section, with real
citations and enough detail that a reader could understand the illusion without
consulting other sources.

---

## Phase 3 — Cornerstone Demos

**Goal:** Create visual demonstrations for the ~40 cornerstone illusions.

### Scope

For each cornerstone illusion, create at minimum:

- **1 static SVG** showing the canonical stimulus configuration
- **1 interactive HTML** demo allowing parameter manipulation

Selected illusions also get:

- **Python generator** scripts for parametric stimulus creation
- **Animated GIF/video** for motion-dependent illusions

### Priority Tiers

| Tier | Description | Target |
|------|-------------|--------|
| **Tier 1** | Geometric illusions reproducible with simple SVG (lines, circles, grids) | ~15 illusions |
| **Tier 2** | Brightness/color illusions needing careful color control | ~10 illusions |
| **Tier 3** | Motion illusions requiring animation (CSS/JS or GIF) | ~10 illusions |
| **Tier 4** | 3D/depth illusions needing stereoscopic or perspective rendering | ~5 illusions |

### Conventions (from CLAUDE.md)

- Interactive HTML is fully self-contained (no CDN dependencies)
- SVG preferred for static images
- Python scripts declare dependencies in manifest
- Every `assets/{slug}/` folder has a valid `manifest.yml`

### Deliverables

- [ ] `assets/{slug}/` folders for ~40 cornerstone illusions
- [ ] Each has `manifest.yml` + at least 1 static image + 1 interactive demo
- [ ] Report frontmatter updated: `has_demos: true`, `demo_count` accurate
- [ ] Section 11 of each cornerstone report references its demos

### Exit Criteria

A reader can open any cornerstone report's demo folder and immediately see and
interact with the illusion.

---

## Phase 4 — Cross-References & Review Advancement

**Goal:** Build the cross-reference network and advance cornerstone reports to
`review` status.

### Scope

**Cross-referencing:**
- Populate `related_illusions` for all cornerstone reports
- Ensure bidirectional links (if A→B exists, B→A exists)
- Write narrative prose in Section 8 describing relationships
- Tag relationship types: `shared-mechanism`, `variant`, `inverse`, `historical`

**Review advancement** (per checklist):
- Expand references to ~15+ per report
- Add effect sizes and confidence intervals where available
- Address counterevidence in Theoretical Accounts
- Reference specific brain regions/models in Neural Mechanisms
- Report individual differences findings or note absence of research
- Confirm writing style compliance (3rd person, APA 7th)
- Eliminate all placeholder text
- Assign reviewer

### Deliverables

- [ ] Bidirectional cross-references verified for all cornerstone reports
- [ ] ~40 reports at `review` status
- [ ] Master index reflects updated statuses

### Exit Criteria

All cornerstone reports pass the `review` checklist. Cross-reference network is
internally consistent — no dangling or one-directional links among cornerstones.

---

## Phase 5 — Breadth Expansion

**Goal:** Develop the remaining ~237 illusions from `stub` to `draft` status.

### Strategy

Work in category batches (same order as Phase 1). Within each batch:

1. Research and write all 11 sections
2. Populate `related_illusions` (including links to existing cornerstone reports)
3. Add at least 1 static demo where feasible
4. Advance to `draft`

### Prioritization Within Categories

Within each category, prioritize:
1. Illusions that are `related_illusions` targets of cornerstone reports (fills
   in dangling references)
2. Illusions with substantial published literature
3. Illusions with strong demo potential
4. Remaining illusions

### Batch Size

Target **15–20 illusions per work session** to maintain quality without context
fatigue. Each category may span multiple sessions.

### Deliverables

- [ ] All 277 reports at `draft` status or higher
- [ ] Basic cross-references populated across all reports
- [ ] Master index fully updated

### Exit Criteria

No report remains at `stub` status. Every report has substantive content in all
11 sections.

---

## Phase 6 — Demo Expansion

**Goal:** Extend visual demonstrations to all illusions where demos are feasible.

### Scope

Not all 277 illusions are equally demonstrable (e.g., atmospheric phenomena,
purely cognitive effects). Target coverage:

| Category | Demo Feasibility | Target Coverage |
|----------|-----------------|-----------------|
| Geometric / Size / Length | High — simple SVG geometry | ~90% |
| Brightness / Lightness / Contrast | High — grayscale/color patches | ~90% |
| Color | High — color rendering | ~85% |
| Motion / Movement | High — CSS/JS animation | ~85% |
| Ambiguous / Bistable | High — static images, some interactive | ~80% |
| Impossible Objects | High — SVG drawings | ~90% |
| Depth / 3D / Stereoscopic | Medium — some need stereo viewing | ~60% |
| Aftereffect / Adaptation | Medium — need timed sequences | ~70% |
| Contour / Shape / Completion | High — simple shapes | ~85% |
| Atmospheric / Natural | Low — photography-dependent | ~30% (external refs) |
| Pareidolia / Pattern Recognition | Low — photograph-dependent | ~30% (external refs) |
| Persistence / Temporal | Medium — need animation timing | ~60% |
| Op Art / Artistic | Medium — reproduction rights vary | ~50% |
| Cognitive / Higher-Order | Low — many are procedural, not visual | ~30% |
| Miscellaneous / Specialized | Mixed | ~40% |

For illusions where local demos aren't feasible, populate `external_references`
in the manifest with links to authoritative demonstrations.

### Deliverables

- [ ] Demo assets for ~150–180 illusions
- [ ] External references for illusions without local demos
- [ ] All manifests valid and accurate

---

## Phase 7 — Review & Completion

**Goal:** Advance all reports to `review` or `complete` status.

### Scope

**Review pass (all 277 reports):**
- Verify references are real and correctly cited (APA 7th)
- Confirm effect sizes are included where literature provides them
- Ensure cross-references are fully bidirectional
- Check taxonomy IDs against YAML files
- Eliminate remaining placeholder text

**Completion pass (cornerstone + well-documented illusions):**
- Full `complete` checklist satisfaction
- At least 2 demos of different types
- Section 11 references available demos
- Abstract accurately reflects full report content
- Ready for external peer review

### Deliverables

- [ ] All 277 reports at `review` status minimum
- [ ] ~100+ reports at `complete` status (cornerstones + well-documented)
- [ ] Remaining reports marked `review` with notes on gaps

### Exit Criteria

The repository is a credible academic reference. Any report at `complete` status
could be shared with a perception researcher without embarrassment.

---

## Phase 8 — Tooling & Validation

**Goal:** Build automation to maintain quality and enable discovery.

### Validation Scripts

- **Frontmatter validator**: Checks all reports against taxonomy YAML files
  (valid categories, mechanisms, aliases match)
- **Cross-reference checker**: Verifies bidirectional links; flags dangling refs
- **Manifest validator**: Confirms every `assets/{slug}/manifest.yml` accurately
  lists existing files; checks required fields
- **Status auditor**: Compares report status against checklist criteria; flags
  reports that claim a status but don't meet it
- **Index sync checker**: Confirms master index matches actual report files and
  statuses

### Discovery Tools

- **Search index**: Generate a JSON index of all illusions with metadata for
  client-side search/filter
- **Category browser**: Static HTML page listing illusions by category with
  links to reports and demos
- **Mechanism map**: Visualization showing which mechanisms connect which
  illusions

### Deliverables

- [ ] `scripts/` directory with validation tools
- [ ] CI-compatible validation (exit codes, structured output)
- [ ] `indexes/search-index.json` for programmatic access

---

## Phase 9 — Publication

**Goal:** Make the repository accessible as a browsable reference.

### Options (decide later)

1. **Static site generator** — Convert markdown reports to a browsable website
   (e.g., MkDocs, Hugo, Jekyll). Interactive demos embed directly.
2. **GitHub Pages** — Lightweight hosting with built-in markdown rendering.
3. **PDF compilation** — Generate a printable compendium from the reports.
4. **API** — Serve illusion metadata as a REST or GraphQL endpoint for
   researchers building tools.

### Scope (deferred)

Publication format depends on audience and use case. This phase is intentionally
left open until the content reaches critical mass (~Phase 5 completion).

---

## Timeline Summary

| Phase | Description | Illusion Count | Status Target |
|-------|-------------|---------------|---------------|
| 0 | Foundation | — | Infrastructure complete |
| 1 | Stub generation | 277 | All `stub` |
| 2 | Cornerstone drafts | ~40 | `draft` |
| 3 | Cornerstone demos | ~40 | Demos created |
| 4 | Cross-refs & review | ~40 | `review` |
| 5 | Breadth expansion | ~237 remaining | All `draft` |
| 6 | Demo expansion | ~150–180 | Demos created |
| 7 | Review & completion | 277 | `review`/`complete` |
| 8 | Tooling & validation | — | Scripts & indexes |
| 9 | Publication | — | Browsable output |

### Dependencies

```
Phase 0 (done)
  └─► Phase 1 (stubs)
        ├─► Phase 2 (cornerstone drafts)
        │     ├─► Phase 3 (cornerstone demos)
        │     └─► Phase 4 (cross-refs & review)
        │           └─► Phase 7 (review & completion)
        └─► Phase 5 (breadth expansion)
              └─► Phase 6 (demo expansion)
                    └─► Phase 7 (review & completion)
                          └─► Phase 8 (tooling)
                                └─► Phase 9 (publication)
```

Phases 2+3 and Phase 5 can run in parallel once Phase 1 is complete. Phase 8
(tooling) can begin as early as Phase 2 for validation scripts — earlier tooling
catches errors sooner.

---

## Principles

1. **Depth before breadth.** A small number of excellent reports is more valuable
   than 277 shallow ones. The cornerstone set proves the format works before
   scaling.

2. **Category batches.** Working through one category at a time maintains research
   context and naturally surfaces cross-references within families.

3. **Demos are not optional.** The whole point of an illusion is experiencing it.
   Reports without demonstrations are incomplete reference material.

4. **Infrastructure pays for itself.** Investing in validation tooling early
   prevents drift as the corpus grows. A bad frontmatter field in report #12
   is easy to fix; the same error in 200 reports is not.

5. **Progressive quality.** Every report passes through stub → draft → review →
   complete. No report jumps straight to complete. The progression ensures
   incremental improvement and catches errors at each gate.
