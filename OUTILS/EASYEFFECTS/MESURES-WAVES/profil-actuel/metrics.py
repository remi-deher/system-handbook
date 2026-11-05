"""Offline electrical metrics; none of these are acoustic SPL or intelligibility."""
import numpy as np
from scipy import signal
import pyloudnorm as pyln
RATE=48000
def db(v):return 20*np.log10(np.maximum(np.abs(v),1e-30))
def rms(v):return np.sqrt(np.mean(np.asarray(v,dtype='float64')**2,axis=0))
def lufs(x):
    if len(x)<19200 or np.max(abs(x))<1e-12:return None
    value=pyln.Meter(RATE,filter_class='DeMan').integrated_loudness(x.astype('float64'))
    return float(value) if np.isfinite(value) else None
def programme(x,with_tp=False):
    x=x.astype('float64');pk=float(np.max(abs(x)));r=float(np.sqrt(np.mean(x*x)))
    mid=(x[:,0]+x[:,1])/2;side=(x[:,0]-x[:,1])/2
    f,p=signal.welch(x,fs=RATE,nperseg=min(4096,len(x)),axis=0)
    bands={}
    for name,lo,hi in [('bass',40,150),('low_mid',150,500),('mid',500,2000),('presence',2000,6000),('treble',6000,20000)]:
        mask=(f>=lo)&(f<hi);power=float(np.mean(np.sum(p[mask],axis=0)*(f[1]-f[0])))
        bands[name]=float(10*np.log10(max(1e-30,power)))
    out=dict(sample_peak_dbfs=float(db(pk)),rms_dbfs=float(db(r)),crest_db=float(db(pk/max(r,1e-30))),lufs=lufs(x),
             mid_rms_dbfs=float(db(rms(mid))),side_rms_dbfs=float(db(rms(side))),
             stereo_correlation=float(np.corrcoef(x.T)[0,1]) if np.all(rms(x)>1e-12) else None,
             bands_power_dbfs=bands,presence_minus_low_mid_db=bands['presence']-bands['low_mid'])
    if with_tp:
        out['estimated_true_peak_4x_dbfs']=float(db(max(np.max(abs(signal.resample_poly(x[:,ch],4,1,window=('kaiser',8.6)))) for ch in [0,1])))
    return out
def harmonic_fit(y,frequency,orders=8):
    n=min(orders,int(20000//frequency));t=np.arange(len(y))/RATE
    basis=np.column_stack([fun(2*np.pi*frequency*h*t) for h in range(1,n+1) for fun in [np.sin,np.cos]]+[np.ones(len(t))])
    coef=np.linalg.lstsq(basis,y.astype('float64'),rcond=None)[0]
    amps=np.hypot(coef[:2*n:2],coef[1:2*n:2]);res=y-basis@coef
    return dict(fundamental_peak_dbfs=db(amps[0]).tolist(),harmonics_peak_dbfs=db(amps).tolist(),
                harmonics_relative_db=db(np.linalg.norm(amps[1:],axis=0)/np.maximum(amps[0],1e-30)).tolist(),
                residual_rms_dbfs=db(rms(res)).tolist())
def imd(y,kind,f1,f2):
    products=[f2-f1,f2+f1,f2-2*f1,f2+2*f1] if kind=='smpte' else [abs(f2-f1),2*abs(f2-f1),2*f1-f2,2*f2-f1]
    products=sorted(set(f for f in products if 0<f<22000 and f not in [f1,f2]));freqs=[f1,f2]+products
    t=np.arange(len(y))/RATE;basis=np.column_stack([fun(2*np.pi*f*t) for f in freqs for fun in [np.sin,np.cos]]+[np.ones(len(t))])
    coef=np.linalg.lstsq(basis,y.astype('float64'),rcond=None)[0];amps=np.hypot(coef[:-1:2],coef[1::2])
    return dict(frequencies=freqs,components_peak_dbfs=db(amps).tolist(),product_to_second_carrier_db=db(np.linalg.norm(amps[2:],axis=0)/np.maximum(amps[1],1e-30)).tolist(),definition='Selected sidebands/products, not certified normative SMPTE/CCIF IMD')
def envelopes(y,frequency):
    n=1920;hop=960;orders=min(8,20000//frequency);t=np.arange(n)/RATE
    basis=np.column_stack([fun(2*np.pi*frequency*h*t) for h in range(1,orders+1) for fun in [np.sin,np.cos]]+[np.ones(n)])
    inverse=np.linalg.pinv(basis);rows=[]
    for off in range(0,len(y)-n+1,hop):
        frame=y[off:off+n];coeff=inverse@frame;amp=np.hypot(coeff[0],coeff[1])
        residual=frame-basis@coeff
        relative=db(rms(residual)/np.maximum(rms(frame),1e-30))
        rows.append((float((off+n/2)/RATE),*db(amp).tolist(),*relative.tolist()))
    return rows
def apparent_matrices(x,y,segments):
    sweeps=[s for s in segments if s['name']=='sweep'];levels=sorted(set(s['input_level'] for s in sweeps))
    nt=1
    while nt<max(s['frames'] for s in sweeps)+round(.15*RATE):nt*=2
    freq=np.fft.rfftfreq(nt,1/RATE);H=np.zeros((len(levels),2,2,len(freq)),complex)
    for s in sweeps:
        # The short probe has only 100 ms between L/R sweeps. Never include
        # the next channel's excitation in the preceding transfer estimate.
        tail=.08 if s['frames']<RATE else .15
        a=s['start'];b=a+s['frames']+round(tail*RATE);ch=s['input_channel'];i=levels.index(s['input_level'])
        xx=np.fft.rfft(x[a:b,ch],n=nt);yy=np.fft.rfft(y[a:b],n=nt,axis=0)
        h=yy*np.conj(xx[:,None])/(abs(xx[:,None])**2+1e-24)
        H[i,:,ch,:]=h.T
    # Stay inside both sweep ranges; spectral division outside the excited
    # band would magnify leakage and bias the adaptive-volume detector.
    centers=80*2**(np.arange(0,94)/12);centers=centers[centers<=16000];rows=[]
    for i,lev in enumerate(levels):
        for ch in [0,1]:
            for out in [0,1]:
                ratio=H[i,out,ch]/(H[i,ch,ch]+1e-30)
                for center in centers:
                    mask=(freq>=center/2**(1/24))&(freq<center*2**(1/24))
                    rows.append(dict(input_level=lev,input_channel=ch,output_channel=out,Hz=float(center),magnitude_db=float(db(np.sqrt(np.mean(abs(H[i,out,ch,mask])**2)))),
                                cross_to_direct_db=float(db(np.sqrt(np.mean(abs(ratio[mask])**2)))),cross_to_direct_phase_deg=float(np.angle(np.mean(ratio[mask]))*180/np.pi)))
    return freq,levels,H,rows
