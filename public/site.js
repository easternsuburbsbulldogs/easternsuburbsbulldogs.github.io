/* UNSW-ES Bulldogs: shared behaviour for every page.
   1. Colour palette: rotates daily, with a picker in the menu
   2. News blend, mobile menu state, keyboard access for the player cards */
(function () {
  var ROTATE = true;                 // a different palette each day; set to false to always use DEFAULT_THEME
  var DEFAULT_THEME = 'tricolour';   // used when ROTATE is false
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
  var todays = ROTATE ? THEMES[dayNumber % THEMES.length].id : DEFAULT_THEME;

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
        b.appendChild(el('span', '', t.name + (t.id === todays ? ' · today' : '')));
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
      menu.appendChild(el('p', 'pal-note', 'Changes every day. Your pick lasts until tomorrow.'));
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
