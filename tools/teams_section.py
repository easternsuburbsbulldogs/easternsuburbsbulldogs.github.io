"""Rebuilds the home page 'Our teams' section: one card per team with its coach, grouped by competition.
Also fills the full team cards on the Men's, Women's and Youth pages (DETAILS at the bottom).
Edit GROUPS and DETAILS, then run:  python tools/teams_section.py public
Coach email: put the address in the last field. While it is None, the button emails the President."""
import pathlib, sys
from urllib.parse import quote

pub = pathlib.Path(sys.argv[1])
PRES = 'president@unswesbulldogs.com.au'
WILLO = 'https://play.afl/sites/default/files/2026-11/Tom%20Williamson_0.jpg'

# Assistant coaches: team -> list of (name, role, photo path in public/ or None, email or None).
# Example: "Men's Premier": [('Sam Example', 'Midfield coach', 'coaches/sam-example.jpg', None)],
ASSISTANTS = {
    "Men's Premier": [('Jake Brown', 'Assistant coach', 'coaches/jake-brown.jpg', None), ('Kieran Emery', 'Assistant coach', 'coaches/kieran-emery.jpg', None)],
    "Men's Division 1": [('Jared Anderson', 'Assistant coach', 'coaches/jared-anderson.jpg', None)],
}

# Director of Coaching: shown above the SFL teams on the home page and on the Men's and Women's pages.
DIRECTOR = ("Ryan O'Keefe", 'Director of Coaching · SFL program',
            "Two-time Swans premiership player and 2012 Norm Smith Medallist. Oversees coaching across our SFL teams.",
            'https://play.afl/sites/default/files/2026-10/Ryan%20O%27Keefe%20appointment.png', 'news/ryan-okeefe-director-of-coaching.html')


def director_strip(prefix=''):
    name, role, blurb, photo, link = DIRECTOR
    return (f'<div class="dirstrip"><span class="ds-av"><img src="{photo}" alt="{name}" loading="lazy" decoding="async"></span>'
            f'<span class="ds-who"><small>{role}</small><b>{name}</b><span>{blurb}</span></span>'
            f'<a class="ds-link" href="{prefix}{link}">Read more →</a></div>')


GROUPS = [
    ('SFL', 'SFL · Sydney Football League', 'Home games at Henson Park, Marrickville', [
        # team, page, note, women?, coach, coach role, photo, coach email
        ("Men's Premier", 'football/mens.html', 'Flagship side', False, 'Jordan “Jordy” Doering', 'Head Coach', 'jordan.jpg', None),
        ("Women's Premier", 'football/womens.html', 'Flagship side', True, 'Tom “Willo” Williamson', 'Head Coach', WILLO, None),
        ("Men's Under 19.5", 'football/youth-juniors.html', 'Pathway to seniors', False, 'Steven Chichester', 'Head Coach', 'coaches/steven-chichester.jpg', None),
        ("Women's Under 20", 'football/youth-juniors.html', '2026 premiers', True, 'Jamie Grant', 'Head Coach', 'coaches/jamie-grant.jpg', None),
    ]),
    ('Divisional', 'AFL Sydney Divisions', 'Home games at David Phillips South, except Division 1 (Henson Park) and some Division 3 games', [
        ("Men's Division 1", 'football/mens.html', 'Reserves · plays at Henson Park', False, 'Paul “Lovey” Love', 'Coach', 'coaches/paul-love.jpg', None),
        ("Men's Division 3", 'football/mens.html', '2026 premiers · plays at both grounds', False, 'Alexander “Dawsey” Dawes', 'Coach', 'coaches/alex-dawes.jpg', None),
        ("Men's Division 5", 'football/mens.html', 'Beginners welcome', False, None, None, None, None),
        ("Women's Division 2", 'football/womens.html', 'Beginners welcome', True, None, None, None, None),
    ]),
]


def slug(team):
    return 't-' + '-'.join(''.join(c if c.isalnum() else ' ' for c in team.lower().replace("'", '')).split())


def initials(name):
    import re
    parts = re.sub(r'“[^”]*”', '', name).split()
    return (parts[0][0] + parts[-1][0]).upper() if len(parts) > 1 else parts[0][0].upper()


out = []
for short, comp, ground, teams in GROUPS:
    out.append(f'''    <div class="tgroup">
      <div class="tg-head"><b>{comp}</b><span>{ground}</span></div>{director_strip() if short == 'SFL' else ''}
      <div class="tgrid">''')
    for team, page, note, w, coach, role, photo, email in teams:
        if coach:
            # a local photo is used only once the file is in public/; until then the card shows initials
            has = photo and (photo.startswith('http') or (pub / photo).exists())
            av = f'<img src="{photo}" alt="" loading="lazy" decoding="async">' if has else f'<span>{initials(coach)}</span>'
            who = f'<b>{coach}</b><small>{role}</small>'
            n_asst = len(ASSISTANTS.get(team, []))
            if n_asst:
                who += f'<a class="tc-asst" href="{page}#{slug(team)}-assistants">+ {n_asst} assistant{"s" if n_asst > 1 else ""}</a>'
        else:
            av = '<span class="q">?</span>'
            who = '<b class="tba">Coach to be announced</b><small>Contact the club</small>'
        href = f'mailto:{email}' if email else f'mailto:{PRES}?subject=' + quote(f'Message for the {team} coach')
        page = page + '#' + slug(team)  # "Team details" jumps to the team's full card
        out.append(f'''        <article class="tcard{' w' if w else ''}">
          <a class="tc-top" href="{page}"><h4>{team}</h4><span>{note}</span></a>
          <div class="tc-coach"><div class="tc-av">{av}</div><div class="tc-who">{who}</div></div>
          <div class="tc-act"><a href="{page}">Team details →</a><a href="{href}">Contact coach →</a></div>
        </article>''')
    out.append('      </div>\n    </div>')

SECTION = f'''<!-- TEAMS (built by tools/teams_section.py) -->
<section id="teams">
  <div class="wrap">
    <div class="shead">
      <div class="sr">Our teams &amp; coaches</div>
      <h2>Teams and coaches</h2>
      <p>Find your team, see who coaches it and get in touch. Training times for each team will be confirmed before the season.</p>
    </div>
    <a id="coaches"></a>
{chr(10).join(out)}
  </div>
</section>

'''
f = pub / 'index.html'
s = f.read_text(encoding='utf-8')
a = s.index('<!-- TEAMS')
b = s.index('<!-- FOOTBALL')
f.write_text(s[:a] + SECTION + s[b:], encoding='utf-8', newline='\n')
print('rebuilt teams section')

# ---------------------------------------------------------------------------------------------
# FULL TEAM CARDS on the football pages. "Team details" on the home page jumps to these.
SFL_TRAIN = 'Tuesdays &amp; Thursdays, 6:30-8:30pm, David Phillips South'
DIV_TRAIN = 'Mondays &amp; Wednesdays, times TBC, David Phillips South'
HENSON = 'Henson Park, Marrickville'
DPS = 'David Phillips South Field, Daceyville'
DETAILS = {
    # team: (about, standard, training, home games, coach bio or None)
    "Men's Premier": ("Our flagship men's side, in the first season of the Sydney Football League.",
                      "The top level of senior men's football in NSW. Selection is competitive and starts at pre-season.",
                      SFL_TRAIN, HENSON,
                      "Former Carlton player and two-time VFL club champion. Coaching since 2007, including two seasons as senior coach of Ainslie in Canberra. <a href=\"../news/jordan-doering-head-coach.html\">Read Jordy's story →</a>"),
    "Women's Premier": ("Our flagship women's side, in the first season of the Sydney Football League.",
                        "The top level of senior women's football in NSW.",
                        SFL_TRAIN, HENSON,
                        "Starts his sixth season in charge in 2027. In 2026 the side finished third on the Women's Premier Division ladder, winning 13 of 16 games."),
    "Men's Under 19.5": ("The step from junior footy into senior football, playing alongside our senior squads.",
                         "Under-age football in the SFL, against the best young players from the other foundation clubs.",
                         SFL_TRAIN, HENSON, None),
    "Women's Under 20": ("2026 premiers, and the pathway into senior women's football.",
                         "Under-age football in the SFL, against the best young players from the other foundation clubs.",
                         SFL_TRAIN, HENSON, "Coached the Under 20s to the 2026 premiership."),
    "Men's Division 1": ("Our reserves side and the next step up to the Premier team.",
                         "Strong senior football. Players here are pushing for Premier selection.",
                         DIV_TRAIN, HENSON, "Coached Division 3 to premierships in 2026 and 2024 (2024 alongside Josh Tighe)."),
    "Men's Division 3": ("2026 premiers. Senior football for players who want a real contest.",
                         "Mid-level senior football in the AFL Sydney Divisions.",
                         DIV_TRAIN, 'Split between ' + HENSON + ' and ' + DPS, None),
    "Men's Division 5": ("New to footy or coming back after a break? Start here.",
                         "Entry-level senior football. No experience needed, and new players get playing gear.",
                         DIV_TRAIN, DPS, None),
    "Women's Division 2": ("Never played before? This is the team to start in.",
                           "Entry-level senior women's football. No experience needed.",
                           DIV_TRAIN, DPS, None),
}
PAGES = {
    'football/mens.html': ("Our 2027 men's teams", ["Men's Premier", "Men's Division 1", "Men's Division 3", "Men's Division 5", "Men's Under 19.5"]),
    'football/womens.html': ("Our 2027 women's teams", ["Women's Premier", "Women's Division 2", "Women's Under 20"]),
    'football/youth-juniors.html': ('UNSW-ES Talent Pathway teams', ["Men's Under 19.5", "Women's Under 20"]),
}
INFO = {t[0]: t for _, comp, _, teams in GROUPS for t in teams}
COMP = {t[0]: comp for _, comp, _, teams in GROUPS for t in teams}


def full_card(team):
    _, _, note, w, coach, role, photo, email = INFO[team]
    about, standard, train, home, bio = DETAILS[team]
    href = f'mailto:{email}' if email else f'mailto:{PRES}?subject=' + quote(f'Message for the {team} coach')
    if coach:
        has = photo and (photo.startswith('http') or (pub / photo).exists())
        src = photo if (photo or '').startswith('http') else '../' + (photo or '')
        av = f'<img src="{src}" alt="{coach}" loading="lazy" decoding="async">' if has else f'<span>{initials(coach)}</span>'
        who = f'<b>{coach}</b><small>{role}</small>' + (f'<p>{bio}</p>' if bio else '')
    else:
        av, who = '<span class="q">?</span>', '<b class="tba">Coach to be announced</b><small>Ask the club in the meantime</small>'
    asst = ASSISTANTS.get(team, [])
    if asst:
        rows = []
        for n, r, ph, em in asst:
            ok = ph and (pub / ph).exists()
            a_av = f'<img src="../{ph}" alt="" loading="lazy" decoding="async">' if ok else f'<span>{initials(n)}</span>'
            a_name = f'<a href="mailto:{em}">{n}</a>' if em else n
            rows.append(f'<li><span class="ta-av">{a_av}</span><span class="ta-who"><b>{a_name}</b><small>{r}</small></span></li>')
        asst_html = f'<div class="tf-asst" id="{slug(team)}-assistants"><h4>Assistant coaches</h4><ul>{"".join(rows)}</ul></div>'
    else:
        asst_html = '<div class="tf-asst none"><h4>Assistant coaches</h4><p>To be announced</p></div>'
    return f'''  <article class="tfull{' w' if w else ''}" id="{slug(team)}">
    <div class="tf-coach"><div class="tf-av">{av}</div><div class="tf-who">{who}<a class="tf-mail" href="{href}">Contact the coach →</a></div>{asst_html}</div>
    <div class="tf-body"><span class="tag">{COMP[team]}</span><h3>{team}</h3><p>{about}</p>
      <dl><dt>Training</dt><dd>{train}</dd><dt>Home games</dt><dd>{home}</dd><dt>Standard</dt><dd>{standard}</dd></dl></div>
  </article>'''


for page, (heading, teams) in PAGES.items():
    f = pub / page
    s = f.read_text(encoding='utf-8')
    h = s.index(f'<h2>{heading}</h2>') + len(f'<h2>{heading}</h2>')
    a = s.index('<div class="', h)
    if s.startswith('<div class="dirstrip">', a):  # drop the strip from a previous run
        a2 = s.index('\n', a) + 1
        s = s[:a] + s[a2:]
    b = s.index('\n</div>', a) + len('\n</div>')
    lead = director_strip('../') + '\n' if page in ('football/mens.html', 'football/womens.html') else ''
    s = s[:a] + lead + '<div class="tfulls">\n' + '\n'.join(full_card(t) for t in teams) + '\n</div>' + s[b:]
    s = s.replace("Team-by-team training times and coaches will be posted on this page as soon as they're confirmed. Until then, everyone is welcome at pre-season.",
                  "Training times marked TBC will be confirmed in March 2027. Until then, everyone is welcome at pre-season.")
    f.write_text(s, encoding='utf-8', newline='\n')
print('rebuilt team cards on football pages')
