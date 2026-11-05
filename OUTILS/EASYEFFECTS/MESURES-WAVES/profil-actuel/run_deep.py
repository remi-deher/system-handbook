import sys,pathlib,json,time
ROOT=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT))
from bench import Session,dump
initial=json.loads((ROOT/'inventory-initial.json').read_text());current=round(initial['volume_scalar']*100)
volumes=list(dict.fromkeys([current,0,10,50,65,75,90,95,100]))
adaptive=ROOT/'analysis/adaptive-volumes.json'
if adaptive.exists():
    adaptive_data=json.loads(adaptive.read_text())
    if not adaptive_data.get('complete_integer_scan'):raise RuntimeError('Complete the integer volume scan and its analysis before detailed trials')
    extra=adaptive_data.get('suggested',[])
    for v in extra[:2]:
        if all(abs(v-b)>3 for b in volumes):volumes.append(v)
plan=[dict(label=f'deep-v{v:03d}',percent=v,enabled=True) for v in volumes]
plan += [dict(label=f'deep-repeat-v{v:03d}',percent=v,enabled=True) for v in [current,100]]
plan += [dict(label=f'deep-off-v{v:03d}',percent=v,enabled=False) for v in [current,100]]
categories=ROOT/'analysis/category-comparison.json'
if categories.exists() and json.loads(categories.read_text()).get('media_material_difference'):
    plan += [dict(label=f'deep-media-v{v:03d}',percent=v,enabled=True,category=11) for v in [current,100]]
dump(ROOT/'plan-deep.json',dict(reference='Current unchanged Waves knobs/EQ; only global Playback power OFF for two matched controls',trials=plan,source='reference/deep-suite.wav',source_levels_dbfs=[-60,-48,-36,-24,-18,-12,-6,-1],all_physical_output_muted=True))
with Session() as session:
    for i,item in enumerate(plan):
        p=ROOT/'captures'/(item['label']+'.json')
        if p.exists() and json.loads(p.read_text()).get('valid_acquisition'):
            print('SKIP',item['label'],flush=True);continue
        session.ui.power(item['enabled']);session.ui.snapshot(item['label'])
        print('DEEP',i+1,'/',len(plan),flush=True)
        session.capture(source_name='deep-suite.wav',**item);time.sleep(.3)
