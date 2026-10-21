# Optical Illusions Research Repository

## Project Overview

This repository is a peer-review-depth research compendium of formally established optical illusions. The seed file (`optical-illusions-comprehensive-list.md`) catalogues ~380 named illusions across 15 categories. Each illusion is being expanded into a standalone research report following the standardized template in `templates/report-template.md`.

## Repository Structure

```
optical illusions/
├── CLAUDE.md                                  # This file — project instructions
├── optical-illusions-comprehensive-list.md    # Original seed file (preserved as-is)
├── taxonomy/
│   ├── categories.yml                         # 15 canonical category definitions
│   ├── mechanisms.yml                         # Controlled vocabulary of perceptual mechanisms
│   ├── aliases.yml                            # Alternate names → canonical slugs
│   └── duplicates-resolved.yml                # Documented merge decisions
├── templates/
│   ├── report-template.md                     # Full 11-section report template
│   ├── report-checklist.md                    # Quality criteria per status level
│   └── demo-manifest-template.yml             # Template manifest for demo folders
├── assets/                                    # Visual demonstrations (per-illusion subfolders)
│   └── {slug}/                                # One folder per illusion
│       ├── manifest.yml                       # Required — lists all demos in this folder
│       ├── static.svg                         # Static stimulus image
│       ├── interactive.html                   # Self-contained interactive demo
│       ├── generate.py                        # Stimulus generation script
│       └── demo.gif                           # Animated demonstration
├── reports/                                   # Individual illusion reports (flat directory)
└── indexes/
    └── master-index.md                        # Living status-tracking index
```

## File Naming Convention

All report filenames use **lowercase kebab-case**:

- Strip diacritics: `Müller-Lyer` → `muller-lyer`
- Replace spaces and special characters with hyphens
- Remove possessives: `Adelson's` → `adelson`
- Maximum 60 characters (excluding `.md` extension)
- Format: `reports/{canonical-slug}.md`

Examples:
- `reports/muller-lyer-illusion.md`
- `reports/checker-shadow-illusion.md`
- `reports/penrose-triangle.md`

## YAML Frontmatter Schema

Every report file begins with YAML frontmatter conforming to this schema:

```yaml
---
# Identification
title: "Full Display Name of the Illusion"
slug: canonical-slug
aliases:
  - "Alternate Name 1"
  - "Alternate Name 2"

# Classification
primary_category: category-id          # From taxonomy/categories.yml
secondary_categories:                   # From taxonomy/categories.yml
  - category-id-2
mechanisms:                             # From taxonomy/mechanisms.yml
  - mechanism-id-1
  - mechanism-id-2
tags:
  - free-form-tag

# Historical Metadata
discovered_by: "Name(s)"
discovery_year: YYYY                   # Integer or null if unknown
named_after: "Person or description"

# Cross-References
related_illusions:
  - slug: other-illusion-slug
    type: shared-mechanism | variant | inverse | historical
  - slug: another-illusion-slug
    type: variant

# Status Tracking
status: stub | draft | review | complete
last_updated: YYYY-MM-DD
reviewer: null                         # Name when in review or complete

# Quantitative Summary
effect_size_range: "description or null"
key_metric: "description or null"

# Demonstrations
has_demos: false               # Set to true when assets/{slug}/ exists with demos
demo_count: 0                  # Number of demos in manifest
---
```

### Field Requirements

- **title**: Full human-readable name including diacritics
- **slug**: Must match the filename (without `.md`)
- **aliases**: All alternate names from `taxonomy/aliases.yml` that point to this slug
- **primary_category**: Exactly one; must be a valid ID from `taxonomy/categories.yml`
- **secondary_categories**: Zero or more; must be valid IDs from `taxonomy/categories.yml`
- **mechanisms**: One or more; must be valid IDs from `taxonomy/mechanisms.yml`
- **status**: One of `stub`, `draft`, `review`, `complete`
- **related_illusions**: Bidirectional — if A references B, B must reference A
- **type**: One of `shared-mechanism`, `variant`, `inverse`, `historical`
- **has_demos**: Boolean; `true` when `assets/{slug}/` exists with a valid `manifest.yml`
- **demo_count**: Integer; number of demo entries in the manifest

## Taxonomy System

All category and mechanism values in report frontmatter **must** come from the controlled YAML vocabularies:

- **Categories** (`taxonomy/categories.yml`): 15 canonical categories corresponding to the seed file headings. Each report has exactly one `primary_category` and zero or more `secondary_categories`.
- **Mechanisms** (`taxonomy/mechanisms.yml`): ~25 perceptual mechanisms organized by processing level (retinal, early cortical, mid-level, high-level, physical). Reports reference whichever mechanisms are relevant.

If a new category or mechanism is needed, add it to the appropriate YAML file first, then reference it in reports.

## Deduplication Policy

The seed file contains intentional overlaps (~18 illusions appearing in multiple categories) and near-duplicate entries (~5 pairs sharing the same underlying phenomenon). The deduplication policy is:

1. **One report per unique phenomenon.** If two names describe the same perceptual effect, they share a single report file under the canonical slug.
2. **`taxonomy/aliases.yml`** maps every alternate name to its canonical slug.
3. **`taxonomy/duplicates-resolved.yml`** documents every merge decision with rationale.
4. **Multi-category illusions** are handled via `primary_category` + `secondary_categories` in frontmatter — no need for duplicate files.
5. When in doubt about whether two entries are the same phenomenon, keep them separate and note the relationship in `related_illusions`.

## Cross-Referencing Guidelines

- **Bidirectional**: If report A lists B in `related_illusions`, report B must list A.
- **Typed relationships**:
  - `shared-mechanism`: Both illusions involve the same perceptual mechanism
  - `variant`: One is a variation or extension of the other
  - `inverse`: The illusions produce opposite perceptual effects
  - `historical`: Connected through history of discovery or naming
- Cross-references appear both in YAML frontmatter and in Section 8 (Relationship to Other Illusions) as narrative prose.

## Status Tracking

Reports progress through four status levels:

| Status     | Description |
|------------|-------------|
| `stub`     | Frontmatter complete, abstract written. Minimal body content. |
| `draft`    | All 11 sections present with substantive content. Suggested ~10+ references (flexible for obscure illusions). |
| `review`   | All sections substantive. Suggested ~15+ references. Statistical claims include effect sizes where available. Theoretical accounts address counterevidence. |
| `complete` | All checklist items satisfied. Cross-references bidirectional and verified. Ready for external review. |

Reference count guidelines are **suggestions, not strict gates**. Some illusions have limited literature, and quality matters more than quantity.

See `templates/report-checklist.md` for detailed quality criteria per level.

## Writing Style Guide

- **Person**: Third person throughout
- **Tense**: Past tense for reporting experimental results; present tense for established facts and theoretical descriptions
- **Citations**: APA 7th edition format
- **Terminology**: Use precise perceptual science terminology; define terms on first use
- **Objectivity**: Present competing theories without editorial bias; note the weight of evidence
- **Quantitative**: Include effect sizes, confidence intervals, and sample sizes where available
- **Figures**: Reference figures by number; describe key visual elements in text for accessibility

## Assets Directory

Each illusion can have an `assets/{slug}/` folder containing visual demonstrations. Every such folder **must** contain a `manifest.yml` describing its contents (see `templates/demo-manifest-template.yml` for the template).

### Demonstration Types

| Type | Description | Formats |
|------|-------------|---------|
| `static-image` | A fixed image showing the illusion stimulus | SVG (preferred), PNG, GIF |
| `interactive` | A self-contained HTML page letting the user manipulate parameters | HTML |
| `generator` | A Python script that produces stimulus images with configurable parameters | PY |
| `video` | An animated demonstration of the illusion | GIF, MP4, WebM |

### Demo File Conventions

- **Self-contained HTML**: Interactive demos must not depend on external CDNs or network resources. All CSS and JS must be embedded in the HTML file.
- **SVG preferred**: For static images, use SVG over raster formats when feasible. SVGs scale cleanly, are editable, and have smaller file sizes for geometric stimuli.
- **Python dependencies**: Generator scripts list their pip dependencies in the manifest's `dependencies` field. Common packages (matplotlib, numpy, Pillow) are expected.
- **Manifest required**: A demo folder without a `manifest.yml` is invalid. The manifest must accurately list every demo file in the folder.
- **Folder naming**: Asset subfolders use the same canonical slug as the report file (e.g., `assets/muller-lyer-illusion/`).
- **External references**: Links to well-known external demonstrations (websites, videos, apps) are listed in the manifest's `external_references` field rather than as local files.

## Workflow: Adding a New Report

1. **Check `taxonomy/aliases.yml`** — confirm the illusion is not an alias for an existing report.
2. **Check `taxonomy/duplicates-resolved.yml`** — confirm it has not been merged into another entry.
3. **Create the file** — copy `templates/report-template.md` to `reports/{slug}.md`.
4. **Fill frontmatter** — populate all fields, using only values from `taxonomy/categories.yml` and `taxonomy/mechanisms.yml`.
5. **Write the abstract** — set status to `stub`.
6. **Develop content** — work through sections; advance to `draft` when all 11 sections have substantive content.
7. **Update cross-references** — add `related_illusions` entries and ensure bidirectional links exist in the referenced reports.
8. **Create demos (optional)** — create `assets/{slug}/` with a `manifest.yml` and at least one demo file. Set `has_demos: true` and `demo_count` in the report frontmatter. Reference demos in Section 11.
9. **Update `indexes/master-index.md`** — set the illusion's status to match the report's current status.
