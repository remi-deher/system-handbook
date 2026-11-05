"""Quick stereo-widening probe: Side/Mid per band, ON vs OFF, on a mono-source (voice) and stereo music."""
import json, pathlib, sys
import numpy as np, soundfile as sf
from scipy import signal
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import analyze as A

R = A.RATE
BANDS = [(80, 200), (200, 500), (500, 1000), (1000, 2000), (2000, 4000), (4000, 8000), (8000, 16000)]
for base in ['voice_L23', 'voice_L30', 'instrumental_L23', 'beemoved_L23']:
    r = A.REF[base + '.wav']
    src, _ = sf.read(A.ROOT / 'reference' / r['file'], dtype='float64', always_2d=True)
    ms, ml = r['music_start_frame'], r['music_frames']
    print(f'\n== {base} (source {"mono" if r["source_channels"]==1 else "stereo"})')
    for state in ['off', 'on']:
        cap = A.load_cap(f'{base}_{state}')
        al, lag, q = A.align(src, cap, ms, ml)
        x = al[ms:ms + ml]
        mid, side = (x[:, 0] + x[:, 1]) / 2, (x[:, 0] - x[:, 1]) / 2
        row = []
        for lo, hi in BANDS:
            pm = A.band_power(mid, lo, hi); ps = A.band_power(side, lo, hi)
            row.append(10 * np.log10(ps / pm))
        # lag between L and R (xcorr of band 1-4k) and inter-channel coherence
        sos = signal.butter(4, [1000, 4000], 'bandpass', fs=R, output='sos')
        l, rr = signal.sosfilt(sos, x[:, 0]), signal.sosfilt(sos, x[:, 1])
        c = signal.correlate(rr, l, mode='full', method='fft')
        k = int(np.argmax(np.abs(c)) - (len(l) - 1))
        f, coh = signal.coherence(x[:, 0], x[:, 1], R, nperseg=8192)
        coh_b = [float(np.mean(coh[(f >= lo) & (f < hi)])) for lo, hi in BANDS]
        print(f'{state.upper():3s} Side/Mid dB  ' + ' '.join(f'{v:6.1f}' for v in row))
        print(f'    L-R coherence ' + ' '.join(f'{v:6.2f}' for v in coh_b) + f'   L/R lag(1-4k) {k/R*1000:+.2f} ms')
print('\nbandes Hz:', BANDS)
