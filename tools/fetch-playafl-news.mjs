// Fetches AFL Sydney / SFL news from Play AFL, keeps the stories that mention the club,
// and writes them to a JSON file the website reads (public/news.json).
// Runs automatically every hour in GitHub Actions (.github/workflows/publish.yml).
// Run by hand with:  node tools/fetch-playafl-news.mjs public/news.json
import { writeFileSync } from 'node:fs';

const OUT = process.argv[2] || 'public/news.json';
const FEED = 'https://play.afl/news/search?tags=734%2C415&page=';
const PAGES = 3; // about 30 recent stories

// Match the club, but not "Western Bulldogs" on its own.
const KEYWORDS = /\b(unsw[- ]?es|unsw|eastern suburbs|east sydney|bulldogs)\b/i;
const NOT_US = /\bwestern bulldogs\b/gi;
const MONTHS = { january: 0, february: 1, march: 2, april: 3, may: 4, june: 5, july: 6, august: 7, september: 8, october: 9, november: 10, december: 11 };

function parseDate(s) {
  // "Tuesday 10 November 2026, 03:03 am"
  const m = /(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})/.exec(s || '');
  if (!m || !(m[2].toLowerCase() in MONTHS)) return null;
  return new Date(Date.UTC(+m[3], MONTHS[m[2].toLowerCase()], +m[1])).toISOString().slice(0, 10);
}

const mentionsClub = n => KEYWORDS.test(`${n.news_tile_heading || ''} ${n.news_summary || ''}`.replace(NOT_US, ''));

const pages = await Promise.all(Array.from({ length: PAGES }, (_, i) =>
  fetch(FEED + i, { headers: { accept: 'application/json', 'user-agent': 'unswes-bulldogs-website' } })
    .then(r => (r.ok ? r.json() : null)).catch(() => null)));

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

writeFileSync(OUT, JSON.stringify({ updated: new Date().toISOString(), items }, null, 2) + '\n');
console.log(`wrote ${items.length} Play AFL stories to ${OUT}` + (pages.some(Boolean) ? '' : ' (feed unreachable)'));
