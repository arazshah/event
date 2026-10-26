"""Synthesise a 12 s, 120 bpm instrumental (Am-F-C-G x1.5) -> music.wav. No samples, no vocals."""
import wave
import numpy as np

SR = 44100
DUR = 12.0
N = int(SR * DUR)
t = np.arange(N) / SR
rng = np.random.default_rng(7)
BEAT = 0.5


def env(n, a, d):  # attack/exp-decay envelope of n samples
    x = np.arange(n) / SR
    return np.minimum(1, x / a) * np.exp(-x / d)


def add(buf, start, sig, pan=0.0, gain=1.0):
    i = int(start * SR)
    if i >= N:
        return
    sig = sig[: N - i]
    buf[0, i:i + len(sig)] += sig * gain * (1 - pan)
    buf[1, i:i + len(sig)] += sig * gain * (1 + pan)


def pluck(f, dur=0.45, bell=False):
    n = int(SR * dur)
    x = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * x) + 0.35 * np.sin(2 * np.pi * 2 * f * x) * np.exp(-x * 9)
    if bell:
        s += 0.25 * np.sin(2 * np.pi * 3.01 * f * x) * np.exp(-x * 14)
    return s * env(n, 0.003, dur / 4)


chords = [  # (bass, [chord tones])
    (110.00, [220.00, 261.63, 329.63]),   # Am
    (87.31, [174.61, 220.00, 261.63]),    # F
    (130.81, [261.63, 329.63, 392.00]),   # C
    (98.00, [196.00, 246.94, 293.66]),    # G
]
pad = np.zeros((2, N)); arp = np.zeros((2, N)); bass = np.zeros((2, N)); drums = np.zeros((2, N)); duck = np.ones(N)

# pad: stacked detuned partials per bar, crossfaded
for bar in range(6):
    _, tones = chords[bar % 4]
    s0 = bar * 2.0
    n = int(SR * 2.4)
    x = np.arange(n) / SR
    for ch, det in ((0, 0.997), (1, 1.003)):
        sig = np.zeros(n)
        for f in tones:
            for h, w in ((1, 1), (2, .5), (3, .25), (4, .12)):
                sig += w * np.sin(2 * np.pi * f * det * h * x + rng.random() * 6)
        e = np.minimum(1, x / 0.5) * np.clip((2.4 - x) / 0.5, 0, 1)
        i = int(s0 * SR)
        seg = (sig * e)[: N - i]
        pad[ch, i:i + len(seg)] += seg * 0.035

# arpeggio, 8ths with a dotted echo added later
for bar in range(6):
    r, tones = chords[bar % 4]
    notes = [tones[0], tones[1], tones[2], tones[0] * 2, tones[1] * 2, tones[0] * 2, tones[2], tones[1]]
    for k, f in enumerate(notes):
        tt = bar * 2.0 + k * 0.25
        add(arp, tt, pluck(f, 0.5, bell=(k % 4 == 3)), pan=(-0.4 if k % 2 else 0.4), gain=0.13)

# bass
for bar in range(6):
    r = chords[bar % 4][0]
    for off, ln in ((0, 0.9), (1.25, 0.4), (1.5, 0.4)):
        if bar == 0 and off:
            continue
        n = int(SR * ln); x = np.arange(n) / SR
        s = (np.sin(2 * np.pi * r * x) + 0.3 * np.sin(2 * np.pi * 2 * r * x)) * env(n, 0.01, ln / 2.5)
        add(bass, bar * 2.0 + off, s, gain=0.33)

# drums
def kick():
    n = int(SR * 0.4); x = np.arange(n) / SR
    f = 45 + 90 * np.exp(-x * 28)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 9)

def noise(dur, decay, hp=True):
    n = int(SR * dur); x = np.arange(n) / SR
    z = rng.standard_normal(n)
    if hp:
        z = np.diff(z, prepend=0)  # crude high-pass
    return z * np.exp(-x * decay)

K = kick()
for b in range(int(DUR / BEAT)):
    tb = b * BEAT
    if tb >= 2.0 and tb < 11.0:
        add(drums, tb, K, gain=0.55)
        i = int(tb * SR); duck[i:i + int(0.28 * SR)] *= 1 - 0.55 * np.exp(-np.arange(min(int(0.28 * SR), N - i)) / SR * 9)
    if tb >= 2.0 and tb < 11.5:
        add(drums, tb + 0.25, noise(0.06, 70), gain=0.05, pan=0.2)       # off-beat hat
    if tb >= 4.0 and tb < 11.0 and b % 2 == 1:
        add(drums, tb, noise(0.22, 22, hp=False) * 0.6 + noise(0.22, 30) * 0.4, gain=0.16)  # snare/clap on 2 & 4
# riser into the drop at 2 s and the final lift at 10 s
for a, b0 in ((0.6, 2.0), (8.8, 10.0)):
    n = int((b0 - a) * SR); x = np.linspace(0, 1, n)
    z = np.diff(rng.standard_normal(n), prepend=0) * x ** 3
    add(drums, a, z, gain=0.07)
add(drums, 2.0, noise(0.9, 4) * 0.5, gain=0.12)
add(drums, 10.0, noise(0.9, 4) * 0.5, gain=0.12)

def echo(sig, delay, fb, mix):
    d = int(delay * SR)
    wet = np.zeros_like(sig); cur = sig
    for k in range(1, 5):
        sh = np.zeros_like(sig); sh[:, d * k:] = sig[:, : N - d * k]
        wet += sh * (fb ** k)
    return sig + wet * mix

arp = echo(arp, 0.375, 0.55, 0.9)
# cheap reverb: a few feedback-free decaying taps on the pad+arp bus
bus = pad + arp
rev = np.zeros_like(bus)
for dly, g in ((0.037, .5), (0.071, .4), (0.113, .33), (0.167, .26), (0.241, .2)):
    d = int(dly * SR); rev[:, d:] += bus[:, :-d] * g
mix = (pad + arp * 1.0 + rev * 0.5) * duck + bass * duck + drums
fade = np.clip((DUR - t) / 0.9, 0, 1) * np.clip(t / 0.05, 0, 1)
mix *= fade
mix = np.tanh(mix * 1.6) / 1.6
mix = mix / np.abs(mix).max() * 0.89
pcm = (mix.T * 32767).astype("<i2")
with wave.open("music.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("ok")
