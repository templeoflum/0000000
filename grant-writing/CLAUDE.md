# IMCCM Grant Tracker — Claude Code Project Context

## What This Is

A grant discovery and tracking web application for the Independent Music Collaborative of Central Minnesota (IMCCM), a 501(c)(3) nonprofit in St. Cloud, MN. The team is 3-5 non-technical people — the interface must be extremely simple.

## Build Directive

The complete build plan is in `IMCCM_Grant_Tracker_Build_Directive.md`. Read it fully before starting any work. It contains 6 phases with verification steps and falsification criteria for each.

## Execution Rules

- Execute phases sequentially (1 → 2 → 3 → 4 → 5 → 6)
- After each phase: run ALL verification steps, then attempt ALL falsification criteria
- Do not proceed to the next phase until every verification passes and every falsification attempt fails
- If a falsification attempt succeeds, that's a bug — fix it and re-verify

## Phase Summary

1. **Project Skeleton** — Repo, Next.js + Tailwind, password auth middleware, placeholder page
2. **Database & Seed** — Supabase schema, RLS, seed script from XLSX
3. **Dashboard** — API routes, timeline view, kanban board, grant detail pages
4. **Draft Management** — File upload/download to Supabase storage
5. **Discovery Pipeline** — CLI scripts, Claude slash command, batch import
6. **Polish & Docs** — Mobile optimization, team guide, operator guide

## Tech Stack

- **Framework:** Next.js 14+ (App Router)
- **Database:** Supabase (PostgreSQL + file storage)
- **Deployment:** Vercel (free tier, auto-deploy from GitHub)
- **Auth:** Single shared password via HTTP-only signed cookie (no user accounts)
- **Styling:** Tailwind CSS
- **Discovery:** CLI scripts (Node.js/TypeScript)

## Repository

- **Name:** `imccm-grant-tracker`
- **Visibility:** Private
- **Create with:** `gh repo create imccm-grant-tracker --private`
- Agent has `gh` CLI and SSH access

## Supabase Setup

- Generate migration SQL and document manual steps clearly
- Do NOT create Supabase project programmatically — the operator will create it manually
- **Pause after Phase 1** and prompt the operator to set up Supabase and Vercel before continuing to Phase 2

## Seed Data Files (in this directory)

- `IMCCM_2026_Grant_Opportunities.xlsx` — 3 sheets: grant opportunities (19 rows), deadline calendar, application tracker
- `IMCCM_Grant_Discovery_Profile_2026.docx` — Org profile with mission, programs, funding history, scoring criteria
- These get copied into `seed/` in the repo during Phase 1

## Key Environment Variables

```
NEXT_PUBLIC_SUPABASE_URL=<supabase project url>
NEXT_PUBLIC_SUPABASE_ANON_KEY=<supabase anon key>
SUPABASE_SERVICE_KEY=<supabase service role key — server-side only>
APP_PASSWORD=<shared team password>
AUTH_COOKIE_NAME=imccm_auth
```

## Design Principles

- Simplicity over features
- Data integrity over speed
- Progressive disclosure (show minimum, reveal on click)
- Fail visibly (clear, actionable errors — never silent)
- No over-engineering — only build what's needed

## Important Constraints

- `SUPABASE_SERVICE_KEY` must NEVER appear in client-side bundles
- Auth cookie must be HTTP-only (not readable by client JS)
- All Supabase access goes through server-side API routes (anon key blocked by RLS)
- Allowed upload types: .pdf, .doc, .docx, .txt, .rtf, .odt (max 10MB)
