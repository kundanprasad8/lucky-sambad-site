#!/usr/bin/env python3
"""Generate 15 hub hero images (1200x630) for luckysambad.in hubs."""
import os, math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1200, 630
OUT = os.path.expanduser("~/workspace/lottery-project/sitegen/assets/hubs/")
os.makedirs(OUT, exist_ok=True)

FB = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"

IMAGES = [
    ("Lottery Sambad Result Today", "home.jpg"),
    ("Dear Lottery Result Today", "dear-lottery-result.jpg"),
    ("Arunachal Pradesh Lottery Result", "arunachal-pradesh.jpg"),
    ("Assam Lottery Result", "assam.jpg"),
    ("Goa Lottery Result", "goa.jpg"),
    ("Kerala Lottery Result", "kerala.jpg"),
    ("Madhya Pradesh Lottery Result", "madhya-pradesh.jpg"),
    ("Maharashtra Lottery Result", "maharashtra.jpg"),
    ("Manipur Lottery Result", "manipur.jpg"),
    ("Meghalaya Lottery Result", "meghalaya.jpg"),
    ("Mizoram Lottery Result", "mizoram.jpg"),
    ("Nagaland Lottery Result", "nagaland.jpg"),
    ("Punjab Lottery Result", "punjab.jpg"),
    ("Sikkim Lottery Result", "sikkim.jpg"),
    ("West Bengal Lottery Result", "west-bengal.jpg"),
]

NAVY = (13, 22, 58)        # deep navy
PURPLE = (52, 28, 96)       # deep purple
GOLD = (245, 197, 66)
GOLD_LT = (255, 214, 120)
WHITE = (255, 255, 255)


def vgradient(w, h, top, bottom):
    """Vertical gradient image."""
    img = Image.new("RGB", (w, h), top)
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(h - 1, 1)
        c = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        d.line([(0, y), (w, y)], fill=c)
    return img


def radial_glow(w, h, cx, cy, radius, color, alpha=90):
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for r in range(radius, 0, -6):
        a = int(alpha * (1 - r / radius) ** 1.6)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color + (a,))
    return layer


def draw_ball(base, cx, cy, r, number, rng):
    """Glossy lottery ball with number."""
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    # shadow
    d.ellipse([cx - r + 6, cy - r + 10, cx + r + 6, cy + r + 10], fill=(0, 0, 0, 70))
    # ball body: white -> light grey radial
    ri = int(r)
    for rr in range(ri, 0, -2):
        t = rr / ri
        shade = int(235 - 60 * (1 - t))
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=(shade, shade, 245, 255))
    # gold ring for some balls
    if rng.random() < 0.35:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=GOLD + (255,), width=max(3, int(r // 12)))
    # gloss highlight
    hx, hy, hr = cx - r * 0.35, cy - r * 0.42, r * 0.28
    d.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], fill=(255, 255, 255, 170))
    # number
    fs = int(r * 0.95)
    f = ImageFont.truetype(FB, fs)
    txt = str(number)
    bb = d.textbbox((0, 0), txt, font=f)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    d.text((cx - tw / 2 - bb[0], cy - th / 2 - bb[1]), txt, font=f, fill=(30, 30, 60, 255))
    base.alpha_composite(layer)


def draw_ticket(base, cx, cy, w, h, angle, rng):
    """Golden ticket, tilted."""
    layer = Image.new("RGBA", (int(w * 1.6), int(h * 2.2)), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x0, y0 = (layer.width - w) / 2, (layer.height - h) / 2
    # shadow
    d.rounded_rectangle([x0 + 8, y0 + 12, x0 + w + 8, y0 + h + 12], radius=18, fill=(0, 0, 0, 80))
    # body
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=18, fill=GOLD + (255,))
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=18, outline=(160, 110, 20, 255), width=4)
    # perforation
    px = x0 + w * 0.68
    for yy in range(int(y0 + 14), int(y0 + h - 10), 16):
        d.line([(px, yy), (px, yy + 8)], fill=(120, 80, 10, 255), width=3)
    # side notches
    d.ellipse([x0 - 14, y0 + h / 2 - 16, x0 + 14, y0 + h / 2 + 16], fill=(0, 0, 0, 0))
    # star
    sx, sy, sr = x0 + w * 0.30, y0 + h / 2, h * 0.22
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = sr if i % 2 == 0 else sr * 0.45
        pts.append((sx + rr * math.cos(ang), sy + rr * math.sin(ang)))
    d.polygon(pts, fill=(255, 255, 255, 235))
    # "WIN" text on stub
    f = ImageFont.truetype(FB, int(h * 0.30))
    d.text((px + 18, y0 + h / 2 - int(h * 0.22)), "WIN", font=f, fill=(110, 70, 8, 255))
    layer = layer.rotate(angle, resample=Image.BICUBIC, expand=False)
    base.alpha_composite(layer, (int(cx - layer.width / 2), int(cy - layer.height / 2)))


def sparkle(d, x, y, r, color):
    d.line([(x - r, y), (x + r, y)], fill=color, width=2)
    d.line([(x, y - r), (x, y + r)], fill=color, width=2)


def make_image(headline, seed):
    rng = random.Random(seed)
    img = vgradient(W, H, NAVY, PURPLE).convert("RGBA")

    # soft glows
    img.alpha_composite(radial_glow(W, H, W // 2, H // 3, 420, (120, 80, 200), 70))
    img.alpha_composite(radial_glow(W, H, W * 0.12, H * 0.9, 300, (245, 197, 66), 40))
    img.alpha_composite(radial_glow(W, H, W * 0.9, H * 0.85, 300, (80, 140, 255), 40))

    # bokeh dots
    bok = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    db = ImageDraw.Draw(bok)
    for _ in range(46):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        r = rng.uniform(3, 16)
        col = rng.choice([(255, 255, 255), GOLD_LT, (170, 140, 255)])
        db.ellipse([x - r, y - r, x + r, y + r], fill=col + (rng.randint(18, 60),))
    bok = bok.filter(ImageFilter.GaussianBlur(1.2))
    img.alpha_composite(bok)

    # lottery balls along edges (keep center clear for headline)
    nums = rng.sample(range(1, 99), 12)
    spots = []
    for _ in range(7):
        side = rng.choice(["L", "R"])
        if side == "L":
            x = rng.uniform(40, 250)
        else:
            x = rng.uniform(W - 250, W - 40)
        y = rng.uniform(70, H - 70)
        r = rng.uniform(30, 62)
        spots.append((x, y, r))
    # a couple top/bottom too
    spots.append((rng.uniform(W * 0.3, W * 0.7), rng.uniform(30, 90), rng.uniform(24, 40)))
    spots.append((rng.uniform(W * 0.3, W * 0.7), rng.uniform(H - 110, H - 40), rng.uniform(24, 40)))
    for (x, y, r), n in zip(spots, nums):
        draw_ball(img, x, y, r, n, rng)

    # golden ticket, tilted, bottom-left
    draw_ticket(img, 170, H - 120, 300, 150, rng.uniform(-18, -8), rng)

    # sparkles
    d = ImageDraw.Draw(img)
    for _ in range(14):
        sparkle(d, rng.uniform(0, W), rng.uniform(0, H), rng.uniform(4, 10),
                (255, 215, 130, rng.randint(90, 160)))

    # vignette
    vig = Image.new("L", (W, H), 0)
    dv = ImageDraw.Draw(vig)
    dv.ellipse([-W * 0.25, -H * 0.35, W * 1.25, H * 1.35], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(120))
    black = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    img = Image.composite(img, black, vig.point(lambda v: int(255 - (255 - v) * 0.45)))

    d = ImageDraw.Draw(img)

    # gold accent bar above headline
    bar_w, bar_h = 120, 8
    d.rounded_rectangle([(W - bar_w) / 2, 218, (W + bar_w) / 2, 218 + bar_h],
                       radius=4, fill=GOLD + (255,))

    # headline, auto-fit
    fs = 92
    f = ImageFont.truetype(FB, fs)
    bb = d.textbbox((0, 0), headline, font=f)
    while bb[2] - bb[0] > 1020 and fs > 40:
        fs -= 4
        f = ImageFont.truetype(FB, fs)
        bb = d.textbbox((0, 0), headline, font=f)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    tx, ty = (W - tw) / 2 - bb[0], 250 - bb[1]
    # drop shadow
    d.text((tx + 3, ty + 4), headline, font=f, fill=(0, 0, 0, 160))
    d.text((tx, ty), headline, font=f, fill=WHITE + (255,))

    # sub-headline
    sub = "Winning Numbers  •  Prize Lists  •  Official PDFs"
    fs2 = 30
    f2 = ImageFont.truetype(FR, fs2)
    bb2 = d.textbbox((0, 0), sub, font=f2)
    tw2 = bb2[2] - bb2[0]
    d.text(((W - tw2) / 2, 250 + th + 28), sub, font=f2, fill=(220, 210, 245, 255))

    # corner brand
    brand = "LuckySambad.in"
    fb3 = ImageFont.truetype(FB, 30)
    bb3 = d.textbbox((0, 0), brand, font=fb3)
    tw3 = bb3[2] - bb3[0]
    d.text((W - tw3 - 36, H - 58), brand, font=fb3, fill=GOLD_LT + (255,))

    return img.convert("RGB")


def main():
    results = []
    for i, (headline, fname) in enumerate(IMAGES):
        try:
            img = make_image(headline, seed=20261018 + i * 77)
            path = os.path.join(OUT, fname)
            img.save(path, "JPEG", quality=88)
            size = os.path.getsize(path)
            ok = size > 0 and img.size == (W, H)
            results.append((fname, size, "OK" if ok else "BAD-SIZE"))
            print(f"{fname}: {size} bytes {'OK' if ok else 'FAIL'}")
        except Exception as e:
            results.append((fname, 0, f"ERROR: {e}"))
            print(f"{fname}: ERROR {e}")
    fails = [r for r in results if r[2] != "OK"]
    print(f"\nDone: {len(results) - len(fails)}/15 OK, {len(fails)} failed")
    return results


if __name__ == "__main__":
    main()
