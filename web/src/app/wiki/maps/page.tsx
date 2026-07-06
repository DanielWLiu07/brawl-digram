import Link from "next/link";
import { getAllMaps } from "@/lib/kb";

export default async function MapsPage() {
  const list = await getAllMaps();

  return (
    <main className="mx-auto max-w-6xl p-6">
      <h1 className="mb-4 text-2xl font-bold">Maps</h1>
      <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
        {list.map((m) => (
          <Link
            key={m.name}
            href={`/wiki/maps/${encodeURIComponent(m.name)}`}
            className="rounded border p-3 hover:bg-zinc-100 dark:hover:bg-zinc-800"
          >
            <div className="font-medium">{m.name}</div>
            {m.inRankedRotation && (
              <span className="text-xs text-amber-600">Ranked</span>
            )}
          </Link>
        ))}
      </div>
    </main>
  );
}
