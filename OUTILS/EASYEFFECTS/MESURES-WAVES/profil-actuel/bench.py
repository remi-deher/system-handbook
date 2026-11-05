import ctypes
ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
ctypes.windll.user32.GetForegroundWindow.restype=ctypes.c_void_p
import sys,pathlib,json,datetime,hashlib,time,importlib.metadata,platform
ROOT=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'Mesures-Effets-Isoles'))
import campaign as ui_module
ui_module.ROOT=ROOT
from campaign import Controls
import numpy as np
import soundfile as sf
import pyaudiowpatch as pa
from pycaw.pycaw import AudioUtilities
def dump(path,v):path.write_text(json.dumps(v,indent=2,ensure_ascii=False,default=str),encoding='utf-8')
def stamp():return datetime.datetime.now().astimezone().isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def endpoint():
    d=AudioUtilities.GetSpeakers()
    if d is None or 'Realtek' not in d.FriendlyName:raise RuntimeError('Physical Realtek default output required')
    return d
class LiveControls(Controls):
    # UWP can recreate its outer frame without changing any audio settings.
    # Do not keep the initial AutomationElement for a long measurement run.
    def refresh(self):
        self.w=self.a.GetRootElement().FindFirst(2,self.a.CreatePropertyCondition(30005,'MaxxAudioPro'))
        if not self.w:raise RuntimeError('Waves frame unavailable')
    def state(self):
        last=None
        for attempt in range(8):
            try:self.refresh();return super().state()
            except (ValueError,RuntimeError) as e:
                last=e
                if attempt in [0,3]:
                    try:
                        self.refresh();hwnd=self.w.CurrentNativeWindowHandle
                        if ctypes.windll.user32.IsIconic(hwnd):ctypes.windll.user32.ShowWindow(hwnd,9)
                        ctypes.windll.user32.SetForegroundWindow(hwnd)
                        # Navigate only: do not alter preset, power or knobs.
                        group=self.w.FindFirst(4,self.a.CreatePropertyCondition(30011,'cmdMenuAudio'))
                        if group:
                            button=group.FindFirst(4,self.a.CreatePropertyCondition(30003,50000))
                            if button:button.GetCurrentPattern(10000).QueryInterface(ui_module.UI.IUIAutomationInvokePattern).Invoke()
                    except Exception:pass
                time.sleep(.5)
        raise RuntimeError('Cannot verify current Waves controls') from last
    def foreground(self):
        self.refresh();hwnd=self.w.CurrentNativeWindowHandle
        if ctypes.windll.user32.IsIconic(hwnd):ctypes.windll.user32.ShowWindow(hwnd,9)
        ctypes.windll.user32.SetForegroundWindow(hwnd);time.sleep(.1)
        if ctypes.windll.user32.GetForegroundWindow()!=hwnd:raise RuntimeError('Cannot safely foreground Waves controls')
    def power(self,on):
        state=self.state()
        if state['power']!=('On' if on else 'Off'):self.foreground()
        return super().power(on)
    def snapshot(self,label):self.state();self.foreground();return super().snapshot(label)
def inventory():
    d=endpoint();v=d.EndpointVolume;c=Controls();state=c.snapshot('initial-profile')
    with pa.PyAudio() as p:
        host=p.get_host_api_info_by_type(pa.paWASAPI);out=p.get_device_info_by_index(host['defaultOutputDevice']);loop=p.get_wasapi_loopback_analogue_by_dict(out)
    from comtypes import CLSCTX_ALL
    from pycaw.api.audioclient import IAudioClient
    client=d._dev.Activate(IAudioClient._iid_,CLSCTX_ALL,None).QueryInterface(IAudioClient);fmt=client.GetMixFormat();f=fmt.contents
    mix={n:getattr(f,n) for n,_ in f._fields_};mix['raw_hex']=ctypes.string_at(fmt,18+f.cbSize).hex();ctypes.windll.ole32.CoTaskMemFree(fmt)
    info=dict(time=stamp(),windows=platform.platform(),python=sys.version,endpoint_id=d.id,endpoint_name=d.FriendlyName,
              volume_scalar=v.GetMasterVolumeLevelScalar(),volume_db=v.GetMasterVolumeLevel(),mute=v.GetMute(),controls=state,mix_format=mix,output=out,loopback=loop,
              packages={n:importlib.metadata.version(n) for n in ['numpy','scipy','soundfile','PyAudioWPatch','pycaw','pyloudnorm','matplotlib']})
    if (ROOT/'inventory-initial.json').exists():raise FileExistsError('Initial inventory must not be overwritten')
    dump(ROOT/'inventory-initial.json',info);print(json.dumps(info,indent=2),flush=True)
class Session:
    def __init__(self):
        self.initial=json.loads((ROOT/'inventory-initial.json').read_text(encoding='utf-8'))
        self.d=endpoint();self.v=self.d.EndpointVolume;self.ui=LiveControls();self.cache={}
        if self.d.id!=self.initial['endpoint_id']:raise RuntimeError('Endpoint changed')
    def __enter__(self):
        if self.ui.state()!=self.initial['controls']:raise RuntimeError('Profile differs from initial snapshot')
        self.v.SetMute(1,None)
        if not self.v.GetMute():raise RuntimeError('Mute failed')
        return self
    def __exit__(self,*exc):
        try:self.ui.power(self.initial['controls']['power']=='On')
        finally:
            self.v.SetMasterVolumeLevelScalar(self.initial['volume_scalar'],None);self.v.SetMute(self.initial['mute'],None)
        state=self.ui.state()
        restored=dict(time=stamp(),controls=state,volume_scalar=self.v.GetMasterVolumeLevelScalar(),mute=self.v.GetMute(),endpoint_id=self.d.id,
                      controls_restored=state==self.initial['controls'],volume_restored=abs(self.v.GetMasterVolumeLevelScalar()-self.initial['volume_scalar'])<1e-6,mute_restored=self.v.GetMute()==self.initial['mute'])
        dump(ROOT/'restoration.json',restored);self.ui.snapshot('restored-profile');print('RESTORED',restored,flush=True)
    def capture(self,label,source_name,percent,enabled=True,category=None):
        path=ROOT/'captures'/(label+'.wav');mp=path.with_suffix('.json')
        if path.exists():raise FileExistsError(path)
        if not 0<=percent<=100:raise ValueError(percent)
        if endpoint().id!=self.initial['endpoint_id']:raise RuntimeError('Default physical endpoint changed')
        self.ui.power(enabled);expected=dict(self.initial['controls'],power='On' if enabled else 'Off')
        before=self.ui.state()
        if before!=expected:raise RuntimeError('Unexpected Waves profile state')
        active=[(s.ProcessId,s.Process.name() if s.Process else 'System') for s in AudioUtilities.GetAllSessions() if s.State==1 and not s.SimpleAudioVolume.GetMute() and s.ProcessId!=__import__('os').getpid()]
        if active:raise RuntimeError('Other active audio sessions: '+str(active))
        source=ROOT/'reference'/source_name
        if source_name not in self.cache:
            x,rate=sf.read(source,dtype='float32',always_2d=True)
            if rate!=48000 or x.shape[1]!=2 or not np.isfinite(x).all() or np.max(abs(x))>.9:raise RuntimeError('Invalid source format/peak')
            self.cache[source_name]=(x,rate,sha(source))
        x,rate,source_hash=self.cache[source_name]
        if sha(source)!=source_hash:raise RuntimeError('Source changed during campaign')
        # High digital levels and endpoint levels are allowed only under mute.
        self.v.SetMute(1,None)
        if not self.v.GetMute():raise RuntimeError('Mute not confirmed')
        self.v.SetMasterVolumeLevelScalar(percent/100,None);time.sleep(.15)
        actual=self.v.GetMasterVolumeLevelScalar();vol_db=self.v.GetMasterVolumeLevel()
        if abs(actual-percent/100)>.005 or not self.v.GetMute():raise RuntimeError('Volume/mute mismatch')
        chunks=[];events=[];start=stamp();t0=time.perf_counter()
        def callback(data,n,info,status):
            chunks.append(data)
            if status:events.append(dict(status=status,frames=n,time=info))
            return (None,pa.paContinue)
        print('START',label,'volume',percent,'duration',len(x)/rate,flush=True)
        renderer_info=dict(renderer='PyAudioWPatch shared WASAPI',category='PortAudio default, not explicitly selected')
        def safety_check():
            if not self.v.GetMute():raise RuntimeError('Mute was removed: playback aborted')
            if abs(self.v.GetMasterVolumeLevelScalar()-actual)>.005:raise RuntimeError('Volume changed during capture')
        with pa.PyAudio() as p:
            host=p.get_host_api_info_by_type(pa.paWASAPI);out=p.get_device_info_by_index(host['defaultOutputDevice']);loop=p.get_wasapi_loopback_analogue_by_dict(out)
            if out['name']!=self.initial['output']['name'] or loop['name']!=self.initial['loopback']['name'] or not loop['isLoopbackDevice'] or loop['maxInputChannels']!=2 or int(loop['defaultSampleRate'])!=rate:raise RuntimeError('Incorrect or changed physical render/loopback endpoint')
            with p.open(format=pa.paFloat32,channels=2,rate=rate,input=True,input_device_index=loop['index'],frames_per_buffer=512,stream_callback=callback) as rec:
                if category is None:
                    with p.open(format=pa.paFloat32,channels=2,rate=rate,output=True,output_device_index=out['index'],frames_per_buffer=512) as play:
                        for off in range(0,len(x),512):
                            safety_check();play.write(x[off:off+512].tobytes(),exception_on_underflow=True)
                else:
                    from native_renderer import play as native_play
                    renderer_info=native_play(self.d,x,rate,category,safety_check)
                time.sleep(.15)
        if not chunks:raise RuntimeError('No captured packets')
        y=np.frombuffer(b''.join(chunks),dtype='float32').reshape(-1,2).copy();after=self.ui.state()
        sf.write(path,y,rate,subtype='FLOAT')
        meta=dict(label=label,time=start,elapsed_seconds=time.perf_counter()-t0,source=source.relative_to(ROOT).as_posix(),source_sha256=source_hash,capture_sha256=sha(path),
                  controls_before=before,controls_after=after,profile_unchanged=after==expected,endpoint_id=self.d.id,endpoint_name=self.d.FriendlyName,
                  volume_percent_requested=percent,volume_scalar_actual=actual,volume_db=vol_db,mute_verified=True,mute_monitored_each_512_frames=True,
                  output=out,loopback=loop,rate=rate,channels=2,source_frames=len(x),captured_frames=len(y),callback_events=events,
                  finite=bool(np.isfinite(y).all()),sample_peak_dbfs=float(20*np.log10(max(1e-30,float(np.max(abs(y)))))),
                  samples_at_or_above_full_scale=int(np.sum(abs(y)>=1)),source_peak_dbfs=float(20*np.log10(np.max(abs(x)))),
                  method='WASAPI shared physical Realtek render-endpoint loopback; float32; no RAW/exclusive; no microphone',renderer=renderer_info,
                  clipping_interpretation='Near-full-scale source probes intentionally characterize limiting; clipping is measured, not silently rejected')
        meta['valid_acquisition']=meta['profile_unchanged'] and meta['finite'] and not events and renderer_info.get('detected_empty_buffer_events',0)==0
        dump(mp,meta)
        print('DONE',label,'peak',round(meta['sample_peak_dbfs'],3),'fullscale',meta['samples_at_or_above_full_scale'],'events',events,flush=True)
        self.v.SetMasterVolumeLevelScalar(self.initial['volume_scalar'],None)
        if not meta['valid_acquisition']:raise RuntimeError('Acquisition anomaly; raw data retained')
        return meta
def run_scan():
    plan=[('probe-initial-a',round(json.loads((ROOT/'inventory-initial.json').read_text())['volume_scalar']*100)),('probe-initial-b',round(json.loads((ROOT/'inventory-initial.json').read_text())['volume_scalar']*100))]
    plan += [(f'probe-v{v:03d}',v) for v in range(101)]
    plan += [(f'probe-return-v{v:03d}',v) for v in [100,75,50,25,0,28]]
    dump(ROOT/'plan-scan.json',dict(scope='Every integer Windows endpoint volume 0..100 inclusive plus repeats; fixed current Waves profile',trials=[dict(label=n,volume_percent=v) for n,v in plan]))
    with Session() as s:
        for i,(label,v) in enumerate(plan):
            p=ROOT/'captures'/(label+'.json')
            if p.exists() and json.loads(p.read_text()).get('valid_acquisition'):
                print('SKIP',label,flush=True);continue
            print('SCAN',i+1,'/',len(plan),flush=True);s.capture(label,'volume-probe.wav',v)
if __name__=='__main__':
    if sys.argv[1]=='inventory':inventory()
    elif sys.argv[1]=='scan':run_scan()

