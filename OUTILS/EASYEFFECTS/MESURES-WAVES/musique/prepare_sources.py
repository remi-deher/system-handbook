"""Prepare music stimuli: FLAC -> 48 kHz stereo float32 WAV at fixed integrated loudness.

No limiter or compressor is applied: only a single linear gain per file. If the
requested loudness would push the peak above PEAK_LIMIT_DBFS, the gain is
reduced and the actual loudness is recorded in the JSON.
"""
import hashlib, json, math, pathlib
from fractions import Fraction
import numpy as np
import soundfile as sf
import pyloudnorm as pyln
from scipy.signal import resample_poly

ROOT = pathlib.Path(__file__).resolve().parent
SAMPLES = ROOT.parent / 'samples'
OUT = ROOT / 'reference'
RATE = 48000
TARGET_LUFS = [-30, -23, -16]
PEAK_LIMIT_DBFS = -1.0
MAX_SECONDS = 45.0
# (file, label, start offset in seconds)
SOURCES = [
    ('instrumental-48000hz-24bit.flac', 'instrumental', 0.0),
    ('music-sample-96000hz-24bit.flac', 'music96', 0.0),
    ('Sample_BeeMoved_96kHz24bit_song.flac', 'beemoved', 0.0),
    ('sample_ultra.flac', 'ultra192', 0.0),
    ('thetestdata-sample-flac-1.flac', 'testdata', 15.0),
    ('voice-sample-44100hz-16bit.flac', 'voice', 0.0),
]


def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def to_48k_stereo(x, rate):
    if x.shape[1] == 1:
        x = np.repeat(x, 2, axis=1)
    elif x.shape[1] > 2:
        x = x[:, :2]
    if rate != RATE:
        f = Fraction(RATE, rate)
        x = resample_poly(x, f.numerator, f.denominator, axis=0)
    return x.astype(np.float64)


def fade(x, fin=0.02, fout=0.3):
    n1, n2 = round(fin * RATE), round(fout * RATE)
    env = np.ones(len(x))
    env[:n1] = np.linspace(0, 1, n1)
    env[-n2:] = np.minimum(env[-n2:], np.linspace(1, 0, n2))
    return x * env[:, None]


def main():
    OUT.mkdir(exist_ok=True)
    meter = pyln.Meter(RATE)
    manifest = []
    for fname, label, start in SOURCES:
        path = SAMPLES / fname
        x, rate = sf.read(path, dtype='float64', always_2d=True)
        channels_in = x.shape[1]
        x = x[round(start * rate):round((start + MAX_SECONDS) * rate)]
        x = to_48k_stereo(x, rate)
        x = fade(x)
        base_lufs = meter.integrated_loudness(x)
        for target in TARGET_LUFS:
            gain_db = target - base_lufs
            peak = np.max(np.abs(x)) * 10 ** (gain_db / 20)
            peak_db = 20 * math.log10(peak)
            limited = False
            if peak_db > PEAK_LIMIT_DBFS:
                gain_db -= peak_db - PEAK_LIMIT_DBFS
                limited = True
            y = x * 10 ** (gain_db / 20)
            lead = np.zeros((RATE, 2))
            t = np.arange(round(.25 * RATE)) / RATE
            s = np.sin(2 * np.pi * 1901 * t)
            e = np.ones(len(s)); n = 480
            e[:n] = np.linspace(0, 1, n); e[-n:] = np.linspace(1, 0, n)
            sync = np.column_stack([s * e, s * e]) * 10 ** (-36 / 20)
            gap = np.zeros((round(.4 * RATE), 2))
            tail = np.zeros((round(1.5 * RATE), 2))
            full = np.concatenate([lead, sync, gap, y, tail]).astype(np.float32)
            music_start = len(lead) + len(sync) + len(gap)
            name = f'{label}_L{abs(target)}.wav'
            sf.write(OUT / name, full, RATE, subtype='FLOAT')
            actual = meter.integrated_loudness(y)
            manifest.append(dict(
                file=name, label=label, source=fname, source_sha256=sha(path),
                source_rate=rate, source_channels=channels_in, source_start_s=start,
                music_start_frame=music_start, music_frames=len(y),
                seconds=len(full) / RATE, target_lufs=target,
                actual_lufs=float(actual), gain_applied_db=float(gain_db),
                peak_dbfs=float(20 * math.log10(np.max(np.abs(y)))),
                peak_limited_gain=limited, sha256=sha(OUT / name)))
            print(f'{name:28s} {len(full)/RATE:6.1f}s  LUFS {actual:6.1f} (cible {target})  peak {manifest[-1]["peak_dbfs"]:6.1f}{"  [gain reduit]" if limited else ""}')
    (OUT / 'reference.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')
    print('total', sum(m['seconds'] for m in manifest), 's for', len(manifest), 'files')


if __name__ == '__main__':
    main()
