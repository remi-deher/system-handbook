import hashlib,json,pathlib
import numpy as np
import soundfile as sf
from scipy import signal
ROOT=pathlib.Path(__file__).resolve().parent
RATE=48000
def build():
    parts=[];segments=[];position=0
    def add(name,v,**details):
        nonlocal position
        parts.append(v);segments.append(dict(name=name,start=position,frames=len(v),**details));position+=len(v)
    def silence(s):return np.zeros((round(s*RATE),2))
    add('lead',silence(1))
    t=np.arange(RATE//4)/RATE;s=np.sin(2*np.pi*1901*t)*10**(-36/20);s*=np.sin(np.linspace(0,np.pi,len(s)))**2
    add('sync',np.column_stack([s,s]));add('gap',silence(.5))
    t=np.arange(2*RATE)/RATE;env=np.ones(len(t));n=960;env[:n]=np.linspace(0,1,n);env[-n:]=np.linspace(1,0,n)
    for f in [125,997]:
        for db in [-30,-48,-36,-30]:
            v=np.sin(2*np.pi*f*t)*env*10**(db/20)
            add('tone',np.column_stack([v,v]),frequency=f,peak_dbfs=db);add('gap',silence(1))
    add('tail',silence(1));x=np.concatenate(parts).astype('float32');p=ROOT/'reference/dynamics.wav';sf.write(p,x,RATE,subtype='FLOAT')
    (ROOT/'reference/dynamics.json').write_text(json.dumps(dict(rate=RATE,segments=segments,frames=len(x),sha256=hashlib.sha256(p.read_bytes()).hexdigest()),indent=2),encoding='utf-8')
    print('Generated',len(x)/RATE,'seconds')
def analyze():
    x,r=sf.read(ROOT/'reference/dynamics.wav',always_2d=True);segs=json.loads((ROOT/'reference/dynamics.json').read_text())['segments'];rows=[]
    for p in sorted((ROOT/'captures').glob('dynamics-*.wav')):
        y,yr=sf.read(p,always_2d=True);assert yr==r
        # Sync alignment has sinusoidal cycle ambiguity. Restrict lag to expected
        # capture offset and report it; steady-state fits are phase invariant.
        s=next(s for s in segs if s['name']=='sync');a=s['start'];n=s['frames'];template=x[a:a+n,0]
        c=signal.correlate(y[:a+n+r//4,0],template,mode='valid',method='fft');lag=int(np.argmax(np.abs(c)))-a
        for i,s in enumerate(segs):
            if s['name']!='tone':continue
            start=s['start']+lag;end=start+s['frames'];full=y[start:end]
            row=dict(capture=p.stem,segment=i,frequency=s['frequency'],input_peak_dbfs=s['peak_dbfs'],lag_samples=lag,windows=[])
            for offset in [.1,.5,1,1.5]:
                v=full[round(offset*r):round((offset+.2)*r)];t=np.arange(len(v))/r;f=s['frequency']
                basis=np.column_stack([fun(2*np.pi*f*h*t) for h in range(1,9) for fun in [np.sin,np.cos]]+[np.ones(len(t))]);coeff=np.linalg.lstsq(basis,v,rcond=None)[0]
                amps=np.hypot(coeff[0::2][:8],coeff[1::2][:8]);fund=amps[0]
                row['windows'].append(dict(offset_s=offset,fundamental_peak_dbfs=(20*np.log10(np.maximum(fund,1e-30))).tolist(),gain_db=(20*np.log10(np.maximum(fund,1e-30))-s['peak_dbfs']).tolist(),harmonics_2_to_8_relative_db=(20*np.log10(np.maximum(np.linalg.norm(amps[1:],axis=0)/np.maximum(fund,1e-30),1e-30))).tolist()))
            rows.append(row)
    (ROOT/'analysis/dynamics.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
    for row in rows:print(row['capture'],row['frequency'],row['input_peak_dbfs'],'gain windows',np.round([v['gain_db'][0] for v in row['windows']],3),'harmonics',round(row['windows'][-1]['harmonics_2_to_8_relative_db'][0],2))
if __name__=='__main__':
    import sys
    build() if 'build' in sys.argv else analyze()
