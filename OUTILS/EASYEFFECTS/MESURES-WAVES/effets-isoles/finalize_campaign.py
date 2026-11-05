import sys,pathlib,json,hashlib,datetime
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from campaign import ROOT,Controls,acq
import numpy as np
import soundfile as sf
from pycaw.pycaw import AudioUtilities
initial=json.loads((ROOT/'inventory-initial.json').read_text(encoding='utf-8'))
extra_labels={v['label'] for planfile in ['plan-extra-volumes.json','plan-volume-controls.json'] for v in json.loads((ROOT/planfile).read_text())['trials']}
expected=['baseline-zero-first']
for planfile in ['plan.json','plan-extra-volumes.json','plan-volume-controls.json']:
    expected += [v['label'] for v in json.loads((ROOT/planfile).read_text())['trials']]
manifest=[]
for label in expected:
    p=ROOT/'captures'/(label+'.json');m=json.loads(p.read_text())
    wave=p.with_suffix('.wav');ref=ROOT/pathlib.Path(m['source'])
    assert hashlib.sha256(wave.read_bytes()).hexdigest()==m['capture_sha256']
    assert hashlib.sha256(ref.read_bytes()).hexdigest()==m['source_sha256']
    y,r=sf.read(wave,always_2d=True);assert r==48000 and y.shape[1]==2 and np.isfinite(y).all()
    assert not np.any(np.abs(y)>=1) and not m['callback_events'] and m['mute']==1
    assert m['ui_state_before']==m['ui_state_after'] and m['settings_restored']
    st=m['ui_state_before']
    for effect in ['bass','details','width']:
        assert int(st[effect].split()[0])==m['effect_levels'].get(effect,0)
    assert st['midnight']=='Off'
    assert all(st[k]=='0.0 dB' for k in st if k.startswith('EQ'))
    ui=ROOT/m['ui_evidence'];assert ui.exists()
    m['ui_evidence_sha256']=hashlib.sha256(ui.read_bytes()).hexdigest()
    implementation=ROOT/'acquisition.py' if label in extra_labels else ROOT.parent/'Mesures-Windows-WASAPI/wasapi_trials.py'
    m['acquisition_implementation']=str(implementation.relative_to(ROOT.parent))
    m['acquisition_implementation_sha256']=hashlib.sha256(implementation.read_bytes()).hexdigest()
    manifest.append(m)
first=manifest[0];assert first['label']=='baseline-zero-first'
assert all(first['ui_state_before'][e]=='0 %' for e in ['bass','details','width'])
d=AudioUtilities.GetSpeakers();v=d.EndpointVolume;state=Controls().snapshot('restored-final-confirmed')
assert d.id==initial['endpoint_id'] and abs(v.GetMasterVolumeLevelScalar()-initial['volume_scalar'])<1e-6 and v.GetMute()==initial['mute']
assert [state[e] for e in ['bass','details','width','power','midnight']]==['50 %','35 %','35 %','On','Off']
restored=dict(time=datetime.datetime.now().astimezone().isoformat(),controls=state,endpoint_id=d.id,volume_scalar=v.GetMasterVolumeLevelScalar(),mute=v.GetMute(),verified=True)
out=dict(captures=manifest,restored=restored,validation=dict(expected=len(expected),actual=len(manifest),first_measure_all_zero=True,one_effect_at_a_time_except_saved_original_mix=True,all_hashes_match=True,all_finite=True,no_sample_clipping=True,no_portaudio_callback_incidents=True,all_physical_output_muted=True,no_microphone=True,acoustic_validation=False))
acq.dump(ROOT/'manifest.json',out);acq.dump(ROOT/'restoration.json',restored)
print(json.dumps(out['validation'],indent=2));print(json.dumps(restored,indent=2))
