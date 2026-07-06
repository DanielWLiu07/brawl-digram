import Link from "next/link";

export default function Home() {
  return (
    <main className="mx-auto flex max-w-2xl flex-1 flex-col items-center justify-center gap-6 p-16 text-center">
      <h1 className="text-3xl font-semibold">Brawl Draft Wiki</h1>
      <p className="text-zinc-600 dark:text-zinc-400">
        Stats-backed counters, synergies, tier lists, and ranked maps.
      </p>
      <div className="flex flex-wrap justify-center gap-3">
        <Link
          href="/wiki/brawlers"
          className="rounded border px-4 py-2 hover:bg-zinc-100 dark:hover:bg-zinc-800"
        >
          Brawlers
        </Link>
        <Link
          href="/wiki/maps"
          className="rounded border px-4 py-2 hover:bg-zinc-100 dark:hover:bg-zinc-800"
        >
          Maps
        </Link>
        <Link
          href="/wiki/tier-lists"
          className="rounded border px-4 py-2 hover:bg-zinc-100 dark:hover:bg-zinc-800"
        >
          Tier Lists
        </Link>
      </div>
    </main>
  );
}
