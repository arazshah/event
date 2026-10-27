"""Procedural 'satellite scene' for the teaser background: right half natural-colour imagery,
left half the same scene as an AI land-cover classification, split by a diagonal scan line."""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 2160, 2700
rng = np.random.default_rng(1405)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)


def fbm(beta, seed):
    r = np.random.default_rng(seed)
    kx = np.fft.fftfreq(W)[None, :]; ky = np.fft.fftfreq(H)[:, None]
    k = np.sqrt(kx ** 2 + ky ** 2); k[0, 0] = 1
    f = np.fft.fft2(r.standard_normal((H, W))) * k ** (-beta / 2)
    n = np.real(np.fft.ifft2(f))
    return (n - n.min()) / (n.max() - n.min())


h = fbm(3.7, 1) * 0.85 + fbm(2.7, 2) * 0.15
# Lake Urmia-like elongated basin on the right, with a city on its western plain
lake = np.exp(-(((xx - 1640) / 300) ** 2 + ((yy - 1250) / 760) ** 2))
h = h - lake * 0.55
plain = np.exp(-(((xx - 980) / 520) ** 2 + ((yy - 1350) / 600) ** 2))
h = h * (1 - 0.45 * plain) + 0.18 * plain
h = (h - h.min()) / (h.max() - h.min())

water = h < 0.30
salt = (h >= 0.30) & (h < 0.335)
mount = h > 0.70
city_mask = np.exp(-(((xx - 900) / 340) ** 2 + ((yy - 1300) / 280) ** 2)) + fbm(2.0, 5) * 0.35 > 0.72
city_mask &= ~water & ~salt

# rotated field parcels
a = np.deg2rad(18)
u = np.floor((xx * np.cos(a) - yy * np.sin(a)) / 64); v = np.floor((xx * np.sin(a) + yy * np.cos(a)) / 44)
cell = (np.sin(u * 12.9898 + v * 78.233) * 43758.5453) % 1
crop = (~water & ~salt & ~mount & ~city_mask & (h < 0.60))
veg = (~water & ~salt & ~mount & ~city_mask & (h >= 0.60))

# hillshade
gy, gx = np.gradient(h * 900)
shade = np.clip((-gx * 0.6 - gy * 0.8) / np.sqrt(gx ** 2 + gy ** 2 + 1) * 0.5 + 0.6, 0.2, 1.15)

nat = np.zeros((H, W, 3), np.float32)
depth = np.clip((0.30 - h) / 0.30, 0, 1)[..., None]
nat[water] = 0
nat += water[..., None] * ((1 - depth) * np.array([80, 160, 150]) + depth * np.array([30, 90, 110]))
nat += salt[..., None] * np.array([232, 228, 214])
fieldc = np.stack([150 + 60 * cell, 160 + 40 * cell, 90 + 30 * (1 - cell)], -1)
greenish = cell < 0.55
fieldc = np.where(greenish[..., None], np.stack([95 + 40 * cell, 135 + 40 * cell, 70 + 20 * cell], -1), fieldc)
nat += crop[..., None] * fieldc
nat += veg[..., None] * np.array([150, 140, 105])
nat += mount[..., None] * (np.array([165, 140, 115]) + (h[..., None] - 0.70) * 260)
blocks = ((np.floor(xx / 18) + np.floor(yy / 18)) % 3 == 0)
nat += city_mask[..., None] * np.where(blocks[..., None], [205, 195, 180], [170, 160, 150])
nat *= np.where(water[..., None], 1.0, shade[..., None])

cls = np.zeros((H, W, 3), np.float32)
pal = {"water": [43, 122, 154], "salt": [236, 234, 222], "crop": [233, 196, 106], "veg": [106, 153, 78],
       "mount": [127, 85, 57], "urban": [192, 80, 77]}
for m, c in ((water, "water"), (salt, "salt"), (crop & ~greenish, "crop"), (crop & greenish, "veg"),
             (veg, "veg"), (mount, "mount"), (city_mask, "urban")):
    cls[m] = pal[c]
cls *= np.where(water[..., None], 1.0, (0.85 + 0.15 * shade)[..., None])

# contour lines on the classified side
lev = np.floor(h * 22)
edge = (np.abs(np.diff(lev, axis=0, prepend=lev[:1])) + np.abs(np.diff(lev, axis=1, prepend=lev[:, :1]))) > 0
cls[edge & ~water] = cls[edge & ~water] * 0.55 + 255 * 0.45

# diagonal split (natural on the right, classification on the left)
split = xx > (W * 0.42 + (yy - H / 2) * 0.32)
img = np.where(split[..., None], nat, cls)
img = np.clip(img, 0, 255).astype(np.uint8)
im = Image.fromarray(img)

d = ImageDraw.Draw(im)
for pts, wdt in (([(0, 980), (500, 1150), (880, 1300), (1300, 1420), (2160, 1700)], 9),
                 ([(900, 0), (950, 700), (900, 1300), (760, 2000), (700, 2700)], 8),
                 ([(0, 1900), (600, 1750), (900, 1300)], 6)):
    d.line(pts, fill=(240, 236, 226), width=wdt, joint="curve")
# scan line along the split
x0 = W * 0.42 - (H / 2) * 0.32; x1 = W * 0.42 + (H / 2) * 0.32
glow = Image.new("L", (W, H), 0); gd = ImageDraw.Draw(glow); gd.line([(x0, 0), (x1, H)], fill=255, width=36)
glow = glow.filter(ImageFilter.GaussianBlur(22))
amber = Image.new("RGB", (W, H), (233, 166, 42))
im = Image.composite(amber, im, glow.point(lambda p: int(p * 0.75)))
ImageDraw.Draw(im).line([(x0, 0), (x1, H)], fill=(255, 236, 190), width=5)
im.save("../assets/bg-rs.jpg", quality=90)
im.resize((540, 675)).save("/tmp/bg_preview.jpg")
print("ok")
