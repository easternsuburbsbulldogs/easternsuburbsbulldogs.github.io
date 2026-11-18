"""Stamps the search-engine and sharing tags into every page for a given web address.

    python tools/seo.py public https://easternsuburbsbulldogs.github.io preview

Safe to run again at any time, for example when the site moves to its final address:

    python tools/seo.py public https://www.unswesbulldogs.com.au

It rewrites the block between <!-- seo --> and <!-- /seo --> in each page's <head>,
points the share images at the given address, and regenerates sitemap.xml and robots.txt.
Page text, layout and links are not touched.
"""
import datetime
import html
import json
import pathlib
import re
import sys

pub = pathlib.Path(sys.argv[1])
SITE = sys.argv[2].rstrip('/')
# Add the word preview at the end to keep every page out of search engines while the club reviews it:
#     python tools/seo.py public https://easternsuburbsbulldogs.github.io preview
PREVIEW = len(sys.argv) > 3 and sys.argv[3] == 'preview'
THEME = '#18296A'
MONTHS = {m: i + 1 for i, m in enumerate(
    'january february march april may june july august september october november december'.split())}

ORG = {
    '@context': 'https://schema.org',
    '@type': 'SportsOrganization',
    'name': 'UNSW-ES Bulldogs',
    'alternateName': ['UNSW-Eastern Suburbs Bulldogs', 'UNSW-ES Bulldogs Australian Football Club'],
    'sport': 'Australian rules football',
    'foundingDate': '1880',
    'url': SITE + '/',
    'logo': SITE + '/app-icon.png',
    'image': SITE + '/share.jpg',
    'email': 'president@unswesbulldogs.com.au',
    'address': {'@type': 'PostalAddress', 'streetAddress': 'c/- Arc @ UNSW Reception, PO Box 173',
                'addressLocality': 'Kingsford', 'addressRegion': 'NSW', 'postalCode': '2032', 'addressCountry': 'AU'},
    'areaServed': 'Eastern Suburbs, Sydney',
    'memberOf': {'@type': 'SportsOrganization', 'name': 'Sydney Football League'},
    'sameAs': ['https://instagram.com/unswesafl', 'https://facebook.com/unswesbulldogsafc',
               'https://www.tiktok.com/@unswesafl'],
}


def iso_date(text):
    m = re.match(r'\s*(?:(\d{1,2})\s+)?([A-Za-z]+)\s+(\d{4})', text)
    if not m or m.group(2).lower() not in MONTHS:
        return None
    out = '%s-%02d' % (m.group(3), MONTHS[m.group(2).lower()])
    return out + ('-%02d' % int(m.group(1)) if m.group(1) else '')


def meta(s, pattern):
    m = re.search(pattern, s)
    return html.unescape(m.group(1)) if m else ''


pages = []
for f in sorted(pub.rglob('*.html')):
    rel = f.relative_to(pub).as_posix()
    s = f.read_text(encoding='utf-8')
    depth = rel.count('/')
    is_404, is_tpl = rel == '404.html', rel.endswith('_template.html')
    prefix = '/' if is_404 else '../' * depth
    path = '/' if rel == 'index.html' else '/' + rel[:-5]
    url = SITE + ('/news/YOUR-FILE-NAME' if is_tpl else path)
    is_news = rel.startswith('news/')

    head_end = s.index('</head>')
    head, body = s[:head_end], s[head_end:]

    head = head.replace('<html lang="en">', '<html lang="en-AU">')
    head = re.sub(r'\n?<!-- seo -->.*?<!-- /seo -->', '', head, flags=re.S)
    head = re.sub(r'\n?<meta (?:property="og:(?:url|type|site_name|locale)"|name="twitter:card")[^>]*>', '', head)
    # only our own images move with the site address; images hosted elsewhere (e.g. play.afl) stay put
    head = re.sub(r'(<meta property="og:image" content=")https?://(?:www\.unswesbulldogs\.com\.au|[a-z0-9-]+\.clubshed\.app)', r'\1' + SITE, head)

    block = ['<!-- seo -->']
    if is_404 or PREVIEW:
        block.append('<meta name="robots" content="noindex">')
    if not is_404:
        block.append('<link rel="canonical" href="%s">' % url)
        block.append('<meta property="og:url" content="%s">' % url)
        block.append('<meta property="og:type" content="%s">' % ('article' if is_news else 'website'))
        block.append('<meta property="og:site_name" content="UNSW-ES Bulldogs">')
        block.append('<meta property="og:locale" content="en_AU">')
        block.append('<meta name="twitter:card" content="summary_large_image">')
    block.append('<meta name="theme-color" content="%s">' % THEME)
    block.append('<link rel="apple-touch-icon" href="%sapp-icon.png">' % prefix)
    if rel == 'index.html':
        block.append('<script type="application/ld+json">%s</script>' % json.dumps(ORG, ensure_ascii=False))
    elif is_news and not is_tpl:
        art = {
            '@context': 'https://schema.org', '@type': 'NewsArticle',
            'headline': meta(head, r'<meta property="og:title" content="([^"]*)"'),
            'description': meta(head, r'<meta name="description" content="([^"]*)"'),
            'image': meta(head, r'<meta property="og:image" content="([^"]*)"'),
            'mainEntityOfPage': url,
            'publisher': {'@type': 'SportsOrganization', 'name': 'UNSW-ES Bulldogs', 'logo': SITE + '/app-icon.png'},
        }
        d = iso_date(meta(body, r'<span class="date">([^<]*)</span>'))
        if d:
            art['datePublished'] = d
        block.append('<script type="application/ld+json">%s</script>' % json.dumps(art, ensure_ascii=False))
    block.append('<script src="%ssite.js"></script>' % prefix)
    block.append('<!-- /seo -->')
    head = head.rstrip('\n') + '\n' + '\n'.join(block) + '\n'

    # header and footer crest: the oval logo instead of the square app tile
    body = re.sub(r'<img class="crestimg" src="([^"]*?)app-icon\.png"', r'<img class="crestimg" src="\1crest.png" width="304" height="199"', body)
    body = body.replace('<span class="car">▼</span>', '<span class="car" aria-hidden="true"></span>')

    f.write_text(head + body, encoding='utf-8', newline='\n')
    if not is_404 and not is_tpl:
        pages.append(url)

today = datetime.date.today().isoformat()
pages.sort(key=lambda u: (u != SITE + '/', u))
sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
sm += ['  <url><loc>%s</loc><lastmod>%s</lastmod></url>' % (u, today) for u in pages]
sm.append('</urlset>')
(pub / 'sitemap.xml').write_text('\n'.join(sm) + '\n', encoding='utf-8', newline='\n')
(pub / 'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n' % SITE, encoding='utf-8', newline='\n')
print('stamped %d pages for %s' % (len(pages), SITE))
