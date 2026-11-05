"""Local shared-WASAPI tests. Never opens a physical capture device."""
import argparse, datetime, hashlib, importlib.metadata, json, pathlib, platform, sys, time
import numpy as np
import pyaudiowpatch as pa
from pycaw.pycaw import AudioUtilities

ROOT = pathlib.Path(__file__).resolve().parent
def dump(path, obj):
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str), encoding='utf-8')
def endpoint():
    d = AudioUtilities.GetSpeakers()
    if d is None or 'Realtek' not in d.FriendlyName:
        raise RuntimeError('Default endpoint is not Realtek: no playback/capture allowed')
    return d
def sessions():
    return [dict(pid=s.ProcessId, process=s.Process.name() if s.Process else 'System',
                 state=s.State, mute=s.SimpleAudioVolume.GetMute(),
                 volume=s.SimpleAudioVolume.GetMasterVolume()) for s in AudioUtilities.GetAllSessions()]
def inventory():
    d=endpoint(); v=d.EndpointVolume
    with pa.PyAudio() as p:
        host=p.get_host_api_info_by_type(pa.paWASAPI)
        devices=list(p.get_device_info_generator_by_host_api(host_api_index=host['index']))
        out=p.get_device_info_by_index(host['defaultOutputDevice'])
        loop=p.get_wasapi_loopback_analogue_by_dict(out)
    inv=dict(time=datetime.datetime.now().astimezone().isoformat(), python=sys.version,
             windows=platform.platform(), endpoint_id=d.id, endpoint_name=d.FriendlyName,
             volume_scalar=v.GetMasterVolumeLevelScalar(),volume_db=v.GetMasterVolumeLevel(),
             mute=v.GetMute(), volume_range=v.GetVolumeRange(), sessions=sessions(),
             devices=devices, output=out, loopback=loop,
             packages={n:importlib.metadata.version(n) for n in ['numpy','scipy','soundfile','PyAudioWPatch','pycaw','pywinauto']})
    dump(ROOT/'inventory-initial.json',inv)
    print(json.dumps(inv,indent=2,ensure_ascii=False,default=str))
def generate():
    import soundfile as sf
    from scipy.signal import chirp
    inv=json.loads((ROOT/'inventory-initial.json').read_text(encoding='utf-8'))
    rate=int(inv['output']['defaultSampleRate']); rng=np.random.default_rng(7440)
    parts=[]; markers=[]; pos=0
    def add(name,x):
        nonlocal pos
        parts.append(np.asarray(x,dtype=np.float32));markers.append(dict(name=name,start=pos,frames=len(x)));pos+=len(x)
    def silence(sec): return np.zeros((round(sec*rate),2))
    def fade(x):
        n=min(round(.02*rate),len(x)//2); env=np.ones(len(x)); env[:n]=np.linspace(0,1,n);env[-n:]=np.linspace(1,0,n)
        return x*env
    add('lead_silence',silence(1))
    t=np.arange(round(.25*rate))/rate
    sync=fade(np.sin(2*np.pi*1901*t))*10**(-36/20)
    add('sync',np.column_stack([sync,sync]));add('gap',silence(.4))
    t=np.arange(round(2*rate))/rate
    sweep=fade(chirp(t,80,t[-1],18000,method='logarithmic'))*10**(-30/20)
    add('sweep_left',np.column_stack([sweep,np.zeros(len(t))]));add('gap',silence(.5))
    add('sweep_right',np.column_stack([np.zeros(len(t)),sweep]));add('gap',silence(.5))
    noise=rng.standard_normal((rate*2,2));noise/=np.max(np.abs(noise)); noise*=10**(-30/20)
    noise[:960]*=np.linspace(0,1,960)[:,None];noise[-960:]*=np.linspace(1,0,960)[:,None]
    add('seeded_noise',noise);add('gap',silence(.5))
    t=np.arange(rate)/rate; tone=fade(np.sin(2*np.pi*997*t))
    for db in [-48,-42,-36,-30]:
        add('tone_'+str(db),np.column_stack([tone,tone])*10**(db/20));add('gap',silence(.4))
    add('tail_silence',silence(1))
    x=np.concatenate(parts); path=ROOT/'reference'/'pilot.wav';sf.write(path,x,rate,subtype='FLOAT')
    dump(ROOT/'reference'/'pilot.json',dict(rate=rate,channels=2,frames=len(x),seconds=len(x)/rate,peak_dbfs=float(20*np.log10(np.max(np.abs(x)))),seed=7440,segments=markers,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    print('Generated',path, len(x)/rate,'seconds, peak',20*np.log10(np.max(np.abs(x))))
def capture(label, state, volume, source_name='pilot.wav', muted=False):
    import soundfile as sf
    d=endpoint();v=d.EndpointVolume; original=dict(scalar=v.GetMasterVolumeLevelScalar(),mute=v.GetMute())
    inv=json.loads((ROOT/'inventory-initial.json').read_text(encoding='utf-8'))
    if d.id!=inv['endpoint_id']:raise RuntimeError('Endpoint changed')
    active=[s for s in sessions() if s['state']==1 and not s['mute'] and s['pid']!=__import__('os').getpid()]
    if active:raise RuntimeError('Other active audio sessions: '+str(active))
    if not 0<=volume<=.15:raise ValueError('Maximum trial volume scalar 0.15')
    if pathlib.Path(source_name).name!=source_name:raise ValueError('Source must be a reference basename')
    source=ROOT/'reference'/source_name;x,rate=sf.read(source,dtype='float32',always_2d=True)
    if np.max(np.abs(x))>10**(-30/20)+1e-7:raise RuntimeError('Source exceeds authorized trial peak')
    chunks=[];events=[]; path=ROOT/'captures'/(label+'.wav')
    if path.exists():raise FileExistsError(path)
    start=datetime.datetime.now().astimezone().isoformat()
    def cb(data,n,info,status):
        chunks.append(data)
        if status:events.append(dict(status=status,time=info,frames=n))
        return (None,pa.paContinue)
    try:
        v.SetMasterVolumeLevelScalar(volume,None);v.SetMute(int(muted),None)
        with pa.PyAudio() as p:
            host=p.get_host_api_info_by_type(pa.paWASAPI)
            out=p.get_device_info_by_index(host['defaultOutputDevice']);loop=p.get_wasapi_loopback_analogue_by_dict(out)
            if 'Realtek' not in out['name'] or not loop['isLoopbackDevice']:raise RuntimeError('Invalid render/loopback device')
            if int(out['defaultSampleRate'])!=rate or loop['maxInputChannels']!=2:raise RuntimeError('Native format mismatch')
            with p.open(format=pa.paFloat32,channels=2,rate=rate,input=True,input_device_index=loop['index'],frames_per_buffer=512,stream_callback=cb) as rec:
                with p.open(format=pa.paFloat32,channels=2,rate=rate,output=True,output_device_index=out['index'],frames_per_buffer=512) as play:
                    for off in range(0,len(x),512):play.write(x[off:off+512].tobytes(),exception_on_underflow=True)
                time.sleep(.25)
        if not chunks:raise RuntimeError('No loopback packets')
        y=np.frombuffer(b''.join(chunks),dtype=np.float32).reshape(-1,2).copy()
        sf.write(path,y,rate,subtype='FLOAT')
        meta=dict(label=label,time=start,waves_state=state,waves_state_verification='See separately saved UI screenshot',endpoint_id=d.id,endpoint_name=d.FriendlyName,
                  source=str(source.relative_to(ROOT)),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),capture_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                  output=out,loopback=loop,rate=rate,channels=2,frames=len(y),volume_scalar=volume,volume_db=v.GetMasterVolumeLevel(),mute=v.GetMute(),
                  original_volume=original,peak_dbfs=float(20*np.log10(max(1e-30,float(np.max(np.abs(y)))))),rms_dbfs=float(20*np.log10(max(1e-30,float(np.sqrt(np.mean(y*y)))))),clipped_samples=int(np.sum(np.abs(y)>=1)),callback_events=events,
                  capture_method='PyAudioWPatch WASAPI render-endpoint loopback / shared output; no RAW/exclusive flags; float32',settings_restored=False)
    finally:
        v.SetMasterVolumeLevelScalar(original['scalar'],None);v.SetMute(original['mute'],None)
    meta['settings_restored']=True;dump(path.with_suffix('.json'),meta);print(json.dumps(meta,indent=2,ensure_ascii=False))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=['inventory','generate','capture']);ap.add_argument('--label');ap.add_argument('--state');ap.add_argument('--volume',type=float,default=.1);ap.add_argument('--source',default='pilot.wav');ap.add_argument('--muted',action='store_true');a=ap.parse_args()
    if a.command=='inventory':inventory()
    elif a.command=='generate':generate()
    else:
        if not a.label or not a.state:ap.error('--label and --state required')
        capture(a.label,a.state,a.volume,a.source,a.muted)
