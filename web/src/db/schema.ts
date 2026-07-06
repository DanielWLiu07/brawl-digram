import {
  pgTable,
  pgEnum,
  serial,
  integer,
  text,
  real,
  boolean,
  unique,
} from "drizzle-orm/pg-core";

// Enums
export const edgeType = pgEnum("edge_type", ["counter", "synergy"]);
export const tierRank = pgEnum("tier_rank", ["S", "A", "B", "C", "D", "E"]);
export const tierScope = pgEnum("tier_scope", ["ranked", "map", "global"]);
export const userRole = pgEnum("user_role", ["contributor", "reviewer", "admin"]);
export const mapEnvironment = pgEnum("map_environment", [
  "canyon", "jungle", "snow", "desert", "beach",
  "volcano", "city", "factory", "space", "underwater",
]);

// Tables
export const brawlers = pgTable("brawlers", {
  name: text("name").primaryKey(),
});

export const edges = pgTable("edges", {
  id: serial("id").primaryKey(),
  a: text("a").notNull().references(() => brawlers.name),
  b: text("b").notNull().references(() => brawlers.name),
  type: edgeType("type").notNull(),
  strength: real("strength").notNull(),
});

export const maps = pgTable("maps", {
  name: text("name").primaryKey(),
  environment: mapEnvironment("environment").notNull(),
  inRankedRotation: boolean("in_ranked_rotation").notNull().default(false),
  inTrophyRotation: boolean("in_trophy_rotation").notNull().default(false),
});

export const tierLists = pgTable("tier_lists", {
  id: serial("id").primaryKey(),
  name: text("name").notNull(),
  scope: tierScope("scope").notNull(),
  mapKey: text("map_key").references(() => maps.name), // set only when scope = 'map'
  patchVersion: text("patch_version").notNull(),
});

export const tierListEntries = pgTable(
  "tier_list_entries",
  {
    id: serial("id").primaryKey(),
    tierListId: integer("tier_list_id").notNull().references(() => tierLists.id),
    brawler: text("brawler").notNull().references(() => brawlers.name),
    tier: tierRank("tier").notNull(),
  },
  (t) => ({
    uq: unique().on(t.tierListId, t.brawler),
  }),
);

export const users = pgTable("users", {
  id: serial("id").primaryKey(),
  username: text("username").notNull().unique(),
  role: userRole("role").notNull().default("contributor"),
});
