"""Rebuilds the home page 'Where & when we train' section: two tabs (pre-season / in season),
each a short plain list. Edit the text below and run:  python tools/train_section.py public"""
import pathlib, sys

pub = pathlib.Path(sys.argv[1])
MAP = 'https://www.google.com/maps/search/?api=1&query='
CP = MAP + 'Robertson%20Road%20Fields%20Centennial%20Park%20NSW'
DPS = MAP + 'David%20Phillips%20Field%20Daceyville%20NSW'
HP = MAP + 'Henson%20Park%20Marrickville%20NSW'


def place(name, sub, url):
    return f'<a class="tp-place" href="{url}" target="_blank" rel="noopener"><b>{name}</b><span>{sub} · Map ↗</span></a>'


def tile(name, sub, used, img, url):
    """A map tile: one per ground, so a ground used for several things appears once."""
    return (f'<a class="tp-map" href="{url}" target="_blank" rel="noopener">'
            f'<img src="{img}" alt="Map of {name}, {sub}" loading="lazy" decoding="async">'
            f'<span class="tp-cap"><b>{name}</b><small>{sub} · {used}</small><i>Open in Maps ↗</i></span></a>')


PRE = f'''        <div class="tp-block">
          <h3>Mondays, 6:00-8:00pm</h3>
          <p>Everyone trains together. Walk-ins welcome, no registration needed. Bring boots and runners.</p>
        </div>
        <div class="tp-maps one">{tile('Robertson Road Fields', 'Centennial Park', 'pre-season', 'map-preseason.jpg', CP)}</div>'''

SEASON = f'''        <div class="tp-block">
          <h3>Training</h3>
          <dl>
            <dt>Tue &amp; Thu</dt><dd>SFL teams, 6:30-8:30pm</dd>
            <dt>Mon &amp; Wed</dt><dd>Divisions teams, times TBC</dd>
          </dl>
        </div>
        <div class="tp-block">
          <h3>Game day, Saturdays</h3>
          <dl>
            <dt>Henson Park</dt><dd>SFL teams and Men's Div 1</dd>
            <dt>David Phillips South</dt><dd>Men's Div 5 and Women's Div 2</dd>
            <dt>Either</dt><dd>Men's Div 3 splits its home games</dd>
          </dl>
          <a class="tp-prev" href="https://www.playhq.com/afl/org/afl-sydney/2026/85fe4ed2" target="_blank" rel="noopener">2027 times aren't out yet. Last season's fixture gives a rough idea ↗</a>
        </div>
        <div class="tp-maps">{tile('David Phillips South', 'Daceyville', 'training and game day', 'map-inseason.jpg', DPS)}{tile('Henson Park', 'Marrickville', 'game day', 'map-gameday.jpg', HP)}</div>'''

SECTION = f'''<!-- TRAIN (built by tools/train_section.py) -->
<section id="train" class="alt">
  <div class="wrap">
    <div class="shead">
      <div class="sr">Where &amp; when we train</div>
      <h2>One place to find the ground</h2>
    </div>
    <div class="week" data-tabs>
      <div class="wk-tabs" role="tablist" aria-label="Season stage"><button type="button" role="tab" id="tab-pre" aria-controls="wk-pre" aria-selected="true">Pre-season · on now</button><button type="button" role="tab" id="tab-season" aria-controls="wk-season" aria-selected="false">In season · from April</button></div>
      <div class="wk-panel tp pre" role="tabpanel" id="wk-pre" aria-labelledby="tab-pre">
{PRE}
      </div>
      <div class="wk-panel tp two" role="tabpanel" id="wk-season" aria-labelledby="tab-season" hidden>
{SEASON}
      </div>
    </div>
  </div>
</section>

'''
f = pub / 'index.html'
s = f.read_text(encoding='utf-8')
a = s.index('<!-- TRAIN')
b = s.index('<!-- TEAMS')
f.write_text(s[:a] + SECTION + s[b:], encoding='utf-8', newline='\n')
print('rebuilt train section')
