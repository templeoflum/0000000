# Report Quality Checklist

Use this checklist to evaluate a report's readiness for each status level.
Status progression: `stub` → `draft` → `review` → `complete`.

Reference count guidelines are **suggestions, not strict gates** — some illusions
have limited literature, and quality matters more than quantity.

---

## Stub

A report achieves `stub` status when:

- [ ] File exists at `reports/{slug}.md`
- [ ] All frontmatter fields are populated (or explicitly set to `null` where unknown)
- [ ] `primary_category` references a valid ID from `taxonomy/categories.yml`
- [ ] `mechanisms` contains at least one valid ID from `taxonomy/mechanisms.yml`
- [ ] `status` is set to `stub`
- [ ] Abstract section is written (150-250 words)
- [ ] `indexes/master-index.md` reflects current status

---

## Draft

A report achieves `draft` status when all stub criteria are met, plus:

- [ ] All 11 body sections are present and contain substantive content (not just placeholders)
- [ ] Historical Background includes discovery date and key researchers
- [ ] Stimulus Description is specific enough to reproduce the basic stimulus
- [ ] At least one theoretical account is described with supporting evidence
- [ ] References section contains cited works (suggested ~10+; fewer acceptable for obscure illusions)
- [ ] All references cited in text appear in the References section
- [ ] `related_illusions` in frontmatter lists at least the most obvious connections
- [ ] At least 1 demo (static image or interactive) in `assets/{slug}/` is encouraged but not required
- [ ] `status` is updated to `draft`
- [ ] `last_updated` date is current

---

## Review

A report achieves `review` status when all draft criteria are met, plus:

- [ ] All 11 sections contain substantive, well-sourced content
- [ ] References section is comprehensive (suggested ~15+; fewer acceptable if literature is limited)
- [ ] Statistical claims include effect sizes where available in the source literature
- [ ] Theoretical Accounts section addresses counterevidence for each theory
- [ ] Neural and Computational Mechanisms section references specific brain regions or models
- [ ] Individual Differences section reports findings or explicitly notes absence of research
- [ ] Cross-references (`related_illusions`) are bidirectional — referenced reports link back
- [ ] Writing follows style guide (3rd person, past tense for results, APA 7th citations)
- [ ] No placeholder text remains
- [ ] At least 1 demo exists in `assets/{slug}/` with a valid `manifest.yml`
- [ ] `has_demos` is set to `true` and `demo_count` is accurate in frontmatter
- [ ] `status` is updated to `review`
- [ ] `reviewer` field is populated in frontmatter

---

## Complete

A report achieves `complete` status when all review criteria are met, plus:

- [ ] All cross-references are bidirectional and verified (checked in both directions)
- [ ] Aliases in frontmatter match entries in `taxonomy/aliases.yml`
- [ ] Category and mechanism IDs are all valid against current taxonomy YAML files
- [ ] Key Demonstrations section describes at least 2 reproducible demonstrations
- [ ] At least 2 demos of different types exist in `assets/{slug}/` (e.g., static-image + interactive)
- [ ] `manifest.yml` is complete and accurately describes all demo files
- [ ] Section 11 references the available demos in `assets/{slug}/`
- [ ] Abstract accurately summarizes the full report content
- [ ] No factual claims lack citations
- [ ] Citation section is complete with suggested citation format
- [ ] Report is ready for external peer review
- [ ] `status` is updated to `complete`
- [ ] `last_updated` date is current

---

## Notes

- **Flexibility**: These are quality guidelines, not mechanical gates. An illusion with 8
  high-quality references covering all major findings may be stronger than one with 20
  tangentially related citations.
- **Obscure illusions**: For illusions with very limited published research, note gaps
  explicitly rather than padding with weak sources. A thorough report on a poorly-studied
  illusion may have fewer references but should cover what is known with precision.
- **Progression**: Reports should generally move forward through statuses. If significant
  new evidence is published, a `complete` report can be reopened to `review` for updating.
