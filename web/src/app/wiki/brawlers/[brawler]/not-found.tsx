import Link from "next/link";

export default function NotFound() {
  return (
    <main className="mx-auto max-w-md space-y-4 p-16 text-center">
      <h1 className="text-2xl font-bold">Brawler not found</h1>
      <Link href="/wiki/brawlers" className="text-sm text-zinc-500 hover:underline">
        ← Back to all brawlers
      </Link>
    </main>
  );
}
