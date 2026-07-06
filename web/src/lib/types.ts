export type Confidence = "pro" | "stats" | "community" | "llm-draft";
export type Role = "tank" | "assassin" | "support" | "controller" | "marksman" | "damage-dealer";
export type PickTiming = "early" | "flex" | "late";
export type EdgeKind = "counter" | "synergy";

// Per-brawler general timing entry (the pick-timing layer).
export interface TimingEntry {
  brawler: string; // display name, matches brawlers.json
  role: Role;
  pickTiming: PickTiming;
  timingReason: string; // one line — WHY (the LLM reads this to explain)
  banPriority: number; // 0..1
  confidence: Confidence;
  patchVersion: string;
  lastVerified: string; // ISO date
}

// Map-specific override — only present when a map genuinely shifts a brawler.
export interface MapOverride {
  brawler: string;
  mapKey: string; // INTERNAL grid name
  pickTiming?: PickTiming;
  timingReason?: string;
  banPriority?: number;
  positioning?: string; // one line — where to play it
  notes?: string;
  confidence: Confidence;
  lastVerified: string;
}

// Counter/synergy edge. Directional: b beats a (counter) / pairs with a (synergy).
export interface Edge {
  a: string;
  b: string;
  type: EdgeKind;
  deltaRating: number; // signed, log-odds-ish
  reason: string;
  modeContext: string | null;
  confidence: Confidence;
  statsCheck?: string;
  source?: string;
  patchVersion: string;
  lastVerified: string;
}

// Shape a brawler page needs for its edges section.
export interface BrawlerEdges {
  counters: Edge[]; // brawlers THIS brawler beats
  counteredBy: Edge[]; // brawlers that beat THIS brawler
  synergies: Edge[];
}
