import Link from "next/link";
import { getTierLists } from "@/lib/kb";

export default async function TierListsPage() {
  const lists = await getTierLists();

  return (
    <main className="mx-auto max-w-3xl p-6">
      <h1 className="mb-4 text-2xl font-bold">Tier Lists</h1>
      <ul className="space-y-2">
        {lists.map((list) => (
          <li key={list.id}>
            <Link
              href={`/wiki/tier-lists/${list.id}`}
              className="hover:underline"
            >
              {list.name}
            </Link>
            <span className="ml-2 text-sm text-zinc-500">({list.scope})</span>
          </li>
        ))}
      </ul>
    </main>
  );
}
