import { notFound } from "next/navigation";
import { getBrawler, getBrawlerEdges, getBrawlerTiers } from "@/lib/kb";
import { MatchupSection, PageHeader, Section } from "@/components/WikiSection";

export default async function BrawlerPage({
  params,
}: {
  params: Promise<{ brawler: string }>;
}) {
  const { brawler: raw } = await params;
  const name = decodeURIComponent(raw);

  const b = await getBrawler(name);
  if (!b) notFound();

  const edges = await getBrawlerEdges(b.name);
  const tiers = await getBrawlerTiers(b.name);

  return (
    <main className="mx-auto max-w-3xl space-y-6 p-6">
      <PageHeader
        backHref="/wiki/brawlers"
        backLabel="All brawlers"
        title={b.name}
      />

      <Section
        title="Tier placements"
        rows={tiers.map((t) => `${t.list}: ${t.tier}`)}
      />
      <MatchupSection title="Counters (beats)" items={edges.counters.map((e) => ({ name: e.opponent, strength: e.strength }))} />
      <MatchupSection title="Countered by" items={edges.counteredBy.map((e) => ({ name: e.opponent, strength: e.strength }))} />
      <MatchupSection title="Synergies" items={edges.synergies.map((e) => ({ name: e.partner, strength: e.strength }))} />
    </main>
  );
}
