"""Deterministic stimuli, including near-programme levels. Playback MUTED only."""
import hashlib,json,pathlib
import numpy as np
import soundfile as sf
from scipy import signal
ROOT=pathlib.Path(__file__).resolve().parent;RATE=48000
def save_json(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False),encoding='utf-8')
def normalize(x,peak):return x*(10**(peak/20)/max(1e-30,float(np.max(abs(x)))))
def fade(x,ms=10):
    n=min(round(ms*RATE/1000),len(x)//2);e=np.ones(len(x));e[:n]=np.linspace(0,1,n);e[-n:]=np.linspace(1,0,n)
    return x*e[:,None] if x.ndim==2 else x*e
def pink(rng,n):
    f=np.fft.rfftfreq(n,1/RATE);a=rng.standard_normal((len(f),2))+1j*rng.standard_normal((len(f),2));a[0]=0
    a/=np.sqrt(np.maximum(f[:,None],40));a[f<50]=0;a[f>17000]=0
    return np.fft.irfft(a,n=n,axis=0)
class Builder:
    def __init__(self,name):self.name=name;self.parts=[];self.segments=[];self.pos=0
    def add(self,name,x,**meta):
        x=np.asarray(x,dtype='float32');assert x.ndim==2 and x.shape[1]==2
        self.parts.append(x);self.segments.append(dict(name=name,start=self.pos,frames=len(x),**meta));self.pos+=len(x)
    def silence(self,seconds,name='gap'):self.add(name,np.zeros((round(seconds*RATE),2)))
    def mono(self,name,x,**meta):self.add(name,np.column_stack([x,x]),**meta)
    def write(self):
        x=np.concatenate(self.parts);p=ROOT/'reference'/(self.name+'.wav');sf.write(p,x,RATE,subtype='FLOAT')
        save_json(p.with_suffix('.json'),dict(rate=RATE,channels=2,frames=len(x),seconds=len(x)/RATE,peak_dbfs=float(20*np.log10(max(1e-30,float(np.max(abs(x)))))),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),segments=self.segments,seed=744030))
        print(self.name,len(x)/RATE,'seconds',flush=True)
def marker(b,rng):
    b.add('conditioning_pink',normalize(fade(pink(rng,RATE)), -30),exclude_from_metrics=True)
    b.silence(.15)
    t=np.arange(round(.15*RATE))/RATE;s=normalize(fade(signal.chirp(t,900,t[-1],5500,method='logarithmic')),-36)
    b.mono('sync',s);b.silence(.15)
def build_scan():
    rng=np.random.default_rng(744030);b=Builder('volume-probe');marker(b,rng)
    for ch in [0,1]:
        t=np.arange(round(.7*RATE))/RATE;s=normalize(fade(signal.chirp(t,65,t[-1],18000,method='logarithmic')),-24);x=np.zeros((len(s),2));x[:,ch]=s
        b.add('sweep',x,input_channel=ch,input_level=-24);b.silence(.1)
    n=round(.65*RATE);noise=normalize(fade(pink(rng,n)),-18);b.add('pink_stereo',noise,input_level=-18)
    for mode in ['mono','side']:
        s=normalize(fade(pink(rng,round(.45*RATE))[:,0]),-24)
        b.add('pink_'+mode,np.column_stack([s,s if mode=='mono' else -s]),input_level=-24)
    t=np.arange(round(.45*RATE))/RATE;s=normalize(fade(np.sin(2*np.pi*997*t)),-18);b.mono('tone',s,frequency=997,input_level=-18)
    b.silence(.6,'tail');b.write()
def build_deep():
    rng=np.random.default_rng(744030);b=Builder('deep-suite');marker(b,rng)
    # Full 2x2 apparent transfers at three amplitudes, with identical sweeps.
    for level in [-48,-24,-6]:
        for ch in [0,1]:
            t=np.arange(round(1.5*RATE))/RATE;s=normalize(fade(signal.chirp(t,45,t[-1],20500,method='logarithmic')),level);x=np.zeros((len(s),2));x[:,ch]=s
            b.add('sweep',x,input_channel=ch,input_level=level);b.silence(.2)
    # Three bands, eight levels. Simultaneous harmonic fits remove leakage.
    for f in [125,997,6000]:
        for level in [-60,-48,-36,-24,-18,-12,-6,-1]:
            t=np.arange(round(.65*RATE))/RATE;s=normalize(fade(np.sin(2*np.pi*f*t)),level)
            b.mono('tone',s,frequency=f,input_level=level);b.silence(.15)
    # Continuous carrier through level changes: no silence/fade at transitions.
    for f in [125,997]:
        levels=[(-42,1.5),(-6,1.5),(-42,2.0),(-18,1.0),(-42,1.0)]
        a=np.concatenate([np.full(round(d*RATE),10**(lev/20)) for lev,d in levels]);t=np.arange(len(a))/RATE
        s=np.sin(2*np.pi*f*t)*a;s=fade(s)
        b.mono('level_steps',s,frequency=f,steps=[dict(level_dbfs=lev,seconds=d) for lev,d in levels]);b.silence(.3)
    for level in [-30,-12,-3]:
        n=round(1.2*RATE);noise=normalize(fade(pink(rng,n)),level)
        b.add('pink_stereo',noise,input_level=level);b.silence(.15)
    for mode in ['mono','side','decorrelated']:
        n=round(1.5*RATE);v=pink(rng,n)
        if mode=='mono':v[:,1]=v[:,0]
        if mode=='side':v[:,1]=-v[:,0]
        if mode=='decorrelated':v[:,1]=np.roll(v[:,0],round(.0007*RATE))
        b.add('pink_'+mode,normalize(fade(v),-12),input_level=-12);b.silence(.2)
    for kind,f1,f2,ratio in [('smpte',60,7000,4),('ccif',18000,19000,1)]:
        for level in [-24,-6]:
            t=np.arange(RATE)/RATE;s=normalize(fade(ratio*np.sin(2*np.pi*f1*t)+np.sin(2*np.pi*f2*t)),level)
            b.mono('intermodulation',s,kind=kind,f1=f1,f2=f2,input_level=level);b.silence(.2)
    # Original, synthetic programme-like material, not real speech/music.
    n=6*RATE;t=np.arange(n)/RATE;v=np.zeros((n,2))
    for start in np.arange(.1,5.8,.3):
        off=int(start*RATE);m=min(round(.28*RATE),n-off);u=np.arange(m)/RATE
        kick=np.sin(2*np.pi*(50*u+18*(1-np.exp(-u*22))))*np.exp(-u*18)
        hat=rng.standard_normal(m)*np.exp(-u*90);hat=signal.sosfilt(signal.butter(3,6000,fs=RATE,btype='high',output='sos'),hat)
        pan=.8 if int(start*10)%2 else .2;v[off:off+m,0]+=kick+.25*hat*pan;v[off:off+m,1]+=kick+.25*hat*(1-pan)
    for k,f in enumerate([220,277.18,329.63,440,554.37]):
        v[:,k%2]+=.12*np.sin(2*np.pi*f*t)*(.5+.5*np.sin(2*np.pi*.7*t))
    b.add('synthetic_percussive_music',normalize(fade(v),-3),input_level=-3);b.silence(.3)
    n=5*RATE;t=np.arange(n)/RATE;f0=125+35*np.sin(2*np.pi*.7*t);phase=2*np.pi*np.cumsum(f0)/RATE
    s=sum(np.sin(k*phase)/k for k in range(1,45));formants=np.zeros(n)
    for f,q in [(650,5),(1200,8),(2500,12)]:
        bb,aa=signal.iirpeak(f,q,fs=RATE);formants+=signal.lfilter(bb,aa,s)
    env=np.maximum(0,np.sin(2*np.pi*4.1*t))**1.5*(.65+.35*np.sin(2*np.pi*.9*t))
    s=normalize(fade(formants*env),-6);b.mono('synthetic_formant_speechlike',s,input_level=-6);b.silence(.3)
    # Low crest-factor multisine and transient/high crest-factor comparison.
    t=np.arange(2*RATE)/RATE;freqs=np.geomspace(80,15000,24);v=np.zeros((len(t),2))
    for k,f in enumerate(freqs):
        v[:,0]+=np.sin(2*np.pi*f*t-np.pi*k*(k-1)/len(freqs));v[:,1]+=np.sin(2*np.pi*f*t+np.pi*k*(k-1)/len(freqs))
    b.add('multisine_dense',normalize(fade(v),-3),input_level=-3);b.silence(.3)
    n=2*RATE;v=np.zeros((n,2))
    for off in [5000,18000,40000,65000,80000]:
        z=rng.standard_normal((480,2))*np.hanning(480)[:,None];v[off:off+480]+=z
    b.add('short_transient_bursts',normalize(v,-1),input_level=-1);b.silence(.3)
    speech_path=ROOT/'reference/speech-tts-original.wav'
    if speech_path.exists():
        speech,sr=sf.read(speech_path,always_2d=True)
        if sr!=RATE:
            from math import gcd
            common=gcd(sr,RATE);speech=signal.resample_poly(speech,RATE//common,sr//common,axis=0)
        speech=np.column_stack([speech[:,0],speech[:,0]])
        for level in [-18,-3]:
            b.add('speech_tts',normalize(fade(speech),level),input_level=level,original_sha256=hashlib.sha256(speech_path.read_bytes()).hexdigest());b.silence(.3)
    b.silence(1.2,'tail');b.write()
def build_recovery():
    rng=np.random.default_rng(744030);b=Builder('recovery-suite');marker(b,rng)
    for ch in [0,1]:
        t=np.arange(round(.7*RATE))/RATE;s=normalize(fade(signal.chirp(t,65,t[-1],18000,method='logarithmic')),-36);x=np.zeros((len(s),2));x[:,ch]=s
        b.add('sweep',x,input_channel=ch,input_level=-36);b.silence(.1)
    def quiet(seconds,after):
        t=np.arange(round(seconds*RATE))/RATE;s=normalize(fade(np.sin(2*np.pi*997*t),ms=5),-36)
        b.mono('recovery_tone',s,frequency=997,input_level=-36,after_stimulus=after)
    quiet(10,'baseline')
    for f in [125,6000]:
        t=np.arange(2*RATE)/RATE;s=normalize(fade(np.sin(2*np.pi*f*t),ms=5),-6)
        b.mono('recovery_burst',s,frequency=f,input_level=-6);quiet(15,f'tone_{f}_Hz')
    b.add('recovery_burst',normalize(fade(pink(rng,3*RATE),ms=5),-6),input_level=-6)
    quiet(15,'broadband_pink');b.silence(1.2,'tail');b.write()
if __name__=='__main__':build_scan();build_deep();build_recovery()
