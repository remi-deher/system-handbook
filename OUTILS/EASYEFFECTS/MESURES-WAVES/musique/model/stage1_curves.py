"""Stage 1: static Mid and Side gain curves (1/3 octave) from ON captures at -30 LUFS source."""
import csv, json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np
from common import *

OUT = ROOT / 'model'
LEVEL = 30
mid_g, side_g, mid_w = [], [], []
for t in TRACKS:
    base = f'{t}_L{LEVEL}'
    s, on = source(base), capture(base, 'on')
    sm, ss = ms(s); om, os_ = ms(on)
    mid_g.append(third_levels(om) - third_levels(sm))
    if t in STEREO_TRACKS:
        side_g.append(third_levels(os_) - third_levels(ss))
mid_g, side_g = np.array(mid_g), np.array(side_g)
mid = np.median(mid_g, axis=0)
side = np.median(side_g, axis=0)
spread_mid, spread_side = mid_g.std(axis=0), side_g.std(axis=0)

# informational: OFF state vs existing SST candidate curve
off = []
for t in TRACKS:
    base = f'{t}_L{LEVEL}'
    s, o = source(base), capture(base, 'off')
    sm, _ = ms(s); om, _ = ms(o)
    off.append(third_levels(om) - third_levels(sm))
off = np.median(off, axis=0)
cand = np.genfromtxt(ROOT.parent / 'candidate-response-linux.csv', delimiter=',', skip_header=1)
cand_at = np.interp(np.log(THIRDS), np.log(cand[:, 0]), cand[:, 1]) - 6.0  # profile has -6 dB input gain

print('Hz     midON  sideON | spread(m,s) | OFF    SSTcand(-6dB)')
for i, f in enumerate(THIRDS):
    print(f'{f:6d} {mid[i]:6.1f} {side[i]:6.1f} | {spread_mid[i]:4.1f} {spread_side[i]:4.1f} | {off[i]:6.1f} {cand_at[i]:6.1f}')
json.dump(dict(freqs=THIRDS, mid_db=mid.tolist(), side_db=side.tolist(), spread_mid=spread_mid.tolist(),
               spread_side=spread_side.tolist(), off_db=off.tolist(), level_lufs=-LEVEL),
          open(OUT / 'curves.json', 'w'), indent=1)
