"""Swaps the footer's text social links for icon links on every page. Safe to re-run.
    python tools/footer_socials.py public"""
import pathlib, re, sys

pub = pathlib.Path(sys.argv[1])
IG = 'M12 2.2c3.2 0 3.6 0 4.9.07 1.2.06 1.8.25 2.2.42.6.2 1 .5 1.4 1 .5.4.8.8 1 1.4.2.4.4 1 .4 2.2.1 1.3.1 1.7.1 4.9s0 3.6-.1 4.9c0 1.2-.2 1.8-.4 2.2-.2.6-.5 1-1 1.4-.4.5-.8.8-1.4 1-.4.2-1 .4-2.2.4-1.3.1-1.7.1-4.9.1s-3.6 0-4.9-.1c-1.2 0-1.8-.2-2.2-.4-.6-.2-1-.5-1.4-1-.5-.4-.8-.8-1-1.4-.2-.4-.4-1-.4-2.2C2.2 15.6 2.2 15.2 2.2 12s0-3.6.1-4.9c0-1.2.2-1.8.4-2.2.2-.6.5-1 1-1.4.4-.5.8-.8 1.4-1 .4-.2 1-.4 2.2-.4C8.4 2.2 8.8 2.2 12 2.2zm0 1.8c-3.1 0-3.5 0-4.7.07-1.1.05-1.7.24-2.1.4-.5.2-.9.44-1.3.84-.4.4-.64.8-.84 1.3-.16.4-.35 1-.4 2.1C2.6 9.5 2.6 9.9 2.6 12s0 2.5.07 3.7c.05 1.1.24 1.7.4 2.1.2.5.44.9.84 1.3.4.4.8.64 1.3.84.4.16 1 .35 2.1.4 1.2.07 1.6.07 4.7.07s3.5 0 4.7-.07c1.1-.05 1.7-.24 2.1-.4.5-.2.9-.44 1.3-.84.4-.4.64-.8.84-1.3.16-.4.35-1 .4-2.1.07-1.2.07-1.6.07-3.7s0-2.5-.07-3.7c-.05-1.1-.24-1.7-.4-2.1-.2-.5-.44-.9-.84-1.3-.4-.4-.8-.64-1.3-.84-.4-.16-1-.35-2.1-.4C15.5 4 15.1 4 12 4zm0 3.1a4.9 4.9 0 110 9.8 4.9 4.9 0 010-9.8zm0 8.1a3.2 3.2 0 100-6.4 3.2 3.2 0 000 6.4zm6.2-8.3a1.15 1.15 0 11-2.3 0 1.15 1.15 0 012.3 0z'
FB = 'M22 12a10 10 0 10-11.6 9.9v-7H7.9V12h2.5V9.8c0-2.5 1.5-3.9 3.8-3.9 1.1 0 2.2.2 2.2.2v2.5h-1.2c-1.2 0-1.6.8-1.6 1.6V12h2.7l-.4 2.9h-2.3v7A10 10 0 0022 12z'
TT = 'M16.6 5.82A4.28 4.28 0 0 1 15.54 3h-3.09v12.4a2.59 2.59 0 1 1-2.59-2.59c.27 0 .53.04.77.12V9.77a5.7 5.7 0 0 0-.77-.05 5.68 5.68 0 1 0 5.68 5.68V9.04a7.33 7.33 0 0 0 4.28 1.37V7.32a4.28 4.28 0 0 1-3.22-1.5z'


def icon(href, label, path):
    return (f'<a href="{href}" target="_blank" rel="noopener" aria-label="{label}" title="{label}">'
            f'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="{path}"/></svg></a>')


NEW = ('<span class="fsoc">'
       + icon('https://instagram.com/unswesafl', 'Instagram', IG)
       + icon('https://facebook.com/unswesbulldogsafc', 'Facebook', FB)
       + icon('https://www.tiktok.com/@unswesafl', 'TikTok', TT)
       + '<span class="fhandle">@unswesafl</span></span>')

n = 0
for f in pub.rglob('*.html'):
    s = f.read_text(encoding='utf-8')
    s2 = re.sub(r'<span class="fsoc">.*?@unswesafl</span>(</span>)?', NEW, s, count=1, flags=re.S)
    if s2 != s:
        f.write_text(s2, encoding='utf-8', newline='\n'); n += 1
print('footer icons on', n, 'pages')
