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

const pages = await Promise.all(FEEDS.flatMap(feed => Array.from({ length: PAGES }, (_, i) =>
  fetch(feed + i, { headers: { accept: 'application/json', 'user-agent': 'unswes-bulldogs-website' } })
    .then(r => (r.ok ? r.json() : null)).catch(() => null))));

const seen = new Set();
const items = [];
for (const p of pages) {
  for (const n of (p && p.data && p.data.news) || []) {
    const url = 'https://play.afl' + (n.news_article_url || '');
    if (!n.news_article_url || seen.has(url) || !mentionsClub(n)) continue;
    seen.add(url);
    items.push({
      title: (n.news_tile_heading || '').trim(),
      summary: (n.news_summary || '').trim(),
      date: parseDate(n.news_date),
      url,
      image: /^https:\/\/play\.afl\//.test(n.news_article_image || '') ? n.news_article_image : null,
      source: 'Play AFL',
    });
  }
}

items.sort((a, b) => (b.date || '').localeCompare(a.date || ''));
writeFileSync(OUT, JSON.stringify({ updated: new Date().toISOString(), items }, null, 2) + '\n');
console.log(`wrote ${items.length} Play AFL stories to ${OUT}` + (pages.some(Boolean) ? '' : ' (feeds unreachable)'));
