import sys,pathlib,json,time
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from campaign import ROOT,Controls,trial,acq
plan=[
 dict(label='zero-v100',levels={},volume=1.0,on=True),
 dict(label='zero-v50',levels={},volume=.5,on=True),
 dict(label='zero-return-v10',levels={},volume=.1,on=True),
 dict(label='bass-050-v100-repeat',levels={'bass':50},volume=1.0,on=True),
 dict(label='bass-050-v10-repeat',levels={'bass':50},volume=.1,on=True)]
acq.dump(ROOT/'plan-volume-controls.json',dict(reason='Confirm volume-dependent response at 100%, isolate common OEM processing with knobs zero and test reversibility',trials=plan))
try:
    for i,item in enumerate(plan):
        p=ROOT/'captures'/(item['label']+'.json')
        if p.exists():raise RuntimeError('Control capture already exists')
        print('CONTROL',i+1,'/',len(plan),flush=True);trial(**item);time.sleep(.4)
finally:
    ui=Controls();ui.power(True)
    for k,v in dict(bass=50,details=35,width=35).items():ui.set_percent(k,v)
    state=ui.snapshot('restored-original');acq.dump(ROOT/'restored-controls.json',state);print('RESTORED',state,flush=True)
