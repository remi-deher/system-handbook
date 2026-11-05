import sys,pathlib,json,time
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from campaign import ROOT,Controls,trial,acq
plan=[dict(label=f'{effect}-050-v{round(volume*100):02d}',levels={effect:50},volume=volume,on=True) for effect in ['bass','details','width'] for volume in [.5,1.0]]
plan.append(dict(label='zero-final',levels={},volume=.1,on=True))
acq.dump(ROOT/'plan-extra-volumes.json',dict(trials=plan,physical_output='MUTED and verified before raising volume; restore volume before unmuting',source_levels_dbfs=[-60,-48,-36]))
try:
    for i,item in enumerate(plan):
        p=ROOT/'captures'/(item['label']+'.json')
        if p.exists():
            meta=json.loads(p.read_text())
            if meta.get('ui_state_before')==meta.get('ui_state_after') and meta.get('effect_levels')==item['levels']:
                print('SKIP',item['label'],flush=True);continue
            raise RuntimeError('Existing incomplete capture')
        print('EXTRA',i+1,'/',len(plan),flush=True);trial(**item);time.sleep(.4)
finally:
    ui=Controls();ui.power(True)
    for k,v in dict(bass=50,details=35,width=35).items():ui.set_percent(k,v)
    state=ui.snapshot('restored-original');acq.dump(ROOT/'restored-controls.json',state);print('RESTORED',state,flush=True)
