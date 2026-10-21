# Phase 7: Notification System (Addendum)

Append this phase to `IMCCM_Grant_Tracker_Build_Directive.md` after Phase 6.

---

## Phase 7: Email Notifications (Hybrid)

### Scope
Hybrid email notification system: daily digest for routine updates, immediate alerts for urgent deadline transitions.

### Architecture

```
┌─────────────────────────┐
│   Vercel Cron (daily)    │───▶ Morning digest email
│   6:00 AM Central Time   │     (approaching deadlines,
└─────────────────────────┘      yesterday's activity)

┌─────────────────────────┐
│   API Route Triggers     │───▶ Urgent alert emails
│   (inline, on write)     │     (deadline threshold crossed,
└─────────────────────────┘      status change to overdue)
                │
                ▼
        ┌──────────────┐
        │   Resend API  │───▶ Team email addresses
        │   (free tier)  │
        └──────────────┘
```

### Services

| Service | Tier | Limits | Purpose |
|---------|------|--------|---------|
| Resend | Free | 100 emails/day, 3,000/month | Email delivery |
| Vercel Cron | Free (Hobby) | Runs once/day minimum | Daily digest trigger |

Both free tiers are more than sufficient for a 3-5 person team.

### Environment Variables (add to existing)

```
RESEND_API_KEY=<resend api key>
NOTIFICATION_EMAILS=anna@example.com,angela@example.com,person3@example.com
NOTIFICATION_FROM=grants@imccm-grants.com
DIGEST_ENABLED=true
URGENT_ALERTS_ENABLED=true
```

`NOTIFICATION_EMAILS` is a comma-separated list. Adding or removing someone is just an env var change in Vercel — no code changes needed.

`NOTIFICATION_FROM` requires a verified domain in Resend, OR use Resend's default onboarding address (`onboarding@resend.dev`) during development. For production, verify a domain (can be a subdomain like `notify.bsidecafemn.com`).

### Email Types

#### 1. Daily Digest (Vercel Cron — 6:00 AM Central)

Sent every morning to all team members. Contains:

**Deadline Alerts**
- Overdue grants (deadline has passed, status not submitted/awarded/declined)
- Due this week (next 7 days)
- Due in 2 weeks (8-14 days out)

**Yesterday's Activity**
- Grants that changed status (e.g., "Community Arts Support moved from Writing → Review")
- New drafts uploaded (e.g., "Angela uploaded 'Budget Narrative v2' to Project Grant Round 2")
- New notes added

**Format:** Clean HTML email, minimal styling, scannable. No images or heavy formatting — just clear text with sections. Include a link to the dashboard at the bottom of every email.

**Skip rule:** If there are no approaching deadlines and no activity from yesterday, do not send the digest. Nobody wants an empty email.

#### 2. Urgent Alerts (Inline Triggers)

Sent immediately when specific conditions are met:

| Trigger | Condition | Email Subject |
|---------|-----------|---------------|
| Deadline approaching | A grant crosses from "Next 2 Weeks" into "This Week" bucket (7 days out) | ⚠️ Grant deadline this week: {grant_name} |
| Overdue | A grant's deadline passes and status is not submitted/awarded/declined | 🔴 OVERDUE: {grant_name} deadline was {deadline} |
| Status escalation | A grant moves to "review" status | 📋 Ready for review: {grant_name} |

**Implementation:** These triggers fire from existing API routes — specifically the `PATCH /api/grants/[id]` route (for status changes) and the daily cron (for deadline threshold crossings). No new endpoints needed for the triggers themselves.

**Deduplication:** Track which alerts have been sent to avoid repeats. Add a simple table:

```sql
CREATE TABLE notification_log (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  created_at TIMESTAMPTZ DEFAULT now(),
  grant_id UUID REFERENCES grants(id) ON DELETE CASCADE,
  notification_type TEXT NOT NULL,  -- 'digest', 'deadline_week', 'overdue', 'status_review'
  sent_to TEXT NOT NULL,            -- email address
  trigger_date DATE NOT NULL        -- prevents re-sending same alert
);

CREATE INDEX idx_notification_log_dedup 
  ON notification_log (grant_id, notification_type, trigger_date);
```

Before sending an urgent alert, check: has this grant + notification_type + today's date already been logged? If yes, skip.

### Deliverables

1. **Resend integration module** (`lib/email.ts`):
   - `sendEmail(to: string[], subject: string, html: string)` wrapper
   - Reads `RESEND_API_KEY` and `NOTIFICATION_FROM` from env
   - Error handling with logging (don't crash the app if email fails)

2. **Email templates** (`lib/email-templates.ts`):
   - `buildDigestEmail(data)` — returns HTML string for the daily digest
   - `buildUrgentAlert(type, grant)` — returns HTML string for each urgent alert type
   - Templates should be plain HTML with inline styles (email clients strip `<style>` tags)
   - Include dashboard link in every email

3. **Daily digest cron route** (`app/api/cron/daily-digest/route.ts`):
   - Vercel Cron configuration in `vercel.json`:
     ```json
     {
       "crons": [
         {
           "path": "/api/cron/daily-digest",
           "schedule": "0 12 * * *"
         }
       ]
     }
     ```
   - Note: `0 12 * * *` is noon UTC = 6:00 AM Central (CST is UTC-6)
   - Adjust to `0 11 * * *` during CDT (UTC-5) or use a timezone-aware approach
   - Secured with `CRON_SECRET` env var (Vercel sets this automatically for cron routes)
   - Queries: overdue grants, upcoming deadlines, yesterday's activity (notes, drafts, status changes)
   - Skips sending if no content
   - Logs to `notification_log`

4. **Urgent alert triggers** (integrated into existing routes):
   - In `PATCH /api/grants/[id]`: when status changes to `review`, send alert
   - In the daily cron: check for grants that just crossed into "this week" or "overdue" territory
   - All check `notification_log` before sending

5. **Notification log table** — migration file and RLS policy (same pattern as existing tables)

6. **Admin toggle** — respect `DIGEST_ENABLED` and `URGENT_ALERTS_ENABLED` env vars so notifications can be turned off without code changes

### Verification Steps — Phase 7

| # | Test | Method | Pass Condition |
|---|------|--------|---------------|
| 7.1 | Resend integration works | Call `sendEmail` with test data | Email received at test address |
| 7.2 | Digest generates correctly | Call digest endpoint manually | Returns well-formed HTML with correct grant data |
| 7.3 | Empty digest skipped | Call digest with no activity or upcoming deadlines | No email sent, endpoint returns "skipped" |
| 7.4 | Urgent alert fires on status change | Change a grant to "review" status | Email sent with correct grant name |
| 7.5 | Deduplication works | Trigger same alert twice in one day | Only one email sent, second is skipped |
| 7.6 | Cron route secured | Hit `/api/cron/daily-digest` without cron secret | Returns 401 |
| 7.7 | Dashboard link in emails | Inspect any sent email | Contains clickable link to dashboard |
| 7.8 | Toggle works | Set `DIGEST_ENABLED=false`, trigger cron | No email sent |
| 7.9 | Missing Resend key handled | Remove `RESEND_API_KEY`, trigger alert | Logs error, does not crash app |
| 7.10 | Email list from env | Set 3 addresses in `NOTIFICATION_EMAILS` | All 3 receive the email |

### Falsification Criteria — Phase 7

- **F7.1:** The cron endpoint is accessible without Vercel's cron authentication
- **F7.2:** A failed email send crashes the API route or prevents the status change from saving
- **F7.3:** The same urgent alert is sent twice on the same day for the same grant
- **F7.4:** A grant in "submitted" status triggers an overdue alert when its deadline passes
- **F7.5:** The digest email is sent when there are zero items to report
- **F7.6:** Email HTML renders broken in Gmail (test with basic structure — no CSS grid, no flexbox)

---

### Resend Setup (Manual — Operator)

1. Create a free Resend account at resend.com
2. Generate an API key
3. For development: use `onboarding@resend.dev` as the from address
4. For production: add and verify a domain (follow Resend's DNS verification steps)
5. Add `RESEND_API_KEY` to `.env` and Vercel environment variables
6. Set `NOTIFICATION_EMAILS` to the team's email addresses

Document these steps in `docs/OPERATOR_GUIDE.md` alongside the existing Supabase and Vercel setup instructions.
