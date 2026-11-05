import sys,pathlib,json,time
ROOT=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT))
from bench import Session,dump
initial=json.loads((ROOT/'inventory-initial.json').read_text());current=round(initial['volume_scalar']*100)
plan=[dict(label=f'deep-recovery-v{v:03d}',percent=v,enabled=True) for v in [current,100]]
plan.append(dict(label=f'deep-recovery-off-v{current:03d}',percent=current,enabled=False))
plan.append(dict(label='deep-recovery-native-v100',percent=100,enabled=True,category=0))
dump(ROOT/'plan-recovery.json',dict(reason='Resolve history/cross-band recovery exposed by normal-level tone sequences',trials=plan,source='reference/recovery-suite.wav'))
with Session() as s:
    for i,item in enumerate(plan):
        p=ROOT/'captures'/(item['label']+'.json')
        if p.exists() and json.loads(p.read_text()).get('valid_acquisition'):continue
        print('RECOVERY',i+1,'/',len(plan),flush=True);s.capture(source_name='recovery-suite.wav',**item);time.sleep(.3)
