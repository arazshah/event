"""24 s solemn, cinematic instrumental for the GIS Day reel (D minor, 120 bpm grid) -> music_gisday.wav.
Hits land on the scene changes of reel_gisday.html. Fully synthesised: no samples, no vocals."""
import wave
import numpy as np

SR = 44100
DUR = 24.0
N = int(SR * DUR)
t = np.arange(N) / SR
rng = np.random.default_rng(1405)
SCENES = [0, 3, 5, 7, 9, 11, 13, 15, 17, 20]

L = np.zeros((2, N))


def put(buf, start, sig, pan=0.0, gain=1.0):
    i = int(start * SR)
    if i >= N:
        return
    sig = sig[: N - i] * gain
    buf[0, i:i + len(sig)] += sig * (1 - pan) * 0.5 * 2
    buf[1, i:i + len(sig)] += sig * (1 + pan) * 0.5 * 2


def saw(f, n, det=1.0, harm=10, tilt=1.35):
    x = np.arange(n) / SR
    s = np.zeros(n)
    ph = rng.random() * 6
    for h in range(1, harm + 1):
        s += np.sin(2 * np.pi * f * det * h * x + ph * h) / h ** tilt
    return s


# chords: (start, length, bass, tones)
D2, D3, F3, A3, D4 = 73.42, 146.83, 174.61, 220.0, 293.66
CH = [
    (0, 4, D2, [D3, F3, A3, D4]),
    (4, 4, 116.54 / 2 * 2 / 2 * 2 / 2 * 2, [116.54, 146.83, 174.61, 233.08]),   # Bb
    (8, 4, 98.0, [98.0 * 2, 233.08, 293.66, 392.0]),                           # Gm
    (12, 5, 110.0, [220.0, 277.18, 329.63, 440.0]),                            # A
    (17, 3, D2, [D3, F3, A3, D4]),                                             # Dm (date)
    (20, 4, D2, [D3, F3, A3, D4, 349.23]),                                     # Dm final
]
CH[1] = (4, 4, 58.27, CH[1][3])

pad = np.zeros((2, N)); bass = np.zeros((2, N))
for st, ln, b, tones in CH:
    n = int(SR * (ln + 0.8)); x = np.arange(n) / SR
    env = np.minimum(1, x / 0.7) * np.clip((ln + 0.8 - x) / 0.8, 0, 1)
    for ch, det in ((0, 0.996), (1, 1.004)):
        sig = sum(saw(f, n, det) for f in tones) * env
        i = int(st * SR); seg = sig[: N - i]
        pad[ch, i:i + len(seg)] += seg * 0.045
    bs = (np.sin(2 * np.pi * b * x) + 0.35 * np.sin(2 * np.pi * 2 * b * x) + 0.12 * np.sin(2 * np.pi * 3 * b * x)) * env
    put(bass, st, bs, gain=0.22)

# low string ostinato (8ths) during the keyword scenes
ost = np.zeros((2, N))
for k in range(int((17 - 3) / 0.25)):
    tt = 3 + k * 0.25
    root = [c for c in CH if c[0] <= tt < c[0] + c[1]][0]
    f = root[3][0] if k % 2 == 0 else root[3][2] / 2
    n = int(SR * 0.22); x = np.arange(n) / SR
    s = saw(f, n, harm=8, tilt=1.2) * np.exp(-x * 18) * np.minimum(1, x / 0.004)
    put(ost, tt, s, pan=(-0.25 if k % 2 else 0.25), gain=0.09 * (0.6 + 0.4 * (k % 4 == 0)))

# bell motif, sparse
bells = np.zeros((2, N))
for st, ln, b, tones in CH[1:5]:
    for j, f in enumerate([tones[-1] * 2, tones[1] * 2, tones[2] * 2]):
        tt = st + 0.5 + j * 1.0
        n = int(SR * 2.2); x = np.arange(n) / SR
        s = (np.sin(2 * np.pi * f * x) + 0.4 * np.sin(2 * np.pi * f * 2.76 * x) * np.exp(-x * 4) + 0.2 * np.sin(2 * np.pi * f * 5.4 * x) * np.exp(-x * 7)) * np.exp(-x * 2.2) * np.minimum(1, x / 0.003)
        put(bells, tt, s, pan=(-0.4, 0.1, 0.4)[j], gain=0.045)


# timpani-like hits on scene changes
def timp(gain, dur=1.6):
    n = int(SR * dur); x = np.arange(n) / SR
    f = 52 + 38 * np.exp(-x * 9)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 2.6)
    skin = rng.standard_normal(n) * np.exp(-x * 40) * 0.35
    return (body + skin) * gain

hits = np.zeros((2, N))
for s in SCENES:
    g = 0.75 if s in (0, 17, 20) else 0.45
    put(hits, s, timp(g))
    if s in (17, 20):
        put(hits, s + 0.25, timp(0.35, 1.0))

# risers into the date and the closing card
for a, b0 in ((15.6, 17.0), (18.6, 20.0)):
    n = int((b0 - a) * SR); x = np.linspace(0, 1, n)
    z = np.convolve(rng.standard_normal(n), np.ones(6) / 6, mode="same") * x ** 3
    put(hits, a, z, gain=0.25)

# reverb: FFT convolution with a decaying noise impulse
def reverb(sig, secs=2.6, mix=0.32):
    n = int(SR * secs); x = np.arange(n) / SR
    ir = rng.standard_normal((2, n)) * np.exp(-x * 3.0)
    ir[:, : int(0.02 * SR)] *= np.linspace(0, 1, int(0.02 * SR))
    size = 1 << int(np.ceil(np.log2(N + n)))
    out = np.real(np.fft.ifft(np.fft.fft(sig, size) * np.fft.fft(ir, size)))[:, :N]
    out /= np.abs(out).max() + 1e-9
    return sig + out * mix * np.abs(sig).max()

wet = reverb(pad + bells + ost * 0.6)
mix = wet + bass + ost * 0.6 + reverb(hits, 1.8, 0.25)
fade = np.clip(t / 0.03, 0, 1) * np.clip((DUR - t) / 1.6, 0, 1)
mix *= fade
mix = np.tanh(mix * 1.4) / 1.4
mix = mix / np.abs(mix).max() * 0.89
with wave.open("music_gisday.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix.T * 32767).astype("<i2").tobytes())
print("ok")
