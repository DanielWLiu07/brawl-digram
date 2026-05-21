"""Pull all Brawlify CDN assets into /assets and write a manifest.
Idempotent: existing files are skipped. Re-run after each patch to refresh.

Layout (human-browseable):
  assets/
    brawlers/<BrawlerHash>/portrait.png
    brawlers/<BrawlerHash>/render.png
    brawlers/<BrawlerHash>/emoji.png
    brawlers/<BrawlerHash>/gadgets/<Gadget-Path>.png
    brawlers/<BrawlerHash>/star-powers/<Star-Power-Path>.png
    maps/<Map-Hash>.png
    game-modes/<Mode-Hash>.png
    manifest.json
"""
import json, re, urllib.request, urllib.error
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

REPO = Path(__file__).resolve().parent.parent
ASSETS = REPO / 'assets'
HDRS = {'User-Agent': 'Mozilla/5.0 (brawl-digram dev)'}

def fetch_json(url):
    req = urllib.request.Request(url, headers=HDRS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def safe(name):
    """Filesystem-safe slug. Brawlify hashes/paths are usually already clean."""
    return re.sub(r'[^\w\-]+', '-', name).strip('-') or 'unknown'

def slug(item, *, fields=('hash', 'path')):
    for f in fields:
        if item.get(f):
            return safe(item[f])
    return f"id-{item.get('id', 'unknown')}"

def download(url, dest):
    if not url:
        return 'noop', 0
    if dest.exists() and dest.stat().st_size > 0:
        return 'skip', dest.stat().st_size
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        req = urllib.request.Request(url, headers=HDRS)
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read()
        dest.write_bytes(data)
        return 'ok', len(data)
    except urllib.error.HTTPError as e:
        return f'err-{e.code}', 0
    except Exception as e:
        return f'err-{type(e).__name__}', 0

def build_tasks():
    print('Fetching API indexes…')
    brawlers  = fetch_json('https://api.brawlify.com/v1/brawlers')['list']
    gamemodes = fetch_json('https://api.brawlify.com/v1/gamemodes')['list']
    maps      = fetch_json('https://api.brawlify.com/v1/maps')['list']

    tasks = []
    for b in brawlers:
        bdir = ASSETS / 'brawlers' / slug(b)
        tasks.append((b.get('imageUrl'),  bdir / 'portrait.png'))
        tasks.append((b.get('imageUrl2'), bdir / 'render.png'))
        tasks.append((b.get('imageUrl3'), bdir / 'emoji.png'))
        for g in b.get('gadgets', []):
            tasks.append((g.get('imageUrl'), bdir / 'gadgets' / f"{slug(g)}.png"))
        for sp in b.get('starPowers', []):
            tasks.append((sp.get('imageUrl'), bdir / 'star-powers' / f"{slug(sp)}.png"))

    for m in gamemodes:
        tasks.append((m.get('imageUrl'), ASSETS / 'game-modes' / f"{slug(m)}.png"))

    for m in maps:
        if m.get('disabled'):
            continue
        tasks.append((m.get('imageUrl'), ASSETS / 'maps' / f"{slug(m)}.png"))

    manifest = {
        'fetchedAt': __import__('datetime').datetime.utcnow().isoformat() + 'Z',
        'brawlers':  brawlers,
        'gameModes': gamemodes,
        'maps':      maps,
    }
    return tasks, manifest

def run():
    tasks, manifest = build_tasks()
    print(f'Downloading {len(tasks)} files…')

    stats = {}
    total_bytes = 0
    with ThreadPoolExecutor(max_workers=24) as pool:
        futures = {pool.submit(download, u, d): (u, d) for u, d in tasks}
        for i, fut in enumerate(as_completed(futures), 1):
            status, size = fut.result()
            stats[status] = stats.get(status, 0) + 1
            total_bytes += size
            if i % 200 == 0:
                print(f'  {i}/{len(tasks)} done…', flush=True)

    print('\n=== summary ===')
    for k in sorted(stats):
        print(f'  {k}: {stats[k]}')
    print(f'  total size on disk: {total_bytes/1024/1024:.1f} MB')

    (ASSETS / 'manifest.json').write_text(json.dumps(manifest, indent=2))
    print(f'  manifest: {(ASSETS/"manifest.json").stat().st_size/1024:.1f} KB')

if __name__ == '__main__':
    run()
