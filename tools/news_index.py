"""Builds public/news/index.html: every club article (newest first), plus a 'From Play AFL' list that
the page fills in itself from /api/news. Run after adding an article:  python tools/news_index.py public"""
import html, json, pathlib, re, sys

pub = pathlib.Path(sys.argv[1])
shell = (pub / 'about/partners.html').read_text(encoding='utf-8')  # same depth, same header/footer

MONTHS = 'january february march april may june july august september october november december'.split()


def iso(txt):
    # the date shown on the page, e.g. "23 November 2026" (used when the page isn't stamped yet)
    m = re.match(r'\s*(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})', txt or '')
    return f'{m.group(3)}-{MONTHS.index(m.group(2).lower()) + 1:02d}-{int(m.group(1)):02d}' if m and m.group(2).lower() in MONTHS else ''


items = []
for f in sorted((pub / 'news').glob('*.html')):
    if f.name in ('_template.html', 'index.html'):
        continue
    s = f.read_text(encoding='utf-8')
    ld = re.search(r'<script type="application/ld\+json">(.*?)</script>', s, flags=re.S)
    data = json.loads(ld.group(1)) if ld else {}
    title = re.search(r'<h1>(.*?)</h1>', s, flags=re.S).group(1)
    lede = re.search(r'<p class="lede">(.*?)</p>', s, flags=re.S)
    img = re.search(r'<div class="himg[^"]*"><img src="([^"]*)"', s)
    pill = re.search(r'<span class="pill ?([^"]*)">([^<]*)</span><span class="date">([^<]*)</span>', s)
    src = re.search(r'href="(https://play\.afl/[^"]+)"', s)
    items.append(dict(file=f.name, title=title, lede=lede.group(1) if lede else '', img=img.group(1) if img else '',
                      cls=pill.group(1).strip() if pill else '', tag=pill.group(2) if pill else 'News',
                      date_txt=pill.group(3) if pill else '', date=data.get('datePublished') or iso(pill.group(3) if pill else ''),
                      source=src.group(1) if src else ''))
items.sort(key=lambda x: x['date'], reverse=True)

cards = []
for it in items:
    cls = {'gold': ' gold', 'navy': ' navy'}.get(it['cls'], '')
    thumb = f'<img src="{it["img"]}" alt="" loading="lazy" decoding="async">' if it['img'] else ''
    cards.append(f'''  <article class="ncard{cls}"{f' data-source="{it["source"]}"' if it["source"] else ''}>
    <div class="band"></div>
    <div class="thumb">{thumb}</div>
    <div class="body">
      <div class="meta"><span class="pill">{it['tag']}</span><span class="date">{it['date_txt']}</span></div>
      <h3>{it['title']}</h3>
      <p>{it['lede']}</p>
      <a class="more" href="{it['file']}">Read more →</a>
    </div>
  </article>''')

main = f'''<section class="phero"><div class="wrap"><div class="crumb"><a href="../index.html">Home</a> · News</div><h1>Around the kennel</h1>
<p>Every club announcement, newest first.</p></div></section>
<main class="pc wide">
<h2>Club news</h2>
<div class="news">
{chr(10).join(cards)}
</div>
</main>
'''
head_end = shell.index('</head>')
head = shell[:head_end]
head = re.sub(r'<title>.*?</title>', '<title>News | UNSW-ES Bulldogs</title>', head)
desc = 'Club news from the UNSW-ES Bulldogs: signings, awards, milestones and what is on, plus AFL Sydney and SFL news about the club.'
head = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{desc}">', head)
head = re.sub(r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="News | UNSW-ES Bulldogs">', head)
head = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{desc}">', head)
body = shell[head_end:]
a = body.index('</header>') + len('</header>')
b = body.index('<footer>')
(pub / 'news/index.html').write_text(head + body[:a] + '\n' + main + body[b:], encoding='utf-8', newline='\n')
print('news index:', len(items), 'articles')
