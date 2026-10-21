# IMCCM Grant Tracker — Build Directive

## Document Purpose

This is a complete build directive for an autonomous coding agent (Claude Code). It contains everything needed to set up, build, deploy, and verify a grant discovery and tracking web application for the Independent Music Collaborative of Central Minnesota (IMCCM).

**The agent executing this directive has `gh` CLI and SSH access.** It should execute each phase sequentially, completing all verification steps before proceeding to the next phase.

---

## Project Context

IMCCM is a 501(c)(3) nonprofit arts organization in St. Cloud, MN that operates B-Side Indie Music Cafe, Project 37 (all-ages music programming), and the Common Roots Festival. They need a system to:

1. **Discover** grant opportunities (operator + AI research → structured data)
2. **Track** deadlines and application status (team dashboard)
3. **Collaborate** on grant writing (upload/view/manage draft documents)

The team is 3-5 non-technical people. The interface must be extremely simple.

---

## Architecture

```
┌─────────────────────┐     ┌──────────────────────┐
│   Claude CLI         │────▶│   Supabase (DB +     │
│   (Discovery runs)   │     │   File Storage)      │
└─────────────────────┘     └──────────┬───────────┘
                                       │
                            ┌──────────▼───────────┐
                            │   Next.js on Vercel   │
                            │   (Team Dashboard)    │
                            └──────────────────────┘
                                       │
                            ┌──────────▼───────────┐
                            │   Browser (Team)      │
                            │   Password-gated      │
                            └──────────────────────┘
```

### Tech Stack

| Component | Technology | Reason |
|-----------|-----------|--------|
| Framework | Next.js 14+ (App Router) | Simple deployment on Vercel, full-stack in one repo |
| Database | Supabase (PostgreSQL) | Free tier, handles DB + file storage, REST API |
| Deployment | Vercel (free tier) | Auto-deploys from GitHub, zero config for Next.js |
| Auth | Single shared password via cookie | Simplest possible — no user accounts needed |
| Styling | Tailwind CSS | Rapid UI development, responsive by default |
| Discovery | CLI scripts (Node.js) | Run locally, push to Supabase |

### Repository

- **Name:** `imccm-grant-tracker`
- **Visibility:** Private
- **Owner:** Use the authenticated GitHub user's account

---

## Data Model

### Table: `grants`

Derived from the actual IMCCM spreadsheet data structure.

```sql
CREATE TABLE grants (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),

  -- Core identification
  funder TEXT NOT NULL,
  grant_name TEXT NOT NULL,
  amount TEXT,                    -- e.g. "$5,000-$12,000", "Up to $8,000", "Varies"

  -- Requirements & fit
  key_requirements TEXT,          -- Eligibility notes
  notes_fit TEXT,                 -- Why this is relevant to IMCCM
  priority TEXT CHECK (priority IN ('HIGH', 'MEDIUM', 'LOW')) DEFAULT 'MEDIUM',
  fit_score INTEGER CHECK (fit_score BETWEEN 0 AND 100),  -- Optional numeric score
  website TEXT,                   -- Funder/program URL
  tags TEXT[],                    -- Array: e.g. ['arts', 'youth', 'operating']

  -- Timeline
  opens TEXT,                     -- e.g. "Now Open", "Feb 1, 2026", "Rolling"
  deadline TEXT,                  -- Human-readable: "Jan 21, 2026", "Rolling", "~May 2026"
  deadline_date DATE,             -- Machine-sortable date (NULL for rolling/TBD)

  -- Application tracking
  status TEXT CHECK (status IN (
    'discovered',
    'researching',
    'writing',
    'review',
    'submitted',
    'awarded',
    'declined',
    'deferred',
    'expired'
  )) DEFAULT 'discovered',
  assigned_to TEXT,
  draft_due DATE,
  submitted_date DATE,
  amount_requested TEXT,
  decision_date DATE,
  awarded BOOLEAN,

  -- Discovery metadata
  discovery_source TEXT,          -- e.g. 'manual', 'claude-cli', 'cmab-website'
  discovery_date DATE DEFAULT CURRENT_DATE
);

-- Index for dashboard queries
CREATE INDEX idx_grants_deadline ON grants (deadline_date);
CREATE INDEX idx_grants_status ON grants (status);
CREATE INDEX idx_grants_priority ON grants (priority);
```

### Table: `drafts`

```sql
CREATE TABLE drafts (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  created_at TIMESTAMPTZ DEFAULT now(),
  grant_id UUID REFERENCES grants(id) ON DELETE CASCADE,
  filename TEXT NOT NULL,
  file_path TEXT NOT NULL,        -- Supabase storage path
  file_size INTEGER,
  uploaded_by TEXT,                -- Just a name string, no auth
  label TEXT,                     -- e.g. "First draft", "Final version", "Budget attachment"
  status TEXT CHECK (status IN (
    'draft',
    'under_review',
    'final',
    'submitted'
  )) DEFAULT 'draft'
);

CREATE INDEX idx_drafts_grant ON drafts (grant_id);
```

### Table: `notes`

Simple activity/comment log per grant.

```sql
CREATE TABLE notes (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  created_at TIMESTAMPTZ DEFAULT now(),
  grant_id UUID REFERENCES grants(id) ON DELETE CASCADE,
  author TEXT,                    -- Name string
  content TEXT NOT NULL
);

CREATE INDEX idx_notes_grant ON notes (grant_id);
```

### Storage Bucket

- **Bucket name:** `grant-drafts`
- **Public:** No (accessed through app API routes only)
- **Allowed types:** `.pdf`, `.doc`, `.docx`, `.txt`, `.rtf`, `.odt`
- **Max file size:** 10MB

---

## Seed Data

The repository includes two reference files in a `seed/` directory:

1. `seed/IMCCM_Grant_Discovery_Profile_2026.docx` — Organization profile with mission, programs, funding history, scoring criteria, and key contacts
2. `seed/IMCCM_2026_Grant_Opportunities.xlsx` — Current grant data across three sheets:
   - **"2026 Grant Opportunities"** — 19 grant records with: Funder, Grant Name, Amount, Key Requirements, Opens, Deadline, Priority, Notes/Fit, Website
   - **"Deadline Calendar"** — 14 entries with: Month, Deadline, Grant, Funder, Amount, Priority
   - **"Application Tracker"** — 5 entries with: Grant Name, Funder, Deadline, Status, Assigned To, Draft Due, Submitted Date, Amount Requested, Decision Date, Awarded?, Notes

**Seed script requirements:**
- Parse the XLSX file using a Node.js library (e.g., `xlsx` / SheetJS)
- Map each row from the "2026 Grant Opportunities" sheet into the `grants` table
- Parse deadline strings into `deadline_date` where possible (NULL for "Rolling", "TBD", approximate dates like "~May 2026")
- Merge status data from the "Application Tracker" sheet by matching on grant name + funder
- Set `discovery_source` to `'seed'` for all seeded records
- The seed script should be idempotent (safe to run multiple times — upsert by funder + grant_name)

---

## Phase 1: Project Skeleton

### Scope
Set up the repository, Supabase project configuration, Next.js application with password protection, and deploy to Vercel.

### Deliverables
1. Private GitHub repository `imccm-grant-tracker` created and initialized
2. Next.js 14+ application with App Router
3. Tailwind CSS configured
4. Supabase client library installed and configured
5. Environment variables documented (`.env.example`)
6. Password-protection middleware that gates all routes
7. A single placeholder page at `/` that says "IMCCM Grant Tracker" after authentication
8. `README.md` with setup instructions for local development
9. Deployment-ready for Vercel

### Environment Variables

```
NEXT_PUBLIC_SUPABASE_URL=<supabase project url>
NEXT_PUBLIC_SUPABASE_ANON_KEY=<supabase anon key>
SUPABASE_SERVICE_KEY=<supabase service role key — server-side only>
APP_PASSWORD=<shared team password>
AUTH_COOKIE_NAME=imccm_auth
```

### Password Protection Implementation

- Middleware checks for a signed cookie on every request
- `/login` route renders a simple password form
- On correct password, set an HTTP-only cookie (7-day expiry)
- No user accounts, no database involvement — just a single env var comparison
- Cookie should be signed/encrypted (use Next.js built-in or a simple HMAC)

### Verification Steps — Phase 1

Each step must PASS before proceeding. If a step fails, fix and re-verify.

| # | Test | Method | Pass Condition |
|---|------|--------|---------------|
| 1.1 | Repository exists and is private | `gh repo view --json isPrivate` | `isPrivate: true` |
| 1.2 | Project builds without errors | `npm run build` | Exit code 0, no errors |
| 1.3 | Dev server starts | `npm run dev` — hit `http://localhost:3000` | Redirects to `/login` |
| 1.4 | Wrong password rejected | POST to `/login` with wrong password | Stays on login page, shows error |
| 1.5 | Correct password accepted | POST to `/login` with correct password | Redirects to `/`, cookie set |
| 1.6 | Protected route works | GET `/` without cookie | Redirects to `/login` |
| 1.7 | Protected route with cookie | GET `/` with valid cookie | Returns 200, shows placeholder |
| 1.8 | Environment variables documented | `.env.example` exists | Contains all required vars with placeholder values |

### Falsification Criteria — Phase 1

These are conditions that would prove the phase is **broken**. The agent should actively attempt to trigger these:

- **F1.1:** Accessing any page without the auth cookie returns content other than a redirect to `/login`
- **F1.2:** Submitting an incorrect password grants access
- **F1.3:** The auth cookie is readable/modifiable by client-side JavaScript (must be HTTP-only)
- **F1.4:** `SUPABASE_SERVICE_KEY` appears in any client-side bundle (check build output)
- **F1.5:** The build produces TypeScript or ESLint errors that were suppressed rather than fixed

---

## Phase 2: Database & Seed Data

### Scope
Create the Supabase schema, storage bucket, and seed the database from the provided XLSX file.

### Deliverables
1. SQL migration file (`supabase/migrations/001_initial_schema.sql`) with all tables and indexes
2. Supabase storage bucket `grant-drafts` configured
3. Seed script (`scripts/seed.ts` or `scripts/seed.js`) that parses the XLSX and populates the database
4. Row Level Security (RLS) policies:
   - All tables: Enable RLS
   - Read/write allowed only with the `service_role` key (used by API routes server-side)
   - The anon key should NOT have direct access to tables (all access goes through Next.js API routes)
5. Supabase configuration documented in README

### Verification Steps — Phase 2

| # | Test | Method | Pass Condition |
|---|------|--------|---------------|
| 2.1 | Schema created | Query `grants` table | Table exists with all columns |
| 2.2 | Seed script runs | `npx tsx scripts/seed.ts` | Inserts 19 grant records, no errors |
| 2.3 | Seed is idempotent | Run seed script twice | Same record count, no duplicates |
| 2.4 | Deadline dates parsed | Query grants with `deadline_date IS NOT NULL` | At least 10 records have parsed dates |
| 2.5 | Rolling/TBD handled | Query grants with `deadline_date IS NULL` | Records with "Rolling"/"TBD" deadlines have NULL date |
| 2.6 | Tracker data merged | Query grants where `status != 'discovered'` | Status from tracker sheet is reflected |
| 2.7 | Storage bucket exists | List Supabase storage buckets | `grant-drafts` bucket present, not public |
| 2.8 | RLS blocks anon access | Query grants table with anon key directly | Returns empty or error (blocked by RLS) |
| 2.9 | Service key works | Query grants table with service key | Returns all records |

### Falsification Criteria — Phase 2

- **F2.1:** The anon key can read or write grant data directly (bypassing API routes)
- **F2.2:** Running the seed script a second time creates duplicate records
- **F2.3:** A grant with deadline "Rolling" has a non-null `deadline_date`
- **F2.4:** The seed script crashes on any row in the source XLSX

---

## Phase 3: Dashboard

### Scope
Build the team-facing dashboard with timeline view, status board, and grant detail pages.

### Deliverables

#### 3A: API Routes
Server-side Next.js API routes (Route Handlers in App Router) that proxy all Supabase access:

- `GET /api/grants` — List all grants, supports query params: `?status=`, `?priority=`, `?upcoming_days=30`
- `GET /api/grants/[id]` — Single grant with its drafts and notes
- `PATCH /api/grants/[id]` — Update grant fields (status, assigned_to, notes, etc.)
- `POST /api/grants` — Create a new grant manually
- `DELETE /api/grants/[id]` — Delete a grant

All routes use the Supabase service key server-side. All routes check the auth cookie.

#### 3B: Dashboard Views

**Home / Timeline View (`/`)**
- Grants grouped by time horizon: **Overdue** → **This Week** → **Next 2 Weeks** → **Next 30 Days** → **Next 90 Days** → **Rolling/TBD** → **Closed/Past**
- Each grant card shows: Funder, Grant Name, Amount, Deadline, Priority badge (color-coded), Status badge
- Click a card → detail page
- Visual urgency: Overdue = red, This Week = orange, Next 2 Weeks = yellow

**Status Board (`/board`)**
- Kanban-style columns: Discovered → Researching → Writing → Review → Submitted → Awarded/Declined
- Grants as cards that can be moved between columns (drag-and-drop if feasible, otherwise dropdown to change status)
- Filter by priority

**Grant Detail (`/grants/[id]`)**
- Full grant information display
- Editable fields: status, assigned_to, notes_fit, priority
- Drafts section (Phase 4)
- Notes/activity log with ability to add new notes
- Link to funder website (opens in new tab)

#### 3C: Navigation & Layout
- Simple top navigation: Timeline | Board | Add Grant
- Mobile-responsive (people will check on phones)
- Clean, minimal design — no heavy graphics, just clear typography and color coding
- IMCCM branding: use organization name in header, keep it professional but not corporate

### Verification Steps — Phase 3

| # | Test | Method | Pass Condition |
|---|------|--------|---------------|
| 3.1 | API returns grants | `GET /api/grants` | Returns array of 19 seeded grants |
| 3.2 | Filtering works | `GET /api/grants?priority=HIGH` | Returns only HIGH priority grants |
| 3.3 | Timeline groups correctly | Visual inspection of home page | Grants appear in correct time buckets based on deadline_date relative to current date |
| 3.4 | Overdue grants visible | Check for grants with past deadlines | Shown in Overdue section (red) |
| 3.5 | Rolling grants handled | Check for rolling deadline grants | Appear in "Rolling/TBD" section, not in time-based groups |
| 3.6 | Status board renders | Navigate to `/board` | All status columns visible, grants in correct columns |
| 3.7 | Status change works | Change a grant's status | Grant moves to new column, persists on refresh |
| 3.8 | Detail page loads | Click a grant card | Shows all grant information |
| 3.9 | Notes can be added | Add a note on detail page | Note appears in log, persists on refresh |
| 3.10 | Mobile responsive | Resize browser to 375px width | Layout readable, no horizontal scroll, cards stack |
| 3.11 | Auth required | Access `/api/grants` without cookie | Returns 401 |
| 3.12 | Add grant works | Use "Add Grant" form | New grant appears in timeline and board |

### Falsification Criteria — Phase 3

- **F3.1:** Any API route returns data without a valid auth cookie
- **F3.2:** A grant with `deadline_date` of today appears in "Next 2 Weeks" instead of "This Week"
- **F3.3:** Changing a grant's status on the board doesn't persist after page refresh
- **F3.4:** A grant with NULL `deadline_date` causes a rendering error or appears in a date-based group
- **F3.5:** The dashboard is unusable on a mobile viewport (375px)

---

## Phase 4: Draft Management

### Scope
File upload, viewing, and management for grant application drafts.

### Deliverables

1. **Upload interface** on each grant's detail page:
   - File picker (accepts .pdf, .doc, .docx, .txt, .rtf, .odt)
   - Label field (e.g., "First draft", "Budget narrative")
   - Uploaded-by name field (free text, remembers last used via localStorage)
   - 10MB max file size with client-side validation
   - Upload goes to Supabase storage via API route, metadata to `drafts` table

2. **Draft list** on each grant's detail page:
   - Shows all drafts for this grant, newest first
   - Displays: filename, label, uploaded_by, date, status, file size
   - Download button for each draft
   - Status toggle: draft → under_review → final → submitted

3. **API Routes:**
   - `POST /api/grants/[id]/drafts` — Upload a file
   - `GET /api/grants/[id]/drafts` — List drafts for a grant
   - `GET /api/drafts/[id]/download` — Download a draft file
   - `PATCH /api/drafts/[id]` — Update draft status/label
   - `DELETE /api/drafts/[id]` — Delete a draft and its file

### Verification Steps — Phase 4

| # | Test | Method | Pass Condition |
|---|------|--------|---------------|
| 4.1 | Upload works | Upload a .pdf file to a grant | File stored in Supabase, metadata in drafts table |
| 4.2 | Upload validation | Try uploading a .exe file | Rejected with clear error message |
| 4.3 | Size limit enforced | Try uploading >10MB file | Rejected before upload begins |
| 4.4 | Draft list shows files | View grant with uploaded drafts | All drafts visible with correct metadata |
| 4.5 | Download works | Click download on a draft | File downloads correctly |
| 4.6 | Status change works | Change draft status | New status persists on refresh |
| 4.7 | Delete works | Delete a draft | Removed from list and storage |
| 4.8 | Auth on all routes | Hit draft API routes without cookie | All return 401 |

### Falsification Criteria — Phase 4

- **F4.1:** A file can be uploaded without auth
- **F4.2:** A file type outside the allowed list can be uploaded
- **F4.3:** A file exceeding 10MB is accepted
- **F4.4:** Deleting a draft leaves an orphaned file in Supabase storage
- **F4.5:** The draft download URL is accessible without authentication

---

## Phase 5: Discovery Pipeline

### Scope
CLI tooling for grant discovery that feeds directly into the dashboard.

### Deliverables

1. **Discovery CLI script** (`scripts/discover.ts`):
   - Reads the IMCCM Grant Discovery Profile for organizational context
   - Accepts a research summary as input (structured text or JSON)
   - Validates required fields (funder, grant_name, deadline minimum)
   - Pushes new grant records to Supabase
   - Outputs a summary of what was added

2. **Claude CLI command configuration** (`.claude/commands/discover-grants.md`):
   - A custom slash command for Claude Code that:
     - Reads the grant discovery profile from `seed/IMCCM_Grant_Discovery_Profile_2026.docx` (or a markdown version)
     - Uses the scoring criteria from the profile to evaluate fit
     - Searches for grant opportunities based on IMCCM's keywords and funder targets
     - Outputs structured grant data
     - Calls the discovery script to push results to the database
   - The command should be documented in README

3. **Grant Discovery Profile** in machine-readable format:
   - Convert the key sections of the DOCX profile into `seed/discovery-profile.md`
   - Include: organization overview, programs, funding priorities, scoring criteria, keywords, target funders
   - This is the reference document the Claude CLI command uses

4. **Batch import script** (`scripts/import-grants.ts`):
   - Accepts a JSON file of grants
   - Validates and upserts to database
   - For manual batch imports outside of the CLI workflow

### CLI Usage Pattern

```bash
# Inside the repo, using Claude Code:
# Run the custom command to discover grants
/discover-grants

# Claude CLI will:
# 1. Read the discovery profile
# 2. Research grant opportunities
# 3. Score them against IMCCM criteria
# 4. Output structured data
# 5. Push to Supabase via the discover script

# Or manually import a batch:
npx tsx scripts/import-grants.ts --file grants-batch.json
```

### Discovery Output Schema

Each discovered grant should be structured as:

```json
{
  "funder": "Central MN Arts Board",
  "grant_name": "Community Arts Support",
  "amount": "$5,000-$12,000",
  "key_requirements": "501(c)(3) arts org in Region 7W, 2+ years operating, budget <$250K",
  "opens": "Now Open",
  "deadline": "Jan 21, 2026",
  "deadline_date": "2026-01-21",
  "priority": "HIGH",
  "notes_fit": "Existing relationship, funds operations",
  "website": "https://www.centralmnartsboard.org/grants/...",
  "tags": ["arts", "operating", "regional"],
  "fit_score": 85,
  "discovery_source": "claude-cli"
}
```

### Verification Steps — Phase 5

| # | Test | Method | Pass Condition |
|---|------|--------|---------------|
| 5.1 | Discover script runs | Execute with sample data | Grant record created in Supabase |
| 5.2 | Validation works | Pass incomplete data (missing funder) | Script rejects with clear error |
| 5.3 | Upsert behavior | Push same grant twice | Only one record exists |
| 5.4 | Discovery profile readable | Script reads discovery-profile.md | Parses scoring criteria and keywords |
| 5.5 | Batch import works | Run import with JSON file of 3 grants | All 3 appear in database |
| 5.6 | Dashboard reflects new grants | Add via CLI, then check dashboard | New grants visible in timeline |
| 5.7 | Claude command file exists | Check `.claude/commands/discover-grants.md` | File exists with proper structure |

### Falsification Criteria — Phase 5

- **F5.1:** The discover script can push a grant without a `funder` or `grant_name`
- **F5.2:** Running the script without valid Supabase credentials silently fails (should error clearly)
- **F5.3:** The batch import creates duplicates when run twice with the same data
- **F5.4:** The discovery profile is not included in the repo or is inaccessible to the CLI command

---

## Phase 6: Polish & Documentation

### Scope
Mobile optimization, deadline notifications, team onboarding guide, and final cleanup.

### Deliverables

1. **Mobile optimization pass:**
   - Test all views at 375px width
   - Touch-friendly tap targets (min 44px)
   - Cards stack vertically on mobile
   - Navigation collapses to hamburger or simple stacked menu

2. **Deadline awareness features:**
   - Color-coded urgency throughout (red/orange/yellow/green)
   - Home page shows a "needs attention" count badge
   - Optional: Simple cron-compatible script that could send email reminders (documented but not auto-deployed)

3. **Team onboarding guide** (`docs/TEAM_GUIDE.md`):
   - How to access the dashboard (URL + password)
   - How to view the timeline and understand urgency colors
   - How to check grant details
   - How to upload a draft
   - How to change a grant's status
   - How to add notes
   - Screenshots or annotated descriptions for each action
   - Keep it under 2 pages when printed

4. **Operator guide** (`docs/OPERATOR_GUIDE.md`):
   - How to run a grant discovery cycle with Claude CLI
   - How to manually add grants via the UI or import script
   - How to manage the Supabase database
   - How to update the shared password
   - How to deploy changes (push to GitHub → Vercel auto-deploys)
   - Troubleshooting common issues

5. **Final cleanup:**
   - Remove any unused dependencies
   - Ensure all environment variables are documented
   - Add license file (suggest MIT or similar)
   - Clean up any TODO comments
   - Ensure `.gitignore` covers all generated files

### Verification Steps — Phase 6

| # | Test | Method | Pass Condition |
|---|------|--------|---------------|
| 6.1 | Mobile usable | Test all pages at 375px | All content accessible, no horizontal scroll |
| 6.2 | Touch targets | Check buttons/links | Min 44px tap targets |
| 6.3 | Team guide complete | Read through guide | Covers all team workflows |
| 6.4 | Operator guide complete | Read through guide | Covers all operator workflows |
| 6.5 | No build warnings | `npm run build` | Zero warnings, zero errors |
| 6.6 | No unused deps | `npx depcheck` | No unused dependencies flagged |
| 6.7 | Env vars documented | Compare `.env.example` to actual usage | All variables present |

### Falsification Criteria — Phase 6

- **F6.1:** Any page is unusable on a 375px viewport
- **F6.2:** The team guide references features that don't exist or uses incorrect screenshots
- **F6.3:** The operator guide omits the discovery workflow
- **F6.4:** The build has suppressed warnings or errors

---

## Deployment Instructions

### Vercel Setup

1. Connect the private GitHub repo to Vercel
2. Set all environment variables in Vercel project settings
3. Deploy from `main` branch
4. Note: Vercel can access private repos via its GitHub integration

### Supabase Setup (Manual — Operator)

These steps must be performed by the operator in the Supabase web console:

1. Create a new Supabase project (free tier)
2. Run the migration SQL to create tables
3. Create the `grant-drafts` storage bucket (set to private)
4. Copy the project URL, anon key, and service role key to `.env` and Vercel

**The agent should document these steps clearly in the README but should NOT attempt to create Supabase resources programmatically** — the operator will do this through the Supabase dashboard.

### Post-Deployment Verification

After deployment to Vercel:

| # | Test | Pass Condition |
|---|------|---------------|
| D.1 | Site loads | Visit the Vercel URL → redirects to login |
| D.2 | Login works | Enter password → dashboard loads |
| D.3 | Data loads | Seeded grants appear on timeline |
| D.4 | File upload works | Upload a test PDF to a grant |
| D.5 | Mobile works | Visit on phone → fully usable |

---

## Execution Order Summary

```
Phase 1: Skeleton
  → Create repo → scaffold Next.js → password middleware → deploy
  → VERIFY ALL 1.x STEPS
  → ATTEMPT ALL F1.x FALSIFICATIONS

Phase 2: Database & Seed
  → Schema migration → storage bucket config → seed script → RLS
  → VERIFY ALL 2.x STEPS
  → ATTEMPT ALL F2.x FALSIFICATIONS

Phase 3: Dashboard
  → API routes → timeline view → status board → detail page → nav
  → VERIFY ALL 3.x STEPS
  → ATTEMPT ALL F3.x FALSIFICATIONS

Phase 4: Draft Management
  → Upload API → file picker UI → draft list → download → status
  → VERIFY ALL 4.x STEPS
  → ATTEMPT ALL F4.x FALSIFICATIONS

Phase 5: Discovery Pipeline
  → CLI script → Claude command → profile conversion → batch import
  → VERIFY ALL 5.x STEPS
  → ATTEMPT ALL F5.x FALSIFICATIONS

Phase 6: Polish & Docs
  → Mobile pass → urgency visuals → team guide → operator guide → cleanup
  → VERIFY ALL 6.x STEPS
  → ATTEMPT ALL F6.x FALSIFICATIONS
```

---

## Constraints & Non-Goals

### In Scope
- Simple password-protected web dashboard
- Grant discovery pipeline via CLI
- File upload/download for drafts
- Timeline and status tracking views
- Mobile-responsive design

### Out of Scope
- Real-time co-editing (use Google Docs externally)
- Automated grant searching (discovery is human + AI assisted)
- Financial tracking or accounting
- Public-facing pages
- Individual user accounts or role-based permissions
- Email/notification service deployment (document only)
- Integration with external grant databases

### Design Principles
- **Simplicity over features:** If a team member can't figure it out in 30 seconds, it's too complex
- **Data integrity over speed:** Every write operation should validate before committing
- **Progressive disclosure:** Show the minimum needed, reveal details on click
- **Fail visibly:** All errors should be clear and actionable, never silent

---

## Reference Files

The following files should be included in the `seed/` directory of the repository:

1. `IMCCM_Grant_Discovery_Profile_2026.docx` — Organization profile (provided by operator)
2. `IMCCM_2026_Grant_Opportunities.xlsx` — Current grant data (provided by operator)

The agent should copy these from the working directory into the repo's `seed/` folder during Phase 1 setup.
