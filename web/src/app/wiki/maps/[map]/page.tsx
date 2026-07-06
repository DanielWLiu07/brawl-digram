import { notFound } from "next/navigation";
import { getMap } from "@/lib/kb";
import { PageHeader } from "@/components/WikiSection";

export default async function MapPage({
  params,
}: {
  params: Promise<{ map: string }>;
}) {
  const { map: raw } = await params;
  const name = decodeURIComponent(raw);

  const m = await getMap(name);
  if (!m) notFound();

  return (
    <main className="mx-auto max-w-3xl space-y-4 p-6">
      <PageHeader backHref="/wiki/maps" backLabel="All maps" title={m.name} />
      <p className="text-sm text-zinc-500">
        Environment: {m.environment}
        {m.inRankedRotation && " · Ranked rotation"}
      </p>
    </main>
  );
}
