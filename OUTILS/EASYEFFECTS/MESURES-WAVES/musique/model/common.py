"""Shared helpers for the Waves-ON model: loading aligned captures, band tools."""
import json, pathlib
import numpy as np, soundfile as sf
from scipy import signal

ROOT = pathlib.Path(__file__).resolve().parent.parent
RATE = 48000
THIRDS = [50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000,
          2500, 3150, 4000, 5000, 6300, 8000, 10000, 12500, 16000]
RES = {r['id']: r for r in json.loads((ROOT / 'analysis' / 'results.json').read_text(encoding='utf-8'))}
REF = {r['file']: r for r in json.loads((ROOT / 'reference' / 'reference.json').read_text(encoding='utf-8'))}
TRACKS = ['instrumental', 'music96', 'beemoved', 'ultra192', 'testdata', 'voice']
STEREO_TRACKS = ['instrumental', 'music96', 'beemoved']  # real Side content


def db(x):
    return 10 * np.log10(np.maximum(x, 1e-30))


def source(base):
    """Return music segment of the prepared source (float64 [n,2])."""
    r = REF[base + '.wav']
    x, _ = sf.read(ROOT / 'reference' / r['file'], dtype='float64', always_2d=True)
    return x[r['music_start_frame']:r['music_start_frame'] + r['music_frames']]


def capture(base, state):
    """Aligned capture music segment, using lags stored by analyze.py."""
    r = REF[base + '.wav']
    cap, _ = sf.read(ROOT / 'captures' / f'{base}_{state}.wav', dtype='float64', always_2d=True)
    lag = int(round(RES[base][f'{state}_lag_ms'] * RATE / 1000))
    a = r['music_start_frame'] + lag
    out = np.zeros((r['music_frames'], 2))
    seg = cap[max(a, 0):a + r['music_frames']]
    out[:len(seg)] = seg
    return out


def ms(x):
    return (x[:, 0] + x[:, 1]) / 2, (x[:, 0] - x[:, 1]) / 2


def third_levels(x):
    """Power (dB) per 1/3-octave band, 1-D signal."""
    f, p = signal.welch(x, RATE, nperseg=16384)
    df = f[1] - f[0]
    return np.array([db(p[(f >= fc / 2 ** (1 / 6)) & (f < fc * 2 ** (1 / 6))].sum() * df) for fc in THIRDS])


def lr_from_ms(m, s):
    return np.column_stack([m + s, m - s])
