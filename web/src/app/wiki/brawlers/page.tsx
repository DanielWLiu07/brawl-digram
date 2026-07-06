import Link from "next/link";
import { getAllBrawlers } from "@/lib/kb";

export default async function BrawlersPage() {
  const list = await getAllBrawlers();

  return (
    <main className="mx-auto max-w-6xl p-6">
      <h1 className="mb-4 text-2xl font-bold">Brawlers</h1>
      <div className="grid grid-cols-4 gap-3 md:grid-cols-8">
        {list.map((b) => (
          <Link
            key={b.name}
            href={`/wiki/brawlers/${encodeURIComponent(b.name)}`}
            className="rounded border p-3 text-center hover:bg-zinc-100 dark:hover:bg-zinc-800"
          >
            {b.name}
          </Link>
        ))}
      </div>
    </main>
  );
}
