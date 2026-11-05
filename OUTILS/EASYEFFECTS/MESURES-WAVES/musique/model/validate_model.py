"""Validate the fitted model on full signals vs the Windows ON captures (and vs an identity baseline)."""
import json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np, pyloudnorm as pyln
from scipy import ndimage
import fit_model as F
from common import *

M = json.loads((F.OUT / 'model.json').read_text())
LIMIT_DB, LOOKAHEAD_MS = -0.3, 5.0


def limiter(x, thr_db=LIMIT_DB, look_ms=LOOKAHEAD_MS):
    n = round(look_ms * RATE / 1000)
    peak = np.max(np.abs(x), axis=1)
    need = np.minimum(1.0, 10 ** (thr_db / 20) / np.maximum(peak, 1e-9))
    g = ndimage.minimum_filter1d(need, size=2 * n + 1, mode='nearest')
    g = ndimage.uniform_filter1d(g, size=n, mode='nearest')
    return x * g[:, None]


def run_chain(src, params=None):
    p = params or M
    eq = F.apply_eq(src, np.array(p['mid_gains']), np.array(p['side_gains']))
    bands = F.split_bands(eq)
    out = np.zeros_like(eq)
    centers = (np.arange(len(eq) // F.BLOCK) + 0.5) * F.BLOCK
    for b, band in enumerate(bands):
        pdb = 10 * np.log10(F.block_power(band) + 1e-30)
        g = F.band_gain_db(pdb, p['thresholds_db'][b], p['ratios'][b])
        out += band * 10 ** (np.interp(np.arange(len(eq)), centers, g) / 20)[:, None]
    return limiter(out)


def metrics(x, meter):
    mid, side = ms(x)
    return dict(lufs=float(meter.integrated_loudness(x)), peak=float(20 * np.log10(np.max(np.abs(x)))),
                rms=float(20 * np.log10(np.sqrt(np.mean(x ** 2)))),
                sm=float(db(np.mean(side ** 2)) - db(np.mean(mid ** 2))),
                corr=float(np.corrcoef(x[:, 0], x[:, 1])[0, 1]) if np.std(x[:, 0] - x[:, 1]) > 1e-9 else 1.0)


def main():
    meter = pyln.Meter(RATE)
    rows, band_err_model, band_err_ident = [], [], []
    for t in TRACKS:
        for L in (30, 23, 16):
            base = f'{t}_L{L}'
            src, on = source(base), capture(base, 'on')
            pred = run_chain(src)
            mm, mp, ms_ = metrics(on, meter), metrics(pred, meter), metrics(src, meter)
            lv_on, lv_pr, lv_sr = [third_levels(ms(z)[0]) for z in (on, pred, src)]
            sel = [i for i, f in enumerate(THIRDS) if 63 <= f <= 12500]
            e_m, e_i = (lv_pr - lv_on)[sel], (lv_sr - lv_on)[sel]
            band_err_model.append(e_m); band_err_ident.append(e_i)
            row = dict(id=base, lufs_on=mm['lufs'], lufs_model=mp['lufs'], lufs_src=ms_['lufs'],
                       peak_on=mm['peak'], peak_model=mp['peak'], sm_on=mm['sm'], sm_model=mp['sm'], sm_src=ms_['sm'],
                       corr_on=mm['corr'], corr_model=mp['corr'],
                       mid_band_rms_model=float(np.sqrt(np.mean(e_m ** 2))), mid_band_rms_identity=float(np.sqrt(np.mean(e_i ** 2))))
            if t in STEREO_TRACKS:
                s_on, s_pr = [third_levels(ms(z)[1]) for z in (on, pred)]
                row['side_band_rms_model'] = float(np.sqrt(np.mean((s_pr - s_on)[sel] ** 2)))
            rows.append(row)
            print(f'{base:18s} LUFS on {mm["lufs"]:6.1f} model {mp["lufs"]:6.1f} (src {ms_["lufs"]:5.1f}) | peak on {mm["peak"]:5.1f} model {mp["peak"]:5.1f} | S/M on {mm["sm"]:6.1f} model {mp["sm"]:6.1f} | corr on {mm["corr"]:.2f} model {mp["corr"]:.2f} | mid-band err RMS model {row["mid_band_rms_model"]:.1f} vs identity {row["mid_band_rms_identity"]:.1f} dB')
    d = np.array([r['lufs_model'] - r['lufs_on'] for r in rows])
    print(f'\nLUFS error model-ON: mean {d.mean():+.2f}, max |{np.abs(d).max():.2f}| dB')
    print(f'1/3-octave Mid error RMS (63-12.5k): model {np.sqrt(np.mean(np.array(band_err_model)**2)):.2f} dB, no-processing {np.sqrt(np.mean(np.array(band_err_ident)**2)):.2f} dB')
    sr = [r['side_band_rms_model'] for r in rows if 'side_band_rms_model' in r]
    print(f'Side error RMS (stereo tracks): {np.mean(sr):.2f} dB')
    print('Mid error by band (mean over files, dB):', dict(zip([THIRDS[i] for i in sel], np.round(np.mean(band_err_model, axis=0), 1))))
    json.dump(rows, open(F.OUT / 'validation.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
