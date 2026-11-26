// Fetches news from Play AFL, keeps the stories that mention the club or its grounds,
// and writes them to a JSON file the website reads (public/news.json).
// Runs on a schedule in GitHub Actions (.github/workflows/publish.yml).
// Run by hand with:  node tools/fetch-playafl-news.mjs public/news.json
import { writeFileSync } from 'node:fs';

const OUT = process.argv[2] || 'public/news.json';

// Play AFL files stories in different places, and no single feed has them all:
//   - the AFL Sydney / SFL tag feed has club stories (e.g. coaching appointments),
//   - the NSW/ACT feed (play.afl/article/nswact) has local stories such as Henson Park fixtures,
//   - the unfiltered feed catches anything else. All three are read and merged.
const FEEDS = [
  'https://play.afl/news/search?tags=734%2C415&page=',
  'https://play.afl/news/search?programme=nswact&page=',
  'https://play.afl/news/search?page=',
];
const PAGES = 3; // per feed, about 30 recent stories each

// Words that mean the story is about us wherever it appears...
const STRONG = /\b(unsw[- ]?es|unsw|eastern suburbs|east sydney|henson park)\b/i;
// ...and "Bulldogs" on its own, which only counts for NSW/ACT stories: nationally it usually means the Western Bulldogs.
const BULLDOGS = /\bbulldogs\b/i;
const NOT_US = /\bwestern bulldogs\b/gi;
const MONTHS = { january: 0, february: 1, march: 2, april: 3, may: 4, june: 5, july: 6, august: 7, september: 8, october: 9, november: 10, december: 11 };

function parseDate(s) {
  // "Tuesday 10 November 2026, 03:03 am"
  const m = /(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})/.exec(s || '');
  if (!m || !(m[2].toLowerCase() in MONTHS)) return null;
  return new Date(Date.UTC(+m[3], MONTHS[m[2].toLowerCase()], +m[1])).toISOString().slice(0, 10);
}

function mentionsClub(n) {
  const text = `${n.news_tile_heading || ''} ${n.news_summary || ''}`.replace(NOT_US, '');
  return STRONG.test(text) || (BULLDOGS.test(text) && (n.news_article_url || '').includes('/nswact/'));
}

// In full article text, a club name sitting in a list of other clubs ("Sydney University, UNSW Eastern
// Suburbs Bulldogs, UTS Bats, ...") is just the SFL line-up, not a story about us. A mention only counts if
// fewer than two other club names sit right around it. Henson Park mentions always count.
const OTHER_CLUBS = /Sydney University|UTS|St\.? George|Pennant Hills|North Shore|Manly|East Coast|Eagles|Giants|GIANTS|Inner West|Wests|West Sydney|Blues|Dragons|Bats|Demons|Wolves|Southern Power|Magpies|Swans Academy/g;
function realMention(text) {
  if (/\bhenson park\b/i.test(text)) return true;
  const re = new RegExp(`${STRONG.source}|${BULLDOGS.source}`, 'gi');
  for (const m of text.matchAll(re)) {
    const around = text.slice(Math.max(0, m.index - 90), m.index + m[0].length + 90);
    if ((around.match(OTHER_CLUBS) || []).length < 2) return true;
  }
  return false;
}

// The feed only has a headline and a one-line summary, so NSW/ACT stories that didn't match are opened and
// their full text checked too (e.g. a fixture or match report that names UNSW-ES further down).
async function bodyMentionsClub(path) {
  try {
    const r = await fetch('https://play.afl' + path, { headers: { accept: 'text/html', 'user-agent': 'unswes-bulldogs-website' } });
    if (!r.ok) return false;
    let html = await r.text();
    const main = html.match(/<main[\s\S]*?<\/main>/i);          // the article itself, not menus or footers
    const text = (main ? main[0] : html).replace(/<script[\s\S]*?<\/script>|<style[\s\S]*?<\/style>/gi, ' ')
      .replace(/<[^>]+>/g, ' ').replace(/&[a-z#0-9]+;/gi, ' ').replace(NOT_US, '');
    return realMention(text) ? text : false;
  } catch { return false; }
}

const pages = await Promise.all(FEEDS.flatMap(feed => Array.from({ length: PAGES }, (_, i) =>
  fetch(feed + i, { headers: { accept: 'application/json', 'user-agent': 'unswes-bulldogs-website' } })
    .then(r => (r.ok ? r.json() : null)).catch(() => null))));

const seen = new Set();
const all = [];
for (const p of pages) {
  for (const n of (p && p.data && p.data.news) || []) {
    const url = 'https://play.afl' + (n.news_article_url || '');
    if (!n.news_article_url || seen.has(url)) continue;
    seen.add(url);
    all.push(n);
  }
}
// headline/summary first; then the full text of NSW/ACT stories, a few at a time
const keep = new Set(all.filter(mentionsClub));
const bodyText = new Map();
const toCheck = all.filter(n => !keep.has(n) && (n.news_article_url || '').includes('/nswact/'));
for (let i = 0; i < toCheck.length; i += 5) {
  const batch = toCheck.slice(i, i + 5);
  const hits = await Promise.all(batch.map(n => bodyMentionsClub(n.news_article_url)));
  batch.forEach((n, j) => { if (hits[j]) { keep.add(n); bodyText.set(n, hits[j]); } });
}
const CLUB = /\b(unsw[- ]?es|unsw|eastern suburbs|east sydney|bulldogs)\b/i;
function tagFor(n) {
  const text = (bodyText.get(n) || `${n.news_tile_heading || ''} ${n.news_summary || ''}`).replace(NOT_US, '');
  return /\bhenson park\b/i.test(text) && !CLUB.test(text) ? 'Henson' : 'Club news';
}
const items = [];
for (const n of all) {
  {
    if (!keep.has(n)) continue;
    const url = 'https://play.afl' + n.news_article_url;
    items.push({
      title: (n.news_tile_heading || '').trim(),
      summary: (n.news_summary || '').trim(),
      date: parseDate(n.news_date),
      url,
      image: /^https:\/\/play\.afl\//.test(n.news_article_image || '') ? n.news_article_image : null,
      source: 'Play AFL',
      tag: tagFor(n),
    });
  }
}

items.sort((a, b) => (b.date || '').localeCompare(a.date || ''));
// every story looked at this run, so pages made earlier for stories that no longer qualify can be removed
const checked = all.map(n => 'https://play.afl' + n.news_article_url);
writeFileSync(OUT, JSON.stringify({ updated: new Date().toISOString(), items, checked }, null, 2) + '\n');
console.log(`checked ${all.length} stories (${toCheck.length} full texts); wrote ${items.length} to ${OUT}` + (pages.some(Boolean) ? '' : ' (feeds unreachable)'));
