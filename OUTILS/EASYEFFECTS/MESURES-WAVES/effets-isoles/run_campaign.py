import json,time,traceback,sys,pathlib
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from campaign import ROOT,Controls,trial,acq
plan=[dict(label='master-off-zero',levels={},volume=.1,on=False)]
for effect in ['bass','details','width']:
    for value in [25,50,75,100]:
        plan.append(dict(label=f'{effect}-{value:03d}-v10',levels={effect:value},volume=.1,on=True))
    plan.append(dict(label=f'zero-after-{effect}',levels={},volume=.1,on=True))
for effect in ['bass','details','width']:
    for volume in [.05,.15]:
        plan.append(dict(label=f'{effect}-050-v{round(volume*100):02d}',levels={effect:50},volume=volume,on=True))
plan.append(dict(label='initial-mix-reference',levels=dict(bass=50,details=35,width=35),volume=.1,on=True))
acq.dump(ROOT/'plan.json',dict(first_capture='baseline-zero-first',trials=plan,source_levels_dbfs=[-60,-48,-36],mute=True,effect_percentages=[0,25,50,75,100],endpoint_volumes=[.05,.1,.15],restoration=dict(bass=50,details=35,width=35,power='On',midnight='Off')))
try:
    for index,item in enumerate(plan):
        dest=ROOT/'captures'/(item['label']+'.json')
        if dest.exists():
            old=json.loads(dest.read_text())
            if old.get('ui_state_before')==old.get('ui_state_after') and old.get('effect_levels')==item['levels']:
                print('RESUME SKIP',item['label'],flush=True);continue
            raise RuntimeError('Existing incomplete or mismatched capture '+str(dest))
        print('TRIAL',index+1,'/',len(plan),flush=True)
        trial(**item)
        time.sleep(.4)
except Exception:
    (ROOT/'campaign-error.txt').write_text(traceback.format_exc(),encoding='utf-8')
    raise
finally:
    ui=Controls();ui.power(True)
    for key,value in dict(bass=50,details=35,width=35).items():ui.set_percent(key,value)
    state=ui.snapshot('restored-original')
    acq.dump(ROOT/'restored-controls.json',state)
    print('RESTORED',state,flush=True)
