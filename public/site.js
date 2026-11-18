/* UNSW-ES Bulldogs: shared behaviour for every page.
   1. Colour palette (and the preview switcher bar)
   2. Mobile menu state for screen readers
   3. Keyboard access for the player cards */
(function () {
  var DEFAULT_THEME = 'tricolour';   // the palette visitors get
  var SHOW_SWITCHER = true;          // set to false once the club has picked a palette
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

  // Runs in <head>, before the page paints, so there is no flash of the wrong colours.
  // A link ending in ?palette=guernsey (or lights, heritage, original, tricolour) opens the site in that palette.
  var fromLink = (location.search.match(/[?&]palette=([a-z]+)/) || [])[1];
  if (fromLink && find(fromLink)) store(KEY, fromLink);
  var current = apply(SHOW_SWITCHER ? (store(KEY) || DEFAULT_THEME) : DEFAULT_THEME);

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

  function buildSwitcher() {
    var bar = el('div', 'themebar');
    bar.setAttribute('role', 'group');
    bar.setAttribute('aria-label', 'Preview a colour palette');
    var label = el('div', 'tb-l', 'Colour palette');
    label.appendChild(el('small', '', 'Tap one to preview'));
    var opts = el('div', 'tb-opts');
    var fab = el('button', 'themefab');
    fab.type = 'button';

    function paint() {
      [].forEach.call(opts.children, function (b) {
        b.setAttribute('aria-pressed', String(b.getAttribute('data-id') === current));
      });
      fab.textContent = '';
      fab.appendChild(swatch(find(current)));
      fab.appendChild(document.createTextNode('Colours'));
    }
    THEMES.forEach(function (t) {
      var b = el('button', 'tb-o');
      b.type = 'button';
      b.setAttribute('data-id', t.id);
      b.appendChild(swatch(t));
      b.appendChild(el('span', '', t.name));
      b.addEventListener('click', function () { current = apply(t.id); store(KEY, current); paint(); });
      opts.appendChild(b);
    });
    var close = el('button', 'tb-x', '×');
    close.type = 'button';
    close.setAttribute('aria-label', 'Hide the palette bar');

    function show(open) {
      bar.style.display = open ? '' : 'none';
      fab.style.display = open ? 'none' : '';
      document.body.classList.toggle('has-themebar', open);
      document.body.classList.toggle('has-themefab', !open);
      store(KEY + '-bar', open ? 'open' : 'closed');
    }
    close.addEventListener('click', function () { show(false); fab.focus(); });
    fab.addEventListener('click', function () { show(true); });

    bar.appendChild(label); bar.appendChild(opts); bar.appendChild(close);
    document.body.appendChild(bar); document.body.appendChild(fab);
    paint();
    show(store(KEY + '-bar') !== 'closed');
  }

  /* NEWS: blend in Play AFL articles about the club.
     Our own articles always win. Each club article gets a HEAD_START (21 days) added to its date
     when ranking, so a Play AFL story only gets ahead of ours if it is three weeks newer. At most
     MAX_PLAYAFL of the visible cards come from Play AFL, a Play AFL story that matches one of ours
     (similar headline) is dropped, and anything older than MAX_AGE days is ignored. If the feed
     can't be reached, the page keeps its own cards as written. */
  var NEWS = { SLOTS: 4, MAX_PLAYAFL: 2, HEAD_START: 21, MAX_AGE: 120 };
  function words(t) {
    return (t || '').toLowerCase().replace(/[^a-z0-9 ]/g, ' ').split(/\s+/).filter(function (w) {
      return w.length > 3 && ['with', 'from', 'into', '2026', '2027', 'unsw', 'bulldogs', 'club'].indexOf(w) < 0;
    });
  }
  function similar(a, b) {
    var A = words(a), B = words(b), hit = 0;
    A.forEach(function (w) { if (B.indexOf(w) >= 0) hit++; });
    return hit / Math.max(1, Math.min(A.length, B.length)) >= 0.5;
  }
  function fmtDate(iso) {
    var d = new Date(iso + 'T00:00:00Z');
    return d.getUTCDate() + ' ' + ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][d.getUTCMonth()] + ' ' + d.getUTCFullYear();
  }
  function playAflCard(it) {
    var a = el('article', 'ncard ext');
    a.innerHTML = '<div class="band"></div><div class="thumb"></div><div class="body"><div class="meta"><span class="pill">Play AFL</span><span class="date"></span></div><h3></h3><p></p><a class="more" target="_blank" rel="noopener">Read on Play AFL ↗</a></div>';
    if (it.image) {
      var img = el('img'); img.src = it.image; img.alt = ''; img.loading = 'lazy'; img.decoding = 'async';
      a.querySelector('.thumb').appendChild(img);
    }
    a.querySelector('.date').textContent = fmtDate(it.date);
    a.querySelector('h3').textContent = it.title;
    a.querySelector('p').textContent = it.summary;
    a.querySelector('.more').href = it.url;
    return a;
  }
  function blendNews() {
    var grid = document.querySelector('#news .news');
    if (!grid || !window.fetch) return;
    var DAY = 864e5, now = Date.now();
    fetch('/news.json', { cache: 'no-cache' }).then(function (r) { return r.ok ? r.json() : null; }).then(function (data) {
      if (!data || !data.items || !data.items.length) return;
      var ours = [].map.call(grid.querySelectorAll('.ncard[data-date]'), function (c) {
        var t = Date.parse(c.getAttribute('data-date'));
        return { el: c, title: c.querySelector('h3').textContent, source: c.getAttribute('data-source'), score: t + NEWS.HEAD_START * DAY, club: true };
      });
      var theirs = data.items.filter(function (it) {
        var t = Date.parse(it.date);
        return it.date && now - t < NEWS.MAX_AGE * DAY && !ours.some(function (o) { return o.source === it.url || similar(o.title, it.title); });
      }).map(function (it) { return { item: it, score: Date.parse(it.date), club: false }; });
      var all = ours.concat(theirs).sort(function (x, y) { return y.score - x.score; });
      var pick = [], ext = 0;
      all.forEach(function (c) {
        if (pick.length >= NEWS.SLOTS) return;
        if (!c.club && ext >= NEWS.MAX_PLAYAFL) return;
        if (!c.club) ext++;
        pick.push(c);
      });
      grid.textContent = '';
      pick.forEach(function (c) { grid.appendChild(c.club ? c.el : playAflCard(c.item)); });
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
    // News page: list Play AFL stories we haven't written up ourselves.
    var pl = document.getElementById('playafl-list');
    if (pl && window.fetch) {
      fetch('/news.json', { cache: 'no-cache' }).then(function (r) { return r.ok ? r.json() : null; }).then(function (d) {
        if (!d || !d.items) return;
        var have = [].map.call(document.querySelectorAll('.ncard'), function (c) {
          return { source: c.getAttribute('data-source'), title: (c.querySelector('h3') || {}).textContent };
        });
        var grid = pl.querySelector('.news'), n = 0;
        d.items.forEach(function (it) {
          if (have.some(function (h) { return h.source === it.url || similar(h.title, it.title); })) return;
          grid.appendChild(playAflCard(it)); n++;
        });
        if (n) pl.hidden = false;
      }).catch(function () {});
    }
    if (SHOW_SWITCHER) buildSwitcher();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', enhance); else enhance();
})();
