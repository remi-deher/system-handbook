"""Analyze generated tests; all transfers are apparent, not proven LTI models."""
import csv, json, pathlib
import numpy as np
import soundfile as sf
from scipy import signal
ROOT=pathlib.Path(__file__).resolve().parent
def db(v):return 20*np.log10(np.maximum(1e-30,np.abs(v)))
def rms(v):return float(np.sqrt(np.mean(np.asarray(v)**2)))
def main():
    x,rate=sf.read(ROOT/'reference/pilot.wav',always_2d=True)
    ref=json.loads((ROOT/'reference/pilot.json').read_text()); segs=ref['segments']
    summary={}; aligned={}; transfers={}; rows=[]
    for path in sorted((ROOT/'captures').glob('pilot-*.wav')):
        y,yr=sf.read(path,always_2d=True); assert yr==rate
        # Align on the complete left-channel sweep; do not rely on wall-clock times.
        seg=next(s for s in segs if s['name']=='sweep_left');start=seg['start'];n=seg['frames']
        template=x[start:start+n,0]
        c=signal.correlate(y[:min(len(y),start+n+rate),0],template,method='fft',mode='valid')
        k=int(np.argmax(np.abs(c)));lag=k-start
        z=np.zeros_like(x); lo=max(0,-lag);hi=min(len(x),len(y)-lag);z[lo:hi]=y[lo+lag:hi+lag]
        aligned[path.stem]=z
        info=dict(frames=len(y),source_frames=len(x),lag_samples=lag,source_coverage=[lo,hi],
                  peak_dbfs=float(db(np.max(np.abs(y)))),rms_dbfs=float(db(rms(y))),finite=bool(np.all(np.isfinite(y))),clipped_samples=int(np.sum(np.abs(y)>=1)),segments={})
        for s in segs:
            if s['name']=='gap':continue
            a=s['start'];b=a+s['frames'];pad=round(.15*rate) if s['name'].startswith('tone_') else 0
            xx=x[a+pad:b-pad];zz=z[a+pad:b-pad]
            item=dict(source_rms_dbfs=float(db(rms(xx))),captured_rms_dbfs=float(db(rms(zz))))
            if np.any(xx):item['gain_db']=float(db(rms(zz)/rms(xx)))
            if s['name'].startswith('tone_'):
                t=np.arange(len(zz))/rate
                # Least squares sine/cosine fit avoids FFT-bin leakage at 997 Hz.
                basis=np.column_stack([fun(2*np.pi*997*h*t) for h in range(1,9) for fun in [np.sin,np.cos]]+[np.ones(len(t))])
                amps=[];ths=[]
                for ch in range(2):
                    fit=np.linalg.lstsq(basis,zz[:,ch],rcond=None)[0];fund=np.hypot(*fit[:2]);amps.append(float(db(fund)))
                    harmonics=[np.hypot(*fit[2*h:2*h+2]) for h in range(1,8)]
                    ths.append(float(db(np.linalg.norm(harmonics)/max(fund,1e-30))))
                item.update(fundamental_peak_dbfs=amps,harmonics_2_to_8_relative_db=ths)
            info['segments'][s['name']]=item
        # Separate sweeps provide both output channels per input. Retain complex
        # responses, but delay is relative to the alignment convention above.
        nt=131072;freq=np.fft.rfftfreq(nt,1/rate);matrix=[]
        for inch,name in enumerate(['sweep_left','sweep_right']):
            s=next(s for s in segs if s['name']==name);a=s['start'];b=a+s['frames']+round(.3*rate)
            X=np.fft.rfft(x[a:b,inch],n=nt);Y=np.fft.rfft(z[a:b],n=nt,axis=0)
            H=Y*np.conj(X[:,None])/(np.abs(X[:,None])**2+1e-20)
            matrix.append(H)
        transfers[path.stem]=(freq,matrix)
        summary[path.stem]=info
        for sname,sdata in info['segments'].items():rows.append(dict(capture=path.stem,segment=sname,**{k:v for k,v in sdata.items() if not isinstance(v,list)}))
    comparisons={}
    pairs=[('pilot-on1','pilot-on2'),('pilot-off1','pilot-off2'),('pilot-off1','pilot-on1'),('pilot-off1','pilot-on2'),('pilot-off1','pilot-off-volume05'),('pilot-on2','pilot-on-volume05'),('pilot-on2','pilot-on-muted')]
    for an,bn in pairs:
        if an not in aligned or bn not in aligned:continue
        a=aligned[an];b=aligned[bn];mask=np.any(np.abs(x)>1e-8,axis=1)
        av=a[mask].ravel();bv=b[mask].ravel();g=float(np.dot(av,bv)/max(1e-30,np.dot(av,av)))
        comparisons[an+' -> '+bn]=dict(rms_ratio_db=float(db(rms(bv)/rms(av))),least_squares_gain=g,
                gain_matched_residual_relative_db=float(db(rms(bv-g*av)/max(1e-30,rms(bv)))))
    # Derived listening material is separate from untouched raw acquisitions.
    derived=ROOT/'analysis/aligned';derived.mkdir(exist_ok=True)
    reference_mask=np.any(np.abs(x)>1e-8,axis=1)
    if 'pilot-off1' in aligned and 'pilot-on1' in aligned:
        off=aligned['pilot-off1'];on=aligned['pilot-on1']
        factor=rms(off[reference_mask])/rms(on[reference_mask])
        sf.write(derived/'pilot-off1-aligned.wav',off,rate,subtype='FLOAT')
        sf.write(derived/'pilot-on1-aligned.wav',on,rate,subtype='FLOAT')
        sf.write(derived/'pilot-on1-RMS-matched-to-off1.wav',on*factor,rate,subtype='FLOAT')
        (derived/'method.json').write_text(json.dumps(dict(alignment='Source left sweep cross-correlation, independent per capture; no acoustic delay claim',on_to_off_linear_factor=factor,on_to_off_db=float(db(factor)),mask='Any nonzero source channel',normalization='Single scalar for both channels; RMS, not perceptual loudness',raw_files_unchanged=True),indent=2),encoding='utf-8')
    (ROOT/'analysis/summary.json').write_text(json.dumps(dict(captures=summary,comparisons=comparisons),indent=2),encoding='utf-8')
    with (ROOT/'analysis/segments.csv').open('w',newline='') as f:
        keys=sorted(set().union(*(r.keys() for r in rows)));w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
    # Standard CSV of 1/12 octave energy averages, plus unwrapped phase.
    with (ROOT/'analysis/apparent-transfers.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['capture','input','output','Hz','magnitude_dB','phase_rad_relative_alignment'])
        for name,(freq,mat) in transfers.items():
            for inch,H in enumerate(mat):
                for outch in range(2):
                    phase=np.unwrap(np.angle(H[:,outch]))
                    for center in 100*2**(np.arange(0,90)/12):
                        if center>16000:break
                        mask=(freq>=center/2**(1/24))&(freq<center*2**(1/24))
                        w.writerow([name,inch,outch,center,float(db(np.sqrt(np.mean(np.abs(H[mask,outch])**2)))),float(np.mean(phase[mask]))])
    print(json.dumps(comparisons,indent=2))
    for name,info in summary.items():
        print(name,'lag',info['lag_samples'],'peak',info['peak_dbfs'])
        for sn,si in info['segments'].items():
            if sn.startswith('tone_'):print(' ',sn,'gain',round(si['gain_db'],3),'harmonics rel dB',np.round(si['harmonics_2_to_8_relative_db'],2))
if __name__=='__main__':main()
