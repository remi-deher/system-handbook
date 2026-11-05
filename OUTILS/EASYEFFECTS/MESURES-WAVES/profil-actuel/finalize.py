import sys,pathlib,json,hashlib
ROOT=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT))
from bench import LiveControls,endpoint,dump,stamp
import soundfile as sf
import numpy as np
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    initial=json.loads((ROOT/'inventory-initial.json').read_text());expected=[]
    for name in ['plan-scan.json','plan-categories.json','plan-deep.json','plan-recovery.json']:
        expected.extend(json.loads((ROOT/name).read_text())['trials'])
    analysis={r['label']:r for r in __import__('csv').DictReader((ROOT/'analysis/files.csv').open())}
    rows=[];unity=[]
    for trial in expected:
        label=trial['label'];p=ROOT/'captures'/(label+'.json');m=json.loads(p.read_text());wav=p.with_suffix('.wav');source=ROOT/m['source']
        if sha(wav)!=m['capture_sha256'] or sha(source)!=m['source_sha256']:raise RuntimeError('Hash mismatch '+label)
        if not m['valid_acquisition'] or not m['mute_verified'] or m['callback_events'] or not m['profile_unchanged']:raise RuntimeError('Invalid acquisition '+label)
        if m['output']['name']!=initial['output']['name'] or m['loopback']['name']!=initial['loopback']['name'] or m['endpoint_id']!=initial['endpoint_id']:raise RuntimeError('Endpoint mismatch '+label)
        y,r=sf.read(wav,dtype='float32',always_2d=True)
        if r!=48000 or y.shape[1]!=2 or not np.isfinite(y).all():raise RuntimeError('Invalid WAV '+label)
        if analysis[label]['useful_segments_covered']!='True':raise RuntimeError('Incomplete active source coverage '+label)
        expected_power='On' if trial.get('enabled',True) else 'Off';st=dict(initial['controls'],power=expected_power)
        if m['controls_before']!=st or m['controls_after']!=st:raise RuntimeError('Profile mismatch '+label)
        count=int(np.sum(abs(y)>=1))
        if count:unity.append(dict(label=label,samples_at_or_above_unity=count))
        rows.append(m)
    grid=sorted(m['volume_percent_requested'] for m in rows if __import__('re').fullmatch(r'probe-v\d{3}',m['label']))
    if grid!=list(range(101)):raise RuntimeError('Integer volume scan incomplete')
    d=endpoint();v=d.EndpointVolume;c=LiveControls();state=c.snapshot('final-verified-profile')
    if d.id!=initial['endpoint_id'] or state!=initial['controls'] or abs(v.GetMasterVolumeLevelScalar()-initial['volume_scalar'])>1e-6 or v.GetMute()!=initial['mute']:raise RuntimeError('Initial state not restored')
    qc=dict(expected=len(expected),verified=len(rows),all_integer_volumes_0_to_100=True,all_hashes_match=True,all_finite=True,all_useful_source_covered=True,all_profiles_verified=True,all_physical_output_muted=True,no_microphone=True,no_callback_incidents=True,
            unity_samples_measured=unity,clipping_not_silently_discarded=True,acoustic_validation=False)
    qc['flagged_recovery_analysis_windows']=[r for r in json.loads((ROOT/'analysis/recovery-summary.json').read_text()) if r['unexplained_late_windows']]
    qc['analysis_anomalies_preserved_and_not_fitted_as_gain']=True
    restored=dict(time=stamp(),endpoint_id=d.id,controls=state,volume_scalar=v.GetMasterVolumeLevelScalar(),volume_db=v.GetMasterVolumeLevel(),mute=v.GetMute(),verified=True)
    dump(ROOT/'manifest.json',dict(validation=qc,captures=rows,restored=restored));dump(ROOT/'restoration.json',restored)
    dump(ROOT/'profile-signature.json',dict(controls=initial['controls'],endpoint_id=initial['endpoint_id'],mix_format=initial['mix_format'],initial_volume=initial['volume_scalar'],signature_sha256=hashlib.sha256(json.dumps(initial['controls'],sort_keys=True).encode()).hexdigest()))
    print(json.dumps(qc,indent=2));print(json.dumps(restored,indent=2))
if __name__=='__main__':main()
