import ctypes
ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
import datetime,hashlib,importlib.util,json,pathlib,time,sys
import numpy as np
import soundfile as sf
from scipy import signal
import comtypes.client
from PIL import ImageGrab
ROOT=pathlib.Path(__file__).resolve().parent
PREVIOUS=ROOT.parent/'Mesures-Windows-WASAPI'
spec=importlib.util.spec_from_file_location('acquisition',ROOT/'acquisition.py')
acq=importlib.util.module_from_spec(spec);spec.loader.exec_module(acq);acq.ROOT=ROOT
UI=comtypes.client.GetModule('UIAutomationCore.dll')
IDS=dict(bass='cmdMaxxBass',details='cmdDetails',width='cmdWidth',power='cmdPower',midnight='cmdMidnight')
class Controls:
    def __init__(self):
        self.a=comtypes.client.CreateObject(UI.CUIAutomation,interface=UI.IUIAutomation)
        self.w=self.a.GetRootElement().FindFirst(2,self.a.CreatePropertyCondition(30005,'MaxxAudioPro'))
        if not self.w:raise RuntimeError('Waves window missing')
    def element(self,key):return self.w.FindFirst(4,self.a.CreatePropertyCondition(30011,IDS.get(key,key)))
    def state(self):
        out={k:self.element(k).CurrentItemStatus for k in IDS}
        for k in ['EQ31','EQ63','EQ125','EQ250','EQ500','EQ1K','EQ2K','EQ4K','EQ8K','EQ16K']:
            out[k]=self.element(k).CurrentItemStatus
        return out
    def snapshot(self,label):
        st=self.state();r=self.w.CurrentBoundingRectangle
        ImageGrab.grab(bbox=(r.left,r.top,r.right,r.bottom)).save(ROOT/'states'/(label+'.png'))
        acq.dump(ROOT/'states'/(label+'.json'),dict(time=datetime.datetime.now().astimezone().isoformat(),controls=st))
        return st
    def percent(self,key):return int(self.element(key).CurrentItemStatus.replace('%','').strip())
    def drag(self,key,delta):
        p=self.element(key);r=p.CurrentBoundingRectangle
        ctypes.windll.user32.SetForegroundWindow(self.w.CurrentNativeWindowHandle)
        ctypes.windll.user32.SetCursorPos((r.left+r.right)//2,r.bottom-40)
        ctypes.windll.user32.mouse_event(2,0,0,0,0);time.sleep(.08)
        # Inject actual mouse movement packets; SetCursorPos alone may not
        # produce manipulation events in the UWP knob.
        direction=1 if delta>0 else -1
        for _ in range(abs(delta)):
            ctypes.windll.user32.mouse_event(1,0,ctypes.c_uint32(-direction),0,0);time.sleep(.005)
        ctypes.windll.user32.mouse_event(4,0,0,0,0);time.sleep(.15)
    def set_percent(self,key,target):
        stagnant=0
        for _ in range(45):
            current=self.percent(key)
            if current==target:return
            diff=target-current
            self.drag(key,int(np.sign(diff)*min(50,max(3,abs(diff)*2+stagnant))))
            stagnant=stagnant+1 if self.percent(key)==current else 0
            if stagnant>5:raise RuntimeError(f'Knob {key} did not react to injected drag')
        raise RuntimeError(f'Unable to reach exact {key}={target}; actual {self.percent(key)}')
    def power(self,on):
        expected='On' if on else 'Off'
        if self.element('power').CurrentItemStatus==expected:return
        r=self.element('power').CurrentBoundingRectangle
        time.sleep(.6);ctypes.windll.user32.SetCursorPos((r.left+r.right)//2,(r.top+r.bottom)//2)
        ctypes.windll.user32.mouse_event(2,0,0,0,0);ctypes.windll.user32.mouse_event(4,0,0,0,0);time.sleep(.7)
        if self.element('power').CurrentItemStatus!=expected:raise RuntimeError('Power mismatch')

def generate():
    rate=48000;rng=np.random.default_rng(74402026);parts=[];segments=[];pos=0
    def add(name,x,**meta):
        nonlocal pos
        parts.append(x);segments.append(dict(name=name,start=pos,frames=len(x),**meta));pos+=len(x)
    def silence(s):return np.zeros((round(rate*s),2))
    def fade(x):
        e=np.ones(len(x));n=min(480,len(x)//2);e[:n]=np.linspace(0,1,n);e[-n:]=np.linspace(1,0,n)
        return x*e[:,None] if x.ndim==2 else x*e
    add('lead',silence(1))
    t=np.arange(12000)/rate;s=fade(np.sin(2*np.pi*1901*t))*10**(-54/20)
    add('sync',np.column_stack([s,s]));add('gap',silence(.25))
    for level in [-60,-48,-36]:
        amp=10**(level/20)
        for ch in [0,1]:
            t=np.arange(72000)/rate;s=fade(signal.chirp(t,65,t[-1],18000,method='logarithmic'))*amp;x=np.zeros((len(t),2));x[:,ch]=s
            add('sweep',x,level_dbfs=level,input_channel=ch);add('gap',silence(.2))
        for f in [80,125,250,997,6000]:
            t=np.arange(28800)/rate;s=fade(np.sin(2*np.pi*f*t))*amp
            add('tone',np.column_stack([s,s]),level_dbfs=level,frequency=f);add('gap',silence(.15))
        for mode in ['independent','mono','side']:
            n=rng.standard_normal((48000,2));
            if mode=='mono':n[:,1]=n[:,0]
            if mode=='side':n[:,1]=-n[:,0]
            n=fade(n/np.max(np.abs(n)))*amp
            add('noise',n,level_dbfs=level,mode=mode);add('gap',silence(.15))
    add('tail',silence(1));x=np.concatenate(parts).astype('float32');p=ROOT/'reference/isolation.wav';sf.write(p,x,rate,subtype='FLOAT')
    acq.dump(p.with_suffix('.json'),dict(rate=rate,frames=len(x),seconds=len(x)/rate,peak_dbfs=float(20*np.log10(np.max(np.abs(x)))),seed=74402026,segments=segments,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    print('Generated',len(x)/rate,'seconds',flush=True)
def trial(label,levels,volume=.1,on=True):
    ui=Controls();ui.power(True)
    for key in ['bass','details','width']:ui.set_percent(key,levels.get(key,0))
    ui.power(on);st=ui.snapshot(label)
    expected={key:f'{levels.get(key,0)} %' for key in ['bass','details','width']}
    if any(st[k]!=v for k,v in expected.items()):raise RuntimeError('Pre-capture state mismatch')
    print('START',label,st,'volume',volume,flush=True)
    acq.capture(label,json.dumps(st),volume,'isolation.wav',True)
    after=ui.state()
    if after!=st:raise RuntimeError('UI changed during capture')
    mp=ROOT/'captures'/(label+'.json');meta=json.loads(mp.read_text());meta.update(ui_state_before=st,ui_state_after=after,effect_levels=levels,ui_evidence=f'states/{label}.png',zero_percent_is_disable_hypothesis=True)
    acq.dump(mp,meta)
    print('DONE',label,flush=True)

if __name__=='__main__':
    cmd=sys.argv[1]
    if cmd=='generate':generate()
    elif cmd=='inventory':acq.inventory();Controls().snapshot('initial-zero-confirmed')
    elif cmd=='baseline':trial('baseline-zero-first',dict(bass=0,details=0,width=0))
    elif cmd=='probe':
        c=Controls();print('before',c.state());c.drag('bass',10);print('after',c.state())
    elif cmd=='trial':trial(sys.argv[2],json.loads(sys.argv[3]),float(sys.argv[4]) if len(sys.argv)>4 else .1,not '--off' in sys.argv)
