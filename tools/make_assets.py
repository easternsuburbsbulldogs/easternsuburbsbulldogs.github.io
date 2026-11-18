"""Builds crest.png (oval crest on transparent) and share.jpg (1200x630 social card) from the pack's own images."""
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont
pub = sys.argv[1]
icon = Image.open(pub + '/app-icon.png').convert('RGB')
bg = icon.getpixel((10, 10))
w, h = icon.size
xs, ys = [], []
px = icon.load()
for y in range(0, 300):
    for x in range(w):
        p = px[x, y]
        if sum(abs(p[i] - bg[i]) for i in range(3)) > 90:
            xs.append(x); ys.append(y)
box = (min(xs), min(ys), max(xs) + 1, max(ys) + 1)
print('crest bbox', box)
S = 4
crop = icon.crop(box).resize(((box[2]-box[0])*S, (box[3]-box[1])*S), Image.LANCZOS)
mask = Image.new('L', crop.size, 0)
ImageDraw.Draw(mask).ellipse((S, S, crop.size[0]-S-1, crop.size[1]-S-1), fill=255)
mask = mask.filter(ImageFilter.GaussianBlur(S*0.6))
crest = crop.convert('RGBA'); crest.putalpha(mask)
crest = crest.resize((box[2]-box[0], box[3]-box[1]), Image.LANCZOS)
crest.save(pub + '/crest.png', optimize=True)
print('crest', crest.size)

# share card
W, H = 1200, 630
NAVY = (24, 41, 106)
hero = Image.open(pub + '/hero2.jpg').convert('RGB')
card = Image.new('RGB', (W, H), NAVY)
ph = hero.resize((int(hero.width * (H / hero.height * 1.12)), int(H * 1.12)), Image.LANCZOS)
card.paste(ph, (W - ph.width + 60, -20))
grad = Image.new('L', (W, 1))
for x in range(W):
    t = (x - 430) / 300
    grad.putpixel((x, 0), int(255 * (1 - max(0, min(1, t)))))
card.paste(Image.new('RGB', (W, H), NAVY), (0, 0), grad.resize((W, H)))
d = ImageDraw.Draw(card)
d.rectangle((0, H - 10, W, H), fill=(200, 16, 46))
def font(names, size):
    for n in names:
        try: return ImageFont.truetype(n, size)
        except OSError: pass
    return ImageFont.load_default()
big = font(['impact.ttf', 'arialbd.ttf'], 74)
sm = font(['arialbd.ttf', 'arial.ttf'], 25)
serif = font(['georgiab.ttf', 'georgia.ttf'], 54)
c2 = crest.resize((int(crest.width * 0.62), int(crest.height * 0.62)), Image.LANCZOS)
card.paste(c2, (70, 62), c2)
d.text((70, 232), 'UNSW-ES', font=big, fill='white')
d.text((70, 314), 'BULLDOGS', font=big, fill='white')
d.rectangle((70, 418, 150, 423), fill=(200, 16, 46))
d.text((70, 446), 'EST. 1880', font=serif, fill='white')
d.text((70, 526), "SYDNEY'S OLDEST CLUB", font=sm, fill=(190, 206, 240))
card.save(pub + '/share.jpg', quality=84, optimize=True, progressive=True)
