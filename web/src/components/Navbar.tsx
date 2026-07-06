import Link from "next/link";

const navLinks = [
  { href: "/wiki/brawlers", label: "Brawlers" },
  { href: "/wiki/maps", label: "Maps" },
  { href: "/wiki/tier-lists", label: "Tier Lists" },
];

export default function Navbar() {
  return (
    <header className="sticky top-0 z-50 border-b border-zinc-200 bg-white/90 backdrop-blur dark:border-zinc-800 dark:bg-zinc-950/90">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between gap-4 px-4 sm:px-6">
        <Link
          href="/"
          className="shrink-0 font-semibold tracking-tight text-zinc-900 dark:text-white"
        >
          Brawl Draft Wiki
        </Link>

        <nav className="flex items-center gap-0.5 sm:gap-1">
          {navLinks.map(({ href, label }) => (
            <Link
              key={href}
              href={href}
              className="rounded-md px-2.5 py-2 text-sm font-medium text-zinc-600 transition-colors hover:bg-zinc-100 hover:text-zinc-900 sm:px-3 dark:text-zinc-400 dark:hover:bg-zinc-800 dark:hover:text-white"
            >
              {label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
