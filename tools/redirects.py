"""Forwarding pages for the old Wix addresses, so links and Google rankings carry over to the new pages.
Each old address (e.g. /afl-players-2) gets a tiny page that sends the visitor straight to the new one.
Edit MAP and run:  python tools/redirects.py public https://www.unswesbulldogs.com.au"""
import pathlib, sys

pub = pathlib.Path(sys.argv[1])
SITE = sys.argv[2].rstrip('/')

MAP = {
    # old Wix address   -> new page
    'registration':        '/#join',
    'transfer-request':    '/#join',
    'football':            '/football/mens',
    'men-s-senior-grades': '/football/mens',
    'women-s-football':    '/football/womens',
    'youth-juniors':       '/football/youth-juniors',
    'insurance':           '/football/insurance',
    'our-club':            '/about/our-story',
    'about':               '/about/our-story',
    'history':             '/about/our-story',
    'honour-board':        '/about/honour-board',
    'afl-players-2':       '/about/afl-players',
    'our-partners':        '/about/partners',
    'governance':          '/about/rules',
    'news-events':         '/news/',
    'contact':             '/#contact',
}

for old, new in MAP.items():
    url = SITE + new
    page = f'''<!DOCTYPE html>
<html lang="en-AU"><head><meta charset="utf-8">
<!-- forwarding page (tools/redirects.py): old Wix address -> new page -->
<title>Moved | UNSW-ES Bulldogs</title>
<link rel="canonical" href="{url}">
<meta http-equiv="refresh" content="0; url={new}">
<script>location.replace({new!r} + location.hash.replace(/^#$/, ''))</script>
</head><body><p>This page has moved to <a href="{new}">{url}</a>.</p></body></html>
'''
    (pub / f'{old}.html').write_text(page, encoding='utf-8', newline='\n')
print('wrote', len(MAP), 'forwarding pages')
