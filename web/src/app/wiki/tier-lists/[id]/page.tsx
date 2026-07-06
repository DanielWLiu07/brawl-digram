import Link from "next/link";
import { notFound } from "next/navigation";
import { getTierList } from "@/lib/kb";
import { PageHeader } from "@/components/WikiSection";

const TIER_ORDER = ["S", "A", "B", "C", "D", "E"] as const;

export default async function TierListPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id: raw } = await params;
  const id = Number(raw);
  if (Number.isNaN(id)) notFound();

  const data = await getTierList(id);
  if (!data) notFound();

  const { list, entries } = data;

  return (
    <main className="mx-auto max-w-5xl space-y-6 p-6">
      <PageHeader
        backHref="/wiki/tier-lists"
        backLabel="All tier lists"
        title={list.name}
      />
      <p className="text-sm text-zinc-500">
        {list.scope} · patch {list.patchVersion}
      </p>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-6">
        {TIER_ORDER.map((tier) => {
          const rows = entries.filter((e) => e.tier === tier);
          return (
            <section key={tier} className="rounded border p-3">
              <h2 className="mb-2 font-bold">{tier}</h2>
              <ul className="space-y-1 text-sm">
                {rows.map((e) => (
                  <li key={e.brawler}>
                    <Link
                      href={`/wiki/brawlers/${encodeURIComponent(e.brawler)}`}
                      className="hover:underline"
                    >
                      {e.brawler}
                    </Link>
                  </li>
                ))}
              </ul>
            </section>
          );
        })}
      </div>
    </main>
  );
}
