"""Apparent transfers, harmonic fits and M/S statistics for isolated effects."""
import csv,hashlib,json,os,pathlib
import numpy as np
import soundfile as sf
from scipy import signal
ROOT=pathlib.Path(__file__).resolve().parent
def db(v):return 20*np.log10(np.maximum(np.abs(v),1e-30))
def rms(v):return np.sqrt(np.mean(np.asarray(v)**2,axis=0))
def writecsv(name,rows):
    if not rows:return
    with (ROOT/'analysis'/name).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=sorted(set().union(*(r.keys() for r in rows))));w.writeheader();w.writerows(rows)
def main():
    refpath=ROOT/'reference/isolation.wav';x,rate=sf.read(refpath,always_2d=True)
    ref=json.loads(refpath.with_suffix('.json').read_text());segs=ref['segments']
    transfers=[];tones=[];noises=[];checks=[];msrows=[]
    centers=80*2**(np.arange(0,94)/12);centers=centers[centers<=16000]
    for path in sorted((ROOT/'captures').glob('*.wav')):
        mp=path.with_suffix('.json')
        if not mp.exists():continue
        meta=json.loads(mp.read_text())
        if 'ui_state_before' not in meta:continue
        y,r=sf.read(path,always_2d=True);assert r==rate
        seg=next(s for s in segs if s['name']=='sweep');start=seg['start'];n=seg['frames']
        template=x[start:start+n,0]
        corr=signal.correlate(y[:start+n+rate//5,0],template,mode='valid',method='fft')
        lag=int(np.argmax(np.abs(corr)))-start
        z=np.zeros_like(x);lo=max(0,-lag);hi=min(len(x),len(y)-lag);z[lo:hi]=y[lo+lag:hi+lag]
        check=dict(label=path.stem,lag_samples=lag,frames=len(y),source_coverage_start=lo,source_coverage_end=hi,
                   clipped_samples=int(np.sum(np.abs(y)>=1)),finite=bool(np.isfinite(y).all()),
                   callback_events=meta['callback_events'],ui_unchanged=meta['ui_state_before']==meta['ui_state_after'],
                   file_sha256_ok=hashlib.sha256(path.read_bytes()).hexdigest()==meta['capture_sha256'],
                   source_sha256_ok=hashlib.sha256(refpath.read_bytes()).hexdigest()==meta['source_sha256'],
                   effect_levels=meta['effect_levels'],volume=meta['volume_scalar'],peak_dbfs=float(db(np.max(np.abs(y)))))
        checks.append(check)
        shared=dict(capture=path.stem,volume=meta['volume_scalar'],power=meta['ui_state_before']['power'],bass=int(meta['ui_state_before']['bass'].split()[0]),details=int(meta['ui_state_before']['details'].split()[0]),width=int(meta['ui_state_before']['width'].split()[0]))
        matrix_by_level={}
        for s in segs:
            a=s['start'];b=a+s['frames']
            if s['name']=='sweep':
                inch=s['input_channel'];end=b+round(.15*rate);nt=131072
                X=np.fft.rfft(x[a:end,inch],n=nt);Y=np.fft.rfft(z[a:end],n=nt,axis=0);freq=np.fft.rfftfreq(nt,1/rate)
                H=Y*np.conj(X[:,None])/(np.abs(X[:,None])**2+1e-28)
                matrix_by_level[(s['level_dbfs'],inch)]=H
                for outch in [0,1]:
                    phase=np.unwrap(np.angle(H[:,outch]))
                    for center in centers:
                        mask=(freq>=center/2**(1/24))&(freq<center*2**(1/24))
                        h=H[mask,outch]
                        ratio=H[mask,outch]/(H[mask,inch]+1e-30)
                        transfers.append(dict(**shared,input_level=s['level_dbfs'],input_channel=inch,output_channel=outch,Hz=float(center),magnitude_db=float(db(np.sqrt(np.mean(abs(h)**2)))),phase_rad=float(np.mean(phase[mask])),cross_to_direct_gain_db=float(db(np.sqrt(np.mean(abs(ratio)**2)))),cross_to_direct_phase_rad=float(np.angle(np.mean(ratio)))))
            if s['name']=='tone':
                f=s['frequency'];harmonics=min(8,20000//f)
                for startsec,endsec in [(.1,.2),(.3,.5)]:
                    v=z[a+round(startsec*rate):a+round(endsec*rate)];t=np.arange(len(v))/rate
                    basis=np.column_stack([fun(2*np.pi*f*h*t) for h in range(1,harmonics+1) for fun in [np.sin,np.cos]]+[np.ones(len(t))])
                    coeff=np.linalg.lstsq(basis,v,rcond=None)[0];amps=np.hypot(coeff[0:2*harmonics:2],coeff[1:2*harmonics:2]);fund=amps[0]
                    residual=v-basis@coeff
                    for ch in [0,1]:
                        item=dict(**shared,frequency=f,input_level=s['level_dbfs'],channel=ch,window_start_s=startsec,window_end_s=endsec,
                            fundamental_peak_dbfs=float(db(fund[ch])),gain_db=float(db(fund[ch])-s['level_dbfs']),
                            harmonics_relative_db=float(db(np.linalg.norm(amps[1:,ch])/max(fund[ch],1e-30))),
                            residual_dbfs=float(db(rms(residual)[ch])))
                        for h in range(harmonics):item[f'h{h+1}_peak_dbfs']=float(db(amps[h,ch]))
                        tones.append(item)
            if s['name']=='noise':
                pad=round(.1*rate);v=z[a+pad:b-pad];xx=x[a+pad:b-pad]
                mid=(v[:,0]+v[:,1])/2;side=(v[:,0]-v[:,1])/2
                noises.append(dict(**shared,input_level=s['level_dbfs'],mode=s['mode'],gain_db=float(db(np.sqrt(np.mean(v*v))/np.sqrt(np.mean(xx*xx)))),
                    left_rms_dbfs=float(db(rms(v)[0])),right_rms_dbfs=float(db(rms(v)[1])),mid_rms_dbfs=float(db(rms(mid))),side_rms_dbfs=float(db(rms(side))),
                    stereo_correlation=float(np.corrcoef(v.T)[0,1]) if np.all(rms(v)>0) else None))
        for level in [-60,-48,-36]:
            hl=matrix_by_level[(level,0)];hr=matrix_by_level[(level,1)]
            mid=(hl[:,0]+hr[:,0]+hl[:,1]+hr[:,1])/2
            side=(hl[:,0]-hr[:,0]-hl[:,1]+hr[:,1])/2
            for center in centers:
                mask=(freq>=center/2**(1/24))&(freq<center*2**(1/24))
                msrows.append(dict(**shared,input_level=level,Hz=float(center),mid_gain_db=float(db(np.sqrt(np.mean(abs(mid[mask])**2)))),side_gain_db=float(db(np.sqrt(np.mean(abs(side[mask])**2))))))
    writecsv('transfers.csv',transfers);writecsv('tones.csv',tones);writecsv('noise-stereo.csv',noises);writecsv('mid-side-apparent.csv',msrows)
    (ROOT/'analysis/validation.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
    # Subtract ON/zero at the same source level, channel and frequency. This
    # removes the always-on baseline, not an assumed flat/bypass response.
    base={(v['input_level'],v['input_channel'],v['output_channel'],v['Hz']):v for v in transfers if v['capture']=='baseline-zero-first'}
    repeated={}
    for v in transfers:
        if v['capture']=='baseline-zero-first' or (v['capture'].startswith('zero-') and v['volume']==.1):
            key=(v['input_level'],v['input_channel'],v['output_channel'],v['Hz'])
            repeated.setdefault(key,[]).append(v['magnitude_db'])
    repeatrows=[]
    for key,values in repeated.items():
        repeatrows.append(dict(input_level=key[0],input_channel=key[1],output_channel=key[2],Hz=key[3],count=len(values),min_db=min(values),median_db=float(np.median(values)),max_db=max(values),spread_db=max(values)-min(values)))
    writecsv('zero-reference-envelope.csv',repeatrows)
    delta=[]
    for v in transfers:
        b=base.get((v['input_level'],v['input_channel'],v['output_channel'],v['Hz']))
        if b and b['magnitude_db']>-140:
            values=repeated[(v['input_level'],v['input_channel'],v['output_channel'],v['Hz'])]
            delta.append(dict(**v,delta_from_zero_db=v['magnitude_db']-b['magnitude_db'],phase_delta_rad=v['phase_rad']-b['phase_rad'],delta_from_zero_median_db=v['magnitude_db']-float(np.median(values)),delta_min_vs_repeated_zeros_db=v['magnitude_db']-max(values),delta_max_vs_repeated_zeros_db=v['magnitude_db']-min(values),zero_repeat_spread_db=max(values)-min(values)))
    writecsv('transfers-relative-to-zero.csv',delta)
    baseline_tones={(v['frequency'],v['input_level'],v['channel'],v['window_start_s']):v for v in tones if v['capture']=='baseline-zero-first'}
    highlights=[]
    for v in tones:
        if v['channel'] or v['window_start_s']!=.3:continue
        b=baseline_tones[(v['frequency'],v['input_level'],v['channel'],v['window_start_s'])]
        highlights.append(dict(**v,delta_gain_from_zero_db=v['gain_db']-b['gain_db']))
    writecsv('tone-comparisons.csv',highlights)
    (ROOT/'analysis/progress.json').write_text(json.dumps(dict(captures=len(checks),all_finite=all(v['finite'] for v in checks),clipped_captures=[v['label'] for v in checks if v['clipped_samples']],all_hashes_match=all(v['file_sha256_ok'] and v['source_sha256_ok'] for v in checks),all_ui_unchanged=all(v['ui_unchanged'] for v in checks)),indent=2),encoding='utf-8')
    print((ROOT/'analysis/progress.json').read_text())
if __name__=='__main__':main()
