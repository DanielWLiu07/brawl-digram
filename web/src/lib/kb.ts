import "server-only";
import { db } from "@/db";
import { brawlers, edges, maps, tierLists, tierListEntries } from "@/db/schema";
import { eq, or, asc, sql } from "drizzle-orm";

export async function getAllBrawlers() {
  return db.select().from(brawlers).orderBy(asc(brawlers.name));
}

export async function getBrawler(name: string) {
  const [b] = await db
    .select()
    .from(brawlers)
    .where(sql`lower(${brawlers.name}) = ${name.toLowerCase()}`);
  return b ?? null;
}

// Directional edges: "b beats a" (counter) / "b pairs with a" (synergy)
export async function getBrawlerEdges(name: string) {
  const rows = await db
    .select()
    .from(edges)
    .where(or(eq(edges.a, name), eq(edges.b, name)));

  return {
    counters: rows
      .filter((e) => e.type === "counter" && e.b === name)
      .map((e) => ({ opponent: e.a, strength: e.strength })),
    counteredBy: rows
      .filter((e) => e.type === "counter" && e.a === name)
      .map((e) => ({ opponent: e.b, strength: e.strength })),
    synergies: rows
      .filter((e) => e.type === "synergy")
      .map((e) => ({
        partner: e.a === name ? e.b : e.a,
        strength: e.strength,
      })),
  };
}

export async function getBrawlerTiers(name: string) {
  return db
    .select({
      list: tierLists.name,
      tier: tierListEntries.tier,
      scope: tierLists.scope,
    })
    .from(tierListEntries)
    .innerJoin(tierLists, eq(tierListEntries.tierListId, tierLists.id))
    .where(eq(tierListEntries.brawler, name));
}

export async function getAllMaps() {
  return db.select().from(maps).orderBy(asc(maps.name));
}

export async function getMap(name: string) {
  const [m] = await db.select().from(maps).where(eq(maps.name, name));
  return m ?? null;
}

export async function getTierLists() {
  return db.select().from(tierLists);
}

export async function getTierList(id: number) {
  const entries = await db
    .select()
    .from(tierListEntries)
    .where(eq(tierListEntries.tierListId, id));
  const [list] = await db.select().from(tierLists).where(eq(tierLists.id, id));
  return list ? { list, entries } : null;
}
