"""Orders the AFL/AFLW player cards by career games at the top level (men and women together).
Home page: one ranked list split across two drifting rows (1st, 3rd, 5th... on top; 2nd, 4th... below).
AFL & AFLW Players page: the same order in the grid. Re-run after changing ORDER:
    python tools/players_rows.py public

ORDER is highest games first. Career games as checked in November 2026 (AFL Tables, club and Wikipedia
lists); numbers are not shown on the site, only the order. Update when a player passes another."""
import pathlib, re, sys

pub = pathlib.Path(sys.argv[1])
ORDER = [
    'Dane Rampe',        # 289
    'Nick Blakey',       # 173
    'Errol Gulden',      # 116
    'Jack Buckley',      # 94
    'Will Langford',     # 72
    'Rebecca Beeson',    # about 70 (AFLW)
    'Phoebe Monahan',    # 60 (AFLW)
    'Maddy Collier',     # 39 (AFLW)
    'Jacinda Barclay',   # 23 (AFLW)
    'Maddy Hendrie',     # 20+ (AFLW)
    'Harry Kyle',        # 12
    'Ben Davis',         # 11
    'Ellie Veerhuis',    # 11+ (AFLW)
    'Amaia Wain',        # 2026 debut season (AFLW)
    'Amelia Martin',     # 6+ (AFLW)
    'Jordan Foote',      # 6
    'Indhi Kirk',        # 0
    'Joel Cochran',      # 0
    'Noah Chamberlain',  # 0
]
NOTE = 'Ordered by career AFL and AFLW games played, highest first, as at November 2026.'


def cards_of(s):
    cards = re.findall(r'      <article class="pcard.*?</article>', s, flags=re.S)
    by = {re.search(r'data-name="([^"]+)"', c).group(1): c for c in cards}
    missing = [n for n in ORDER if n not in by] + [n for n in by if n not in ORDER]
    assert not missing, missing
    return [by[n] for n in ORDER]


# home page
f = pub / 'index.html'
s = f.read_text(encoding='utf-8')
a = s.index('<div class="prows">')
end = s.index('</section>', a)
inner_end = s.rindex('</div>\n  </div>\n', a, end)
ranked = cards_of(s[a:inner_end])
# home page keeps men on the top row and women on the bottom, each in games order
top = [c for c in ranked if 'data-tag="AFL"' in c]
bottom = [c for c in ranked if 'data-tag="AFL"' not in c]


def row(lst, cls, label, count):
    return f'''    <div class="prow">
      <div class="prow-h"><b>{label}</b><span>{count}</span><a href="about/afl-players.html">See all →</a></div>
      <div class="marquee {cls}"><div class="mtrack">
{chr(10).join(lst)}
      </div></div>
    </div>'''


new = ('<div class="prows">\n'
       + row(top, 'm', 'AFL', f'{len(top)} men') + '\n' + row(bottom, 'w', 'AFLW', f'{len(bottom)} women') + '\n    ')
s = s[:a] + new + s[inner_end:]
f.write_text(s, encoding='utf-8', newline='\n')

# AFL & AFLW players page grid
f = pub / 'about/afl-players.html'
s = f.read_text(encoding='utf-8')
a = s.index('<div class="pgrid">') + len('<div class="pgrid">')
b = s.index('\n    </div>', a)
ranked = cards_of(s[a:b])
s = s[:a] + '\n' + '\n'.join(ranked) + s[b:]
if NOTE not in s:
    s = s.replace('<div class="pgrid">', f'<p class="psort">{NOTE}</p>\n    <div class="pgrid">', 1)
f.write_text(s, encoding='utf-8', newline='\n')
print('ordered', len(ranked), 'players')
