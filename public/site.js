/* UNSW-ES Bulldogs: shared behaviour for every page.
   1. Colour palette: rotates daily, with a picker in the menu
   2. News blend, mobile menu state, keyboard access for the player cards */
(function () {
  var ROTATE = true;                 // a different palette each day; set to false to always use DEFAULT_THEME
  var DEFAULT_THEME = 'tricolour';   // used when ROTATE is false
  var NIGHT_THEMES = ['lights', 'heritage', 'original', 'tricolour']; // dark palettes used after dark, one per night; [] turns it off
  var NIGHT_FROM = 19, NIGHT_UNTIL = 6; // 7pm to 6am, visitor's local time
  var SHOW_SWITCHER = true;          // the palette picker in the menu; set to false to hide it
  var THEMES = [
    { id: 'tricolour', name: 'Tricolour',     sw: ['#18296A', '#C8102E', '#FFFFFF'] },
    { id: 'guernsey',  name: 'Home Guernsey', sw: ['#FFFFFF', '#C8102E', '#23519E'], bar: '#FFFFFF' },
    { id: 'lights',    name: 'Under Lights',  sw: ['#0A0E1A', '#E3263F', '#FFFFFF'] },
    { id: 'heritage',  name: 'Heritage 1880', sw: ['#101A44', '#B3152D', '#F1E9D8'] },
    { id: 'original',  name: 'Original',      sw: ['#0B1F3A', '#C8102E', '#E0A93E'] }
  ];
  var KEY = 'bulldogs-palette', root = document.documentElement;

  function store(k, v) {
    try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; }
  }
  function find(id) { for (var i = 0; i < THEMES.length; i++) if (THEMES[i].id === id) return THEMES[i]; return null; }
  function apply(id) {
    var t = find(id) || find(DEFAULT_THEME);
    root.setAttribute('data-theme', t.id);
    var m = document.querySelector('meta[name="theme-color"]');
    if (m) m.setAttribute('content', t.bar || t.sw[0]);
    return t.id;
  }

  // Today's palette: everyone sees the same one on the same day, and it moves on at midnight.
  var now = new Date();
  var today = now.getFullYear() + '-' + (now.getMonth() + 1) + '-' + now.getDate();
  var dayNumber = Math.floor((now.getTime() - now.getTimezoneOffset() * 60000) / 864e5);
  var daytime = ROTATE ? THEMES[dayNumber % THEMES.length].id : DEFAULT_THEME;
  function isNight(d) { var h = d.getHours(); return h >= NIGHT_FROM || h < NIGHT_UNTIL; }
  var nightly = NIGHT_THEMES.length ? NIGHT_THEMES[dayNumber % NIGHT_THEMES.length] : '';
  if (nightly === daytime && NIGHT_THEMES.length > 1) nightly = NIGHT_THEMES[(dayNumber + 1) % NIGHT_THEMES.length]; // always a visible change at 7pm
  var todays = nightly && isNight(now) ? nightly : daytime;

  // A visitor's own pick (from the menu, or a link ending in ?palette=lights) lasts for the rest of the day.
  function picked() {
    var v = (store(KEY) || '').split('|');
    return v[1] === today && find(v[0]) ? v[0] : null;
  }
  function pick(id) { store(KEY, id + '|' + today); }
  var fromLink = (location.search.match(/[?&]palette=([a-z]+)/) || [])[1];
  if (fromLink && find(fromLink)) pick(fromLink);
  // Runs in <head>, before the page paints, so there is no flash of the wrong colours.
  var current = apply((SHOW_SWITCHER && picked()) || todays);

  // If the page is left open across 7pm (or 6am), switch over without a reload, unless the visitor picked one.
  if (nightly) setInterval(function () {
    var want = isNight(new Date()) ? nightly : daytime;
    if (!(SHOW_SWITCHER && picked()) && want !== current) { current = apply(want); if (window.__palPaint) window.__palPaint(); }
  }, 60000);

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text) n.textContent = text;
    return n;
  }
  function swatch(t) {
    var s = el('span', 'tb-sw');
    t.sw.forEach(function (c) { var i = el('i'); i.style.background = c; s.appendChild(i); });
    return s;
  }

  // Palette picker: a "Colours" dropdown in the desktop menu and a section in the mobile menu.
  function buildSwitcher() {
    var groups = [];
    function options(cls) {
      var box = el('div', cls);
      box.setAttribute('role', 'group');
      box.setAttribute('aria-label', 'Colour palette');
      THEMES.forEach(function (t) {
        var b = el('button', 'pal-o');
        b.type = 'button';
        b.setAttribute('data-id', t.id);
        b.appendChild(swatch(t));
        b.appendChild(el('span', '', t.name + (t.id === daytime ? ' · today' : '') + (t.id === nightly && nightly !== daytime ? ' · tonight' : '')));
        b.addEventListener('click', function () { current = apply(t.id); pick(t.id); paint(); });
        box.appendChild(b);
      });
      groups.push(box);
      return box;
    }
    var btn;
    function paint() {
      groups.forEach(function (g) {
        [].forEach.call(g.children, function (b) {
          if (b.hasAttribute('data-id')) b.setAttribute('aria-pressed', String(b.getAttribute('data-id') === current));
        });
      });
      if (btn) { var old = btn.querySelector('.tb-sw'); btn.replaceChild(swatch(find(current)), old); }
    }
    window.__palPaint = paint;

    var links = document.querySelector('nav.links'), cta = links && links.querySelector('.navcta');
    if (links) {
      var dd = el('div', 'dd pal-dd');
      btn = el('button', 'ddb pal-btn');
      btn.type = 'button';
      btn.setAttribute('aria-haspopup', 'true');
      btn.setAttribute('aria-label', 'Colour palette');
      btn.appendChild(el('span', 'tb-sw'));
      var car = el('span', 'car'); car.setAttribute('aria-hidden', 'true'); btn.appendChild(car);
      var menu = el('div', 'ddm pal-menu');
      menu.appendChild(el('div', 'pal-h', 'Colour palette'));
      menu.appendChild(options('pal-list'));
      menu.appendChild(el('p', 'pal-note', 'Changes every day, with a darker palette from 7pm. Your pick lasts until tomorrow.'));
      dd.appendChild(btn); dd.appendChild(menu);
      links.insertBefore(dd, cta || null);
    }
    var mwrap = document.querySelector('#mnav .wrap'), mcta = mwrap && mwrap.querySelector('.navcta');
    if (mwrap) {
      mwrap.insertBefore(el('div', 'mh', 'Colour palette'), mcta || null);
      mwrap.insertBefore(options('pal-list pal-mobile'), mcta || null);
    }
    paint();
  }

  /* NEWS: the home page shows the newest club articles. Hand-written cards are in the page; stories brought in
     from Play AFL by the scheduled job (tools/playafl_articles.py) get their own club page and are listed in
     news.json. Everything is sorted by date and the newest NEWS_SLOTS are shown. If news.json can't be read,
     the page keeps its own cards as written. */
  var NEWS_SLOTS = 4;
  function fmtDate(iso) {
    var d = new Date(iso + 'T00:00:00Z');
    return d.getUTCDate() + ' ' + ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][d.getUTCMonth()] + ' ' + d.getUTCFullYear();
  }
  function storyCard(it) {
    var a = el('article', 'ncard navy');
    a.innerHTML = '<div class="band"></div><div class="thumb"></div><div class="body"><div class="meta"><span class="pill">Club news</span><span class="date"></span></div><h3></h3><p></p><a class="more">Read more →</a></div>';
    if (it.image) {
      var img = el('img'); img.src = it.image; img.alt = ''; img.loading = 'lazy'; img.decoding = 'async';
      a.querySelector('.thumb').appendChild(img);
    }
    a.querySelector('.pill').textContent = it.tag || 'Club news';
    a.querySelector('.date').textContent = fmtDate(it.date);
    var t = it.title === it.title.toUpperCase() ? it.title.toLowerCase().replace(/\b\w/g, function (c) { return c.toUpperCase(); }) : it.title;
    a.querySelector('h3').textContent = t;
    a.querySelector('p').textContent = it.summary;
    a.querySelector('.more').href = it.page;
    return a;
  }
  function blendNews() {
    var grid = document.querySelector('#news .news');
    if (!grid || !window.fetch) return;
    fetch('/news.json', { cache: 'no-cache' }).then(function (r) { return r.ok ? r.json() : null; }).then(function (data) {
      if (!data || !data.items) return;
      var ours = [].map.call(grid.querySelectorAll('.ncard[data-date]'), function (c) {
        var link = c.querySelector('a.more');
        return { el: c, date: c.getAttribute('data-date'), source: c.getAttribute('data-source'), page: link ? link.getAttribute('href').replace(/\.html$/, '') : '' };
      });
      var extra = data.items.filter(function (it) {
        return it.page && it.date && !ours.some(function (o) { return o.source === it.url || ('/' + o.page) === it.page || o.page === it.page; });
      }).map(function (it) { return { item: it, date: it.date }; });
      var all = ours.concat(extra).sort(function (x, y) { return y.date < x.date ? -1 : y.date > x.date ? 1 : 0; }).slice(0, NEWS_SLOTS);
      grid.textContent = '';
      all.forEach(function (c) { grid.appendChild(c.el || storyCard(c.item)); });
    }).catch(function () {});
  }

  function enhance() {
    apply(current); // the theme-color tag may not have existed yet when the first call ran
    var burger = document.querySelector('.burger'), mnav = document.getElementById('mnav');
    if (burger && mnav) {
      burger.setAttribute('aria-controls', 'mnav');
      burger.setAttribute('aria-expanded', 'false');
      burger.addEventListener('click', function () {
        burger.setAttribute('aria-expanded', String(mnav.style.display === 'block'));
      });
      mnav.addEventListener('click', function (e) {
        if (e.target.closest('a')) { mnav.style.display = 'none'; burger.setAttribute('aria-expanded', 'false'); }
      });
    }
    // Player cards open a pop-up on click; make them reachable and usable from the keyboard too.
    [].forEach.call(document.querySelectorAll('.pcard'), function (c) {
      c.setAttribute('tabindex', '0');
      c.setAttribute('role', 'button');
      c.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); c.click(); }
      });
    });
    var modal = document.getElementById('pmodal');
    if (modal) {
      modal.setAttribute('role', 'dialog');
      modal.setAttribute('aria-modal', 'true');
      modal.setAttribute('aria-labelledby', 'pm-name');
    }
    // Tabs (training week): buttons with role=tab switch their panels.
    [].forEach.call(document.querySelectorAll('[data-tabs]'), function (box) {
      var tabs = box.querySelectorAll('[role=tab]');
      [].forEach.call(tabs, function (t, i) {
        t.addEventListener('click', function () {
          [].forEach.call(tabs, function (o) {
            var on = o === t;
            o.setAttribute('aria-selected', String(on));
            o.tabIndex = on ? 0 : -1;
            document.getElementById(o.getAttribute('aria-controls')).hidden = !on;
          });
        });
        t.addEventListener('keydown', function (e) {
          var d = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;
          if (d) { var n = tabs[(i + d + tabs.length) % tabs.length]; n.click(); n.focus(); }
        });
        t.tabIndex = t.getAttribute('aria-selected') === 'true' ? 0 : -1;
      });
    });
    // Player rows: copy each row once so the drift loops without a gap. Copies are hidden from screen readers.
    [].forEach.call(document.querySelectorAll('.mtrack'), function (t) {
      var n = t.children.length;
      [].slice.call(t.children).forEach(function (c) {
        var d = c.cloneNode(true);
        d.setAttribute('aria-hidden', 'true');
        d.setAttribute('data-clone', '');
        d.tabIndex = -1;
        d.addEventListener('click', function () { c.click(); });
        t.appendChild(d);
      });
      t.style.setProperty('--dur', (n * 12) + 's');
    });
    blendNews();
    if (SHOW_SWITCHER) buildSwitcher();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', enhance); else enhance();
})();
