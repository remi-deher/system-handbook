"""Offline comparison only; never plays audio or changes a profile."""
import sys,pathlib,argparse,json
ROOT=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT))
import numpy as np
import soundfile as sf
from scipy import signal
import metrics
def align(y,x,rate,segments):
    # Restrict search to the first sweep; later programme peaks can dominate
    # an unnormalised correlation with the quiet conditioning signal.
    s=next(v for v in segments if v['name']=='sweep' and v.get('input_channel',0)==0)
    a=s['start'];n=s['frames'];search=y[:a+n+rate//3]
    corr=signal.correlate(search[:,0],x[a:a+n,0],mode='valid',method='fft');lag=int(np.argmax(abs(corr)))-a
    z=np.zeros_like(x);lo=max(0,-lag);hi=min(len(x),len(y)-lag);z[lo:hi]=y[lo+lag:hi+lag]
    return z,dict(lag_samples=lag,coverage_start=lo,coverage_end=hi)
def main():
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--windows',required=True);p.add_argument('--linux',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    source=pathlib.Path(a.source);x,r=sf.read(source,dtype='float32',always_2d=True);ref=json.loads(source.with_suffix('.json').read_text())
    arrays=[];alignment=[]
    for path in [a.windows,a.linux]:
        y,yr=sf.read(path,dtype='float32',always_2d=True)
        if yr!=r or y.shape[1]!=2 or not np.isfinite(y).all():raise RuntimeError('Require finite stereo WAV at source sample rate')
        z,meta=align(y,x,r,ref['segments']);arrays.append(z);alignment.append(meta)
    rows=[]
    for s in ref['segments']:
        if s['name'] in ['gap','tail','sync','conditioning_pink','sweep','tone','level_steps']:continue
        begin=s['start'];end=begin+s['frames']
        if any(m['coverage_start']>begin or m['coverage_end']<end for m in alignment):raise RuntimeError('Recording does not cover programme segment '+s['name'])
        w,l=[metrics.programme(v[begin:end]) for v in arrays]
        rows.append(dict(name=s['name'],input_level=s.get('input_level'),windows_lufs=w['lufs'],linux_lufs=l['lufs'],linux_minus_windows_lu=l['lufs']-w['lufs'] if l['lufs'] is not None and w['lufs'] is not None else None,
                         linux_minus_windows_rms_db=l['rms_dbfs']-w['rms_dbfs'],linux_minus_windows_crest_db=l['crest_db']-w['crest_db'],windows_correlation=w['stereo_correlation'],linux_correlation=l['stereo_correlation'],
                         linux_minus_windows_bands_db={k:l['bands_power_dbfs'][k]-w['bands_power_dbfs'][k] for k in w['bands_power_dbfs']}))
    result=dict(source=str(source),windows=a.windows,linux=a.linux,alignment=alignment,comparisons=rows,normalization_applied=False,
                note='Electrical comparison only; verify Linux tap precedes physical attenuation. Absolute delay/correlation alone do not establish equivalent stereo phase or acoustic fidelity.')
    pathlib.Path(a.out).write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8');print('Compared',len(rows),'programme segments; no gain normalization')
if __name__=='__main__':main()
