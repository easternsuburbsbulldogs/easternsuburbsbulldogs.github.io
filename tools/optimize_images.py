"""Makes small WebP copies of the site's photos and logos (sized for how they are shown) and points the
pages at them. Social-share images (og:image) stay as JPG. Safe to re-run after adding images.
    python tools/optimize_images.py public
To add a new image to the list, add a line to JOBS: (source file, output file, max width, crop box or None)."""
import pathlib, re, sys
from PIL import Image

pub = pathlib.Path(sys.argv[1])
DL = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else None   # folder with downloaded play.afl originals

JOBS = [
    ('hero2.jpg', 'hero2.webp', 1400, None),
    ('coach-jordy.jpg', 'coach-jordy.webp', 760, None),
    ('coach-jordy-wide.jpg', 'coach-jordy-wide.webp', 800, None),
    ('prem-trophies.jpg', 'prem-trophies.webp', 900, None),
    ('news-rampe.jpg', 'news-rampe.webp', 760, None),
    ('news-pride.jpg', 'news-pride.webp', 900, None),
    ('news-sfl.jpg', 'news-sfl.webp', 760, None),
    ('jordan.jpg', 'jordan.webp', 300, None),
    ('crest.png', 'crest.webp', 200, None),
    ('map-preseason.jpg', 'map-preseason.webp', 840, None),
    ('map-inseason.jpg', 'map-inseason.webp', 840, None),
    ('map-gameday.jpg', 'map-gameday.webp', 840, None),
] + [(f'partners/{p}.png', f'partners/{p}.webp', 320, None)
     for p in ('avc', 'azura', 'fwbuilding', 'kensington', 'ppd', 'souvlaki', 'unsw')] \
  + [(f'coaches/{c}.jpg', f'coaches/{c}.webp', 240, None)
     for c in ('alex-dawes', 'jake-brown', 'jamie-grant', 'jared-anderson', 'kieran-emery', 'paul-love', 'steven-chichester')]

# play.afl originals (downloaded once into DL): news images and headshots, hosted here instead of hot-linked
PLAYAFL = {
    'https://play.afl/sites/default/files/2026-11/Tom%20Williamson_0.jpg': 'news-willo',
    'https://play.afl/sites/default/files/2026-10/Ryan%20O%27Keefe%20appointment.png': 'news-okeefe',
}
if DL:
    JOBS += [
        (DL / 'willo.jpg', 'news-willo.webp', 900, None),
        (DL / 'willo.jpg', 'news-willo.jpg', 1200, None),
        (DL / 'willo.jpg', 'coaches/tom-williamson.webp', 240, (1040, 140, 1560, 660)),
        (DL / 'okeefe.png', 'news-okeefe.webp', 900, None),
        (DL / 'okeefe.png', 'news-okeefe.jpg', 1200, None),
        (DL / 'okeefe.png', 'coaches/ryan-okeefe.webp', 240, (525, 70, 965, 510)),
    ]

total_in = total_out = 0
for src, out, width, box in JOBS:
    src = src if isinstance(src, pathlib.Path) else pub / src
    if not src.exists():
        continue
    im = Image.open(src)
    if box:
        im = im.crop(box)
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    dest = pub / out
    if out.endswith('.jpg'):
        im.convert('RGB').save(dest, quality=82, optimize=True, progressive=True)
    else:
        keep_alpha = im.mode in ('RGBA', 'LA', 'P')
        im.convert('RGBA' if keep_alpha else 'RGB').save(dest, 'WEBP', quality=80, method=6)
    total_in += src.stat().st_size
    total_out += dest.stat().st_size

# point pages at the new files: <img src>, data-img (player pop-ups) and the generator scripts; og:image stays JPG
swap = {s if isinstance(s, str) else '': o for s, o, _, _ in JOBS if isinstance(s, str) and o.endswith('.webp')}
pages = list(pub.rglob('*.html'))
for f in pages:
    s = f.read_text(encoding='utf-8')
    t = s
    for old, new in swap.items():
        t = re.sub(r'((?:src|data-img)="(?:\.\./|/)?)' + re.escape(old) + '"', r'\g<1>' + new + '"', t)
    if DL:
        for url, name in PLAYAFL.items():
            t = re.sub(r'(src|data-img)="' + re.escape(url) + '"', lambda m: f'{m.group(1)}="{"../" * f.relative_to(pub).as_posix().count("/")}{name}.webp"', t)
            t = t.replace(f'content="{url}"', f'content="https://www.unswesbulldogs.com.au/{name}.jpg"')
            t = t.replace(f'"image": "{url}"', f'"image": "https://www.unswesbulldogs.com.au/{name}.jpg"')
    if t != s:
        f.write_text(t, encoding='utf-8', newline='\n')
print(f'images: {total_in // 1024} KB of originals -> {total_out // 1024} KB')
