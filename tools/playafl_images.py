"""Runs after fetch-playafl-news.mjs in the hourly GitHub Action: downloads each Play AFL story's image,
saves a small WebP copy in public/playafl/, and points news.json at it, so visitors never load the
full-size originals from play.afl. If an image can't be fetched, the story simply shows without one.
    python tools/playafl_images.py public/news.json public/playafl"""
import hashlib, io, json, pathlib, sys, urllib.request
from PIL import Image

news_file = pathlib.Path(sys.argv[1])
out_dir = pathlib.Path(sys.argv[2])
out_dir.mkdir(parents=True, exist_ok=True)
WIDTH = 800  # news cards are at most ~400px wide, so 2x for sharp screens

data = json.loads(news_file.read_text(encoding='utf-8'))
done = 0
for item in data.get('items', []):
    url = item.get('image')
    if not url or not url.startswith('https://play.afl/'):
        item['image'] = None
        continue
    name = hashlib.sha1(url.encode()).hexdigest()[:12] + '.webp'
    dest = out_dir / name
    if not dest.exists():
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'unswes-bulldogs-website'})
            raw = urllib.request.urlopen(req, timeout=30).read()
            im = Image.open(io.BytesIO(raw))
            im = im.convert('RGBA' if im.mode in ('RGBA', 'LA', 'P') else 'RGB')
            if im.width > WIDTH:
                im = im.resize((WIDTH, round(im.height * WIDTH / im.width)), Image.LANCZOS)
            im.save(dest, 'WEBP', quality=78, method=6)
        except Exception as e:  # keep the story, drop the picture
            print('image skipped:', url, e)
            item['image'] = None
            continue
    item['image'] = '/' + dest.relative_to(news_file.parent).as_posix()
    done += 1

news_file.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print(f'{done} Play AFL images ready in {out_dir}')
