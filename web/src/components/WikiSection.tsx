import Link from "next/link";

type Item = { name: string; strength: number };

export function MatchupSection({
  title,
  items,
}: {
  title: string;
  items: Item[];
}) {
  return (
    <section>
      <h2 className="font-semibold">{title}</h2>
      {items.length ? (
        <ul className="list-disc pl-5">
          {items.map((item) => (
            <li key={item.name}>
              <Link
                href={`/wiki/brawlers/${encodeURIComponent(item.name)}`}
                className="hover:underline"
              >
                {item.name}
              </Link>{" "}
              ({item.strength.toFixed(2)})
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-zinc-500 text-sm">none</p>
      )}
    </section>
  );
}

export function Section({ title, rows }: { title: string; rows: string[] }) {
  return (
    <section>
      <h2 className="font-semibold">{title}</h2>
      {rows.length ? (
        <ul className="list-disc pl-5">
          {rows.map((r) => (
            <li key={r}>{r}</li>
          ))}
        </ul>
      ) : (
        <p className="text-zinc-500 text-sm">none</p>
      )}
    </section>
  );
}

export function PageHeader({
  backHref,
  backLabel,
  title,
}: {
  backHref: string;
  backLabel: string;
  title: string;
}) {
  return (
    <>
      <Link href={backHref} className="text-sm text-zinc-500 hover:underline">
        ← {backLabel}
      </Link>
      <h1 className="text-2xl font-bold">{title}</h1>
    </>
  );
}
