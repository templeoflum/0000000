# hedawnism.com — Site Architecture

## Stack

| Layer | Tool | Reason |
|---|---|---|
| Framework | SvelteKit | Lean, expressive, ideal for interactive/visual content |
| Hosting | Cloudflare Pages | Unlimited bandwidth free tier, handles delivery |
| Database + Auth | Supabase | Postgres, auth, real-time — generous free tier |
| Media Storage | Backblaze B2 + Cloudflare CDN | B2/CF are bandwidth alliance partners — egress is free. ~$0.006/GB/month storage only |
| Domain | Cloudflare Registrar | At-cost pricing, native DNS/CDN, same ecosystem as hosting |

### Storage Split

| Asset Type | Where |
|---|---|
| Video animations (can exceed 1GB each) | Backblaze B2 → Cloudflare CDN |
| Audio masters, stems | Backblaze B2 → Cloudflare CDN |
| Project files (Ableton, Resolume, etc.) | Backblaze B2 → Cloudflare CDN |
| Cover art, visual artwork | Backblaze B2 → Cloudflare CDN |
| Thumbnails, UI assets | Cloudflare Pages static |
| All metadata and content | Supabase Postgres |

> Note: Supabase storage is not used for media. B2 handles all files. Supabase is database only.

---

## Repository Structure

```
hedawnism.com/
├── src/
│   ├── routes/
│   │   ├── +layout.svelte          # Global shell
│   │   ├── +page.svelte            # Landing / entry point
│   │   ├── explore/                # The whole inner world — unified traversable graph
│   │   │   ├── +page.svelte        # Explorer home / map
│   │   │   ├── [slug]/             # Any node: concept, myth, archetype, release, artwork, etc.
│   │   │   └── releases/           # Filtered lens — portfolio view of release nodes only
│   │   ├── workshop/               # Outward-facing, practical
│   │   │   ├── +page.svelte        # Workshop home
│   │   │   ├── tools/              # Curated software and tools directory
│   │   │   ├── guides/             # How-to content, workflows, tutorials
│   │   │   └── spotlights/         # Creators and orgs worth knowing
│   │   ├── community/              # Future phase
│   │   └── about/│   │   ├── community/              # Future phase
│   │   └── about/
│   ├── lib/
│   │   ├── components/             # Shared UI
│   │   ├── stores/                 # Svelte stores (state)
│   │   ├── supabase.js             # Client init
│   │   └── types/                  # TypeScript interfaces
│   └── app.html
├── static/                         # Static assets
├── supabase/
│   └── migrations/                 # DB schema versioned
└── .env
```

---

## Database Schema (Supabase)

### `nodes` — Unified explorer graph
Every traversable thing in the explorer is a node. Type determines how it renders.
```sql
id            uuid primary key
slug          text unique
title         text
type          text              -- 'concept' | 'archetype' | 'myth' | 'ethic' | 'illusion' 
                                --  | 'thought_experiment' | 'release' | 'artwork' | 'visual'
body          jsonb             -- Rich structured content
tags          text[]
related       uuid[]            -- Cross-links to other nodes (traversal edges)
published     boolean
created_at    timestamptz
```

### `assets` — Files belonging to a release node
```sql
id            uuid primary key
node_id       uuid references nodes(id)
role          text              -- 'master' | 'stem' | 'video' | 'cover' | 'project_file' | 'visual' | 'other'
format        text              -- 'wav' | 'mp3' | 'flac' | 'mp4' | 'als' | 'png' | etc.
label         text              -- e.g. "Ableton Live Set", "Stems ZIP"
url           text              -- Backblaze B2 URL
size_bytes    bigint
duration_ms   int               -- audio/video only
license       text              -- 'CC-BY-NC-SA-4.0' default, can vary per asset
created_at    timestamptz
```

### `workshop_items` — Tools, guides, spotlights
```sql
id            uuid primary key
slug          text unique
category      text              -- 'tool' | 'guide' | 'spotlight'
title         text
body          jsonb
url           text              -- external link where relevant
tags          text[]
published     boolean
created_at    timestamptz
```

### `users` (future community phase)
```sql
id            uuid references auth.users
display_name  text
bio           text
created_at    timestamptz
```

---

## Navigation

```
Explore   Workshop   Community
```

**Explore** — the whole inner world of Hedawnism. One unified traversable graph of concepts, archetypes, myths, thought experiments, ethics, optical illusions, artwork, music, video, and visual work. A release page and a philosophy entry are both nodes — you can arrive at a piece of music through the idea that generated it, or arrive at an idea through the artwork it produced. `/explore/releases` is a filtered lens on the same graph for visitors who want the portfolio view specifically.

**Workshop** — outward-facing and practical. Tools you can use locally and cheaply, guides built from real practice, spotlights on creators and organizations worth knowing.

**Community** — future phase.

---

## Content Architecture — The Explorer Graph

Every node in the explorer has:
- Title + rich body content
- Type (determines render template)
- Related nodes (traversal edges — the connective tissue)
- Tags
- Optional assets (for release/artwork nodes)

Navigation is non-linear. No enforced hierarchy. A visitor enters anywhere and follows relation links through the graph. The experience mirrors how the ideas and works actually connect to each other.

---

## Open Source Distribution Model

Everything on hedawnism.com is free to use, reuse, and repurpose for personal use, local community development, and nonprofit purposes. Commercial use and for-profit monetization is not permitted.

Default license: **CC BY-NC-SA 4.0**
- Free for personal, educational, community, and nonprofit use
- Derivatives must carry the same license
- Commercial monetization requires separate permission

Each release surfaces:
- Stream/preview (audio player, video embed)
- Download options per asset with clear labels (Master WAV, Stems ZIP, Ableton Set, etc.)
- License badge + plain-language summary
- Attribution guidance

Goal: zero friction between finding something and being able to use it.

---

## Phases

### Phase 0 — Foundation
- Repo init, SvelteKit + Supabase wired
- Cloudflare Pages deployment pipeline
- Backblaze B2 bucket configured, Cloudflare CDN pointed at it
- Domain migrated from Squarespace to Cloudflare Registrar
- Auth scaffold (Supabase)
- DB schema deployed

### Phase 1 — Explorer
- Node CRUD (admin only initially)
- Explorer browse + graph traversal via related links
- Individual node pages — type-aware rendering
- Basic search and tag filtering
- `/explore/releases` filtered view

### Phase 2 — Workshop
- Tools directory
- Guides
- Spotlights

### Phase 3 — Community
- User accounts
- Comments and annotations on nodes
- Favorites / collections
- Possible: community-contributed nodes (moderated)

---

## Domain Migration Path

1. Unlock domain in Squarespace
2. Get auth code
3. Transfer to Cloudflare Registrar
4. Update nameservers (Cloudflare takes over DNS)
5. Add hedawnism.com to Cloudflare Pages project
6. SSL auto-provisioned by Cloudflare

Migration window: ~7 days for registrar transfer propagation.

---

## Cost Estimate

| Service | Cost |
|---|---|
| Cloudflare Pages | Free |
| Cloudflare Registrar | ~$10/yr |
| Backblaze B2 | ~$0.006/GB/month storage — egress to Cloudflare is free |
| Supabase | Free tier (500MB DB) |
| **Base total** | **~$10/yr + B2 storage** |

Example: 500GB of video, audio, and project files = ~$3/month. Scales linearly with what you upload, no egress surprises.
