"""Turns each new Play AFL story about the club into a club news page on our site.
Runs in the scheduled GitHub Action after fetch-playafl-news.mjs and playafl_images.py; new pages are
committed to the repo so they stay even after the story drops off Play AFL's feed.

Each page has the headline, date, photo (our WebP copy), Play AFL's short summary and a button to the
full story on Play AFL, with a source credit. It does not copy the article text itself: that belongs to
the AFL. To publish a fuller write-up in the club's own words (like the Ryan O'Keefe article), edit the
generated page's text by hand; it won't be overwritten.

Stories the club has already written up (any news page linking to the same Play AFL address) are skipped.
    python tools/playafl_articles.py public"""
import html, json, pathlib, re, sys
from datetime import date

pub = pathlib.Path(sys.argv[1])
news_dir = pub / 'news'
data = json.loads((pub / 'news.json').read_text(encoding='utf-8'))
shell = (news_dir / 'dane-rampe-retires.html').read_text(encoding='utf-8')
MONTHS = 'January February March April May June July August September October November December'.split()

# which Play AFL stories already have a club page, and where
covered = {}
for f in news_dir.glob('*.html'):
    if f.name in ('_template.html', 'index.html'):
        continue
    for url in re.findall(r'href="(https://play\.afl/[^"]+)"', f.read_text(encoding='utf-8')):
        covered.setdefault(url, f.name)


def slugify(t):
    s = re.sub(r'[^a-z0-9]+', '-', re.sub(r"['’]", '', t.lower())).strip('-')
    return s[:60].rstrip('-') or 'story'


def long_date(iso):
    d = date.fromisoformat(iso)
    return f'{d.day} {MONTHS[d.month - 1]} {d.year}'


def nice_title(t):
    # Play AFL sometimes shouts headlines in capitals; our pages style headings in capitals anyway
    return t.title() if t.isupper() else t


# remove generated pages for stories that were looked at this run but no longer qualify
kept = {it['url'] for it in data.get('items', [])}
removed = 0
for url in data.get('checked', []):
    name = covered.get(url)
    if url in kept or not name:
        continue
    f = news_dir / name
    if 'generated from Play AFL' in f.read_text(encoding='utf-8'):
        f.unlink()
        del covered[url]
        removed += 1
if removed:
    print(f'removed {removed} pages for stories that no longer qualify')

made = 0
for it in data.get('items', []):
    url = it['url']
    if url in covered:
        it['page'] = '/news/' + covered[url][:-5]
        # keep the tag on generated pages up to date (hand-written pages are left alone)
        f = news_dir / covered[url]
        t = f.read_text(encoding='utf-8')
        if 'generated from Play AFL' in t:
            t2 = re.sub(r'<span class="pill navy">[^<]*</span>', f'<span class="pill navy">{html.escape(it.get("tag") or "Club news")}</span>', t, count=1)
            if t2 != t:
                f.write_text(t2, encoding='utf-8', newline='\n')
        continue
    if not it.get('date'):
        continue
    name = f"playafl-{slugify(it['title'])}.html"
    it['page'] = '/news/' + name[:-5]
    if (news_dir / name).exists():
        continue
    title = html.escape(nice_title(it['title']))
    summary = html.escape(it.get('summary') or '')
    img = it.get('image')
    head_end = shell.index('</head>')
    head, body = shell[:head_end], shell[head_end:]
    head = re.sub(r'<title>.*?</title>', f'<title>{title} | UNSW-ES Bulldogs</title>', head)
    for prop, val in (('name="description"', summary), ('property="og:title"', title),
                      ('property="og:description"', summary)):
        head = re.sub(r'<meta ' + prop + r' content="[^"]*">', f'<meta {prop} content="{val}">', head)
    og = 'https://www.unswesbulldogs.com.au' + img if img else 'https://www.unswesbulldogs.com.au/share.jpg'
    head = re.sub(r'<meta property="og:image" content="[^"]*">', f'<meta property="og:image" content="{og}">', head)
    m0, m1 = body.index('<main class="art">'), body.index('</main>') + len('</main>')
    more = re.search(r'<div class="more-news">.*?</div></div>', body[m0:m1], flags=re.S).group(0)
    hero = f'\n  <div class="himg"><img src="..{img}" alt="" loading="lazy" decoding="async"></div>' if img else ''
    main = f'''<main class="art">
  <!-- generated from Play AFL by tools/playafl_articles.py; safe to edit by hand -->
  <a class="back" href="../index.html#news">← All news</a>
  <div class="meta"><span class="pill navy">{html.escape(it.get('tag') or 'Club news')}</span><span class="date">{long_date(it['date'])}</span></div>
  <h1>{title}</h1>
  <p class="lede">{summary}</p>{hero}
  <div class="body">
    <p>The full story was published by Play AFL, the home of community football.</p>
  </div>
  <div class="cta"><b>Read the full story</b><a class="btn btn-red" href="{html.escape(url)}" target="_blank" rel="noopener">Read it on Play AFL ↗</a></div>
  <div class="src">Source: <a href="{html.escape(url)}" target="_blank" rel="noopener">Play AFL, {long_date(it['date'])}</a>. Image: Play AFL.</div>
  {more}
</main>'''
    (news_dir / name).write_text(head + body[:m0] + main + body[m1:], encoding='utf-8', newline='\n')
    covered[url] = name
    made += 1

(pub / 'news.json').write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print(f'{made} new club pages from Play AFL stories')
