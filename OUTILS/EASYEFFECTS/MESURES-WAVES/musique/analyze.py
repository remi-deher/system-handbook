"""Analyse music loopback captures: Waves ON vs OFF vs source (all 48 kHz float32 stereo)."""
import csv, json, math, pathlib
import numpy as np
import soundfile as sf
import pyloudnorm as pyln
from scipy import signal

ROOT = pathlib.Path(__file__).resolve().parent
RATE = 48000
REF = {r['file']: r for r in json.loads((ROOT / 'reference' / 'reference.json').read_text(encoding='utf-8'))}
THIRDS = [50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000, 12500, 16000]
MACRO = {'grave 40-120': (40, 120), 'bas-med 120-500': (120, 500), 'medium 500-2k': (500, 2000),
         'presence 2k-6k': (2000, 6000), 'aigu 6k-16k': (6000, 16000)}
EPS = 1e-20


def db(x):
    return 10 * np.log10(np.maximum(x, EPS))


def load_cap(label):
    x, r = sf.read(ROOT / 'captures' / (label + '.wav'), dtype='float64', always_2d=True)
    return x


def env(x, win=96):
    e = np.abs(x).mean(axis=1) if x.ndim == 2 else np.abs(x)
    return np.convolve(e, np.ones(win) / win, mode='same')


def align(src, cap, music_start, music_len):
    """Return cap shifted so that cap[i] corresponds to src[i]. Coarse: sync burst / envelope; fine: envelope xcorr."""
    n = min(len(cap), 12 * RATE)
    es, ec = env(src[:n]), env(cap[:n])
    es, ec = es - es.mean(), ec - ec.mean()
    c = signal.correlate(ec, es, mode='full', method='fft')
    lag = int(np.argmax(c) - (len(es) - 1))
    # fine on music envelope (downsampled) +/- 30 ms around coarse lag
    best, best_v = lag, -1
    seg = slice(music_start, music_start + min(music_len, 20 * RATE))
    s = env(src[seg], 48)
    for l in range(lag - 1440, lag + 1441, 4):
        a = seg.start + l
        if a < 0 or a + (seg.stop - seg.start) > len(cap):
            continue
        cc = env(cap[a:a + (seg.stop - seg.start)], 48)
        v = np.corrcoef(s[::24], cc[::24])[0, 1]
        if v > best_v:
            best_v, best = v, l
    out = np.zeros_like(src)
    a = max(0, best); b = min(len(cap), len(src) + best)
    out[a - best:b - best] = cap[a:b]
    return out, best, float(best_v)


def band_power(x, f_lo, f_hi, nper=16384):
    f, p = signal.welch(x, RATE, nperseg=nper, axis=0)
    m = (f >= f_lo) & (f < f_hi)
    return p[m].sum(axis=0) * (f[1] - f[0])


def third_octave_levels(x):
    """Per-channel power (dB) per 1/3 octave band over the whole segment."""
    f, p = signal.welch(x, RATE, nperseg=16384, axis=0)
    df = f[1] - f[0]
    out = []
    for fc in THIRDS:
        lo, hi = fc / 2 ** (1 / 6), fc * 2 ** (1 / 6)
        m = (f >= lo) & (f < hi)
        out.append(db(p[m].sum(axis=0) * df))
    return np.array(out)  # [band, ch]


def frames_macro(x, win=int(.4 * RATE), hop=int(.2 * RATE)):
    """Energy per frame per macroband on mid+side-agnostic mono-sum power (sum over channels)."""
    n = (len(x) - win) // hop
    w = signal.get_window('hann', win)
    f = np.fft.rfftfreq(win, 1 / RATE)
    res = {k: np.zeros(n) for k in MACRO}
    for i in range(n):
        seg = x[i * hop:i * hop + win] * w[:, None]
        sp = (np.abs(np.fft.rfft(seg, axis=0)) ** 2).sum(axis=1)
        for k, (lo, hi) in MACRO.items():
            res[k][i] = sp[(f >= lo) & (f < hi)].sum()
    return res


def stereo_stats(x):
    l, r = x[:, 0], x[:, 1]
    mid, side = (l + r) / 2, (l - r) / 2
    pm, ps = np.mean(mid ** 2), np.mean(side ** 2)
    corr = float(np.corrcoef(l, r)[0, 1]) if np.std(l) > 0 and np.std(r) > 0 else float('nan')
    return dict(side_over_mid_db=float(db(ps) - db(pm)), lr_corr=corr)


def true_peak_db(x):
    up = signal.resample_poly(x, 4, 1, axis=0)
    return float(20 * np.log10(max(np.max(np.abs(up)), 1e-12)))


def main():
    meter = pyln.Meter(RATE)
    results, bands_rows, slope_rows = [], [], []
    for caps in sorted((ROOT / 'captures').glob('*_on.wav')):
        label_on = caps.stem
        base = label_on[:-3]  # e.g. voice_L23
        label_off = base + '_off'
        if not (ROOT / 'captures' / (label_off + '.wav')).exists():
            continue
        r = REF[base + '.wav']
        src, _ = sf.read(ROOT / 'reference' / r['file'], dtype='float64', always_2d=True)
        ms, ml = r['music_start_frame'], r['music_frames']
        item = dict(id=base, track=r['label'], target_lufs=r['target_lufs'], src_lufs=r['actual_lufs'])
        seg = slice(ms, ms + ml)
        data = {'src': src[seg]}
        for state in ['on', 'off']:
            cap = load_cap(f'{base}_{state}')
            al, lag, q = align(src, cap, ms, ml)
            data[state] = al[seg]
            item[f'{state}_lag_ms'] = lag / RATE * 1000
            item[f'{state}_align_quality'] = q
        for k, x in data.items():
            item[f'{k}_lufs'] = float(meter.integrated_loudness(x))
            item[f'{k}_rms_dbfs'] = float(20 * np.log10(np.sqrt(np.mean(x ** 2))))
            item[f'{k}_peak_dbfs'] = float(20 * np.log10(np.max(np.abs(x))))
            item[f'{k}_truepeak_dbfs'] = true_peak_db(x)
            item[f'{k}_crest_db'] = item[f'{k}_peak_dbfs'] - item[f'{k}_rms_dbfs']
            item[f'{k}_stereo'] = stereo_stats(x)
        item['on_samples_ge_1'] = int(np.sum(np.abs(data['on']) >= 1.0))
        item['gain_on_minus_off_lufs'] = item['on_lufs'] - item['off_lufs']
        item['gain_off_minus_src_lufs'] = item['off_lufs'] - item['src_lufs']
        item['gain_on_minus_src_lufs'] = item['on_lufs'] - item['src_lufs']
        # 1/3-octave long-term gains
        lv = {k: third_octave_levels(v) for k, v in data.items()}
        for i, fc in enumerate(THIRDS):
            bands_rows.append(dict(id=base, track=r['label'], lufs=r['target_lufs'], freq_hz=fc,
                                   off_minus_src_db=float(np.mean(lv['off'][i] - lv['src'][i])),
                                   on_minus_src_db=float(np.mean(lv['on'][i] - lv['src'][i])),
                                   on_minus_off_db=float(np.mean(lv['on'][i] - lv['off'][i])),
                                   on_L_minus_R_db=float(lv['on'][i, 0] - lv['on'][i, 1]),
                                   src_L_minus_R_db=float(lv['src'][i, 0] - lv['src'][i, 1])))
        # time-varying gain + slope (compression indicator)
        fr = {k: frames_macro(v) for k, v in data.items()}
        for band in MACRO:
            s_db = db(fr['src'][band])
            ok = s_db > (np.max(s_db) - 60)
            for state in ['on', 'off']:
                o_db = db(fr[state][band])
                g = (o_db - s_db)[ok]
                if ok.sum() < 8:
                    continue
                slope = float(np.polyfit(s_db[ok], o_db[ok], 1)[0])
                slope_rows.append(dict(id=base, track=r['label'], lufs=r['target_lufs'], band=band, state=state,
                                       gain_median_db=float(np.median(g)), gain_p10_db=float(np.percentile(g, 10)),
                                       gain_p90_db=float(np.percentile(g, 90)), gain_spread_db=float(np.percentile(g, 90) - np.percentile(g, 10)),
                                       slope_out_vs_in=slope, frames=int(ok.sum())))
        # coherence src -> capture (linearity), mid channel
        for state in ['on', 'off']:
            ms_src = data['src'].mean(axis=1); ms_out = data[state].mean(axis=1)
            f, coh = signal.coherence(ms_src, ms_out, RATE, nperseg=8192)
            for k, (lo, hi) in MACRO.items():
                m = (f >= lo) & (f < hi)
                item[f'{state}_coherence_{k}'] = float(np.mean(coh[m]))
        results.append(item)
        print(f'{base:18s} lag on/off {item["on_lag_ms"]:.1f}/{item["off_lag_ms"]:.1f} ms  ON-OFF {item["gain_on_minus_off_lufs"]:+.1f} LU  OFF-src {item["gain_off_minus_src_lufs"]:+.1f}  peak ON {item["on_peak_dbfs"]:.1f}', flush=True)
    out = ROOT / 'analysis'; out.mkdir(exist_ok=True)
    (out / 'results.json').write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding='utf-8')
    for name, rows in [('band-gains.csv', bands_rows), ('dynamics-by-band.csv', slope_rows)]:
        with open(out / name, 'w', newline='', encoding='utf-8') as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print('written', len(results), 'comparisons')


if __name__ == '__main__':
    main()
