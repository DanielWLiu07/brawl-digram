import "./load-env"; // MUST be first — loads DATABASE_URL
import { db } from "./index";
import {
  brawlers,
  edges,
  maps,
  tierLists,
  tierListEntries,
} from "./schema";
import fs from "node:fs";
import path from "node:path";

const DATA = path.join(process.cwd(), "..", "data"); // web/ -> repo-root/data

interface BrawlersFile {
  brawlers: { name: string }[];
}

interface MatrixEdge {
  a: string;
  b: string;
  delta: number;
}

interface BrawlerStrength {
  rank: number;
}

interface SynergyMatrixFile {
  synergy: MatrixEdge[];
  counter: MatrixEdge[];
  brawlerStrength: Record<string, BrawlerStrength>;
}

interface MapsFile {
  maps: Record<
    string,
    {
      likelyRanked?: boolean;
    }
  >;
}

type EdgeRow = {
  a: string;
  b: string;
  type: "synergy" | "counter";
  strength: number;
};

type Tier = "S" | "A" | "B" | "C" | "D" | "E";

const read = <T>(f: string): T =>
  JSON.parse(fs.readFileSync(path.join(DATA, f), "utf8")) as T;

function rankToTier(rank: number): Tier {
  if (rank <= 17) return "S";
  if (rank <= 34) return "A";
  if (rank <= 51) return "B";
  if (rank <= 68) return "C";
  if (rank <= 85) return "D";
  return "E";
}

async function main() {
  // --- 1) brawlers (the FK target — must exist before edges) ---
  const names: string[] = read<BrawlersFile>("brawlers.json").brawlers.map(
    (b) => b.name,
  );

  // --- 2) name normalizer: UPPERCASE (matrix) -> canonical Title Case (brawlers.json) ---
  const up2canon = new Map(names.map((n) => [n.toUpperCase(), n]));
  const norm = (raw: string) => up2canon.get(raw.toUpperCase()) ?? null;

  // --- 3) build edge rows from the data-backed matrix ---
  const m = read<SynergyMatrixFile>("draft_synergy_matrix.json");
  const toRow = (e: MatrixEdge, type: "synergy" | "counter"): EdgeRow | null => {
    const a = norm(e.a);
    const b = norm(e.b);
    return a && b ? { a, b, type, strength: e.delta } : null;
  };
  const edgeRows = [
    ...m.synergy.map((e) => toRow(e, "synergy")),
    ...m.counter.map((e) => toRow(e, "counter")),
  ].filter((r): r is EdgeRow => r !== null);

  // --- 4) maps (ranked pool from maps.json) ---
  const mapsData = read<MapsFile>("maps.json");
  const mapRows = Object.entries(mapsData.maps)
    .filter(([, map]) => map.likelyRanked)
    .map(([name]) => ({
      name,
      environment: "canyon" as const,
      inRankedRotation: true,
      inTrophyRotation: false,
    }));

  // --- 5) tier list entries from stats ranks ---
  const tierRows = Object.entries(m.brawlerStrength)
    .map(([raw, s]) => {
      const brawler = norm(raw);
      if (!brawler) return null;
      return { brawler, tier: rankToTier(s.rank) };
    })
    .filter((r): r is { brawler: string; tier: Tier } => r !== null);

  // --- 6) write to Postgres (delete children first) ---
  await db.delete(tierListEntries);
  await db.delete(tierLists);
  await db.delete(edges);
  await db.delete(maps);

  await db
    .insert(brawlers)
    .values(names.map((name) => ({ name })))
    .onConflictDoNothing();

  await db.insert(edges).values(edgeRows);
  await db.insert(maps).values(mapRows).onConflictDoNothing();

  const [rankedList] = await db
    .insert(tierLists)
    .values({
      name: "Ranked (stats)",
      scope: "ranked",
      patchVersion: "2026-06",
    })
    .returning({ id: tierLists.id });

  await db.insert(tierListEntries).values(
    tierRows.map((row) => ({
      tierListId: rankedList.id,
      brawler: row.brawler,
      tier: row.tier,
    })),
  );

  console.log(
    `seeded: ${names.length} brawlers, ${edgeRows.length} edges, ${mapRows.length} maps, ${tierRows.length} tier entries`,
  );
}

main()
  .then(() => process.exit(0))
  .catch((e: unknown) => {
    console.error(e);
    process.exit(1);
  });
