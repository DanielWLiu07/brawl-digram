# Brawl Draft Wiki (web)

Next.js App Router app for the read-only draft wiki. Server Components query Neon Postgres via Drizzle — no API routes.

## Setup

```bash
cd web
npm install
cp .env.example .env.local   # add your Neon DATABASE_URL
npm run db:seed
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) (or `-p 3002` if 3000 is taken).

## Scripts

| Command | What |
|---------|------|
| `npm run dev` | Dev server |
| `npm run build` | Production build |
| `npm run db:seed` | Load `data/brawlers.json`, `draft_synergy_matrix.json`, `maps.json` into Postgres |

## Routes

| Path | Description |
|------|-------------|
| `/` | Home |
| `/wiki/brawlers` | All brawlers |
| `/wiki/brawlers/[name]` | Counters, synergies, tier placement |
| `/wiki/maps` | Ranked maps |
| `/wiki/maps/[name]` | Map detail |
| `/wiki/tier-lists` | Tier list index |
| `/wiki/tier-lists/[id]` | Tier columns (S–E) |

## Layout

```
src/
├── app/           routes (pages)
├── components/    Navbar, WikiSection
├── db/            schema, seed, Drizzle client
└── lib/kb.ts      server-only query layer
```

Seed reads JSON from repo-root `data/` (run from `web/`).
