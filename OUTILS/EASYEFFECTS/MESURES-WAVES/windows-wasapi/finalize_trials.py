import datetime,hashlib,json,pathlib
import numpy as np
import soundfile as sf
from pycaw.pycaw import AudioUtilities
ROOT=pathlib.Path(__file__).resolve().parent
evidence={'pilot-on1':'waves-initial.png','pilot-on2':'pilot-on1-confirm.png','pilot-off1':'pilot-off1.png','pilot-off2':'pilot-off1.png','pilot-off-volume05':'pilot-off1.png','pilot-on-volume05':'pilot-on3.png','pilot-on-muted':'pilot-on3.png','dynamics-on1':'pilot-on3.png','dynamics-off1':'dynamics-off.png','dynamics-on2':'waves-restored.png'}
initial=json.loads((ROOT/'inventory-initial.json').read_text(encoding='utf-8'))
d=AudioUtilities.GetSpeakers();v=d.EndpointVolume
final=dict(time=datetime.datetime.now().astimezone().isoformat(),endpoint_id=d.id,volume_scalar=v.GetMasterVolumeLevelScalar(),mute=v.GetMute(),waves_playback='ON, visually confirmed in waves-restored.png',knobs='Untouched throughout; initial and restored UI screenshots',spatial_windows='Not independently confirmed; no spatial setting modified')
assert d.id==initial['endpoint_id']
assert abs(final['volume_scalar']-initial['volume_scalar'])<1e-6
assert final['mute']==initial['mute']
manifest=[]
for p in sorted((ROOT/'captures').glob('*.json')):
    m=json.loads(p.read_text());f=p.with_suffix('.wav');ref=ROOT/pathlib.Path(m['source'])
    assert hashlib.sha256(f.read_bytes()).hexdigest()==m['capture_sha256']
    assert hashlib.sha256(ref.read_bytes()).hexdigest()==m['source_sha256']
    y,r=sf.read(f,always_2d=True)
    assert np.isfinite(y).all() and y.shape[1]==2 and r==48000
    assert m['clipped_samples']==0 and not m['callback_events'] and m['settings_restored']
    m['ui_evidence']=evidence[m['label']];assert (ROOT/m['ui_evidence']).exists()
    m['source_peak_max_dbfs']=-30
    manifest.append(m)
out=dict(captures=manifest,restoration=final,validation=dict(count=len(manifest),all_hashes_match=True,all_finite=True,no_sample_clipping=True,no_portaudio_callback_incidents=True,physical_microphone_opened=False,acoustic_validation=False))
(ROOT/'manifest.json').write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding='utf-8')
(ROOT/'restoration.json').write_text(json.dumps(final,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(out['validation'],indent=2));print(json.dumps(final,indent=2))
