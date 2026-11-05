import sys,pathlib,json,time
ROOT=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT))
from bench import Session,dump
initial=json.loads((ROOT/'inventory-initial.json').read_text());current=round(initial['volume_scalar']*100)
plan=[dict(label=f'category-{name}-v{v:03d}',source_name='volume-probe.wav',percent=v,enabled=True,category=category)
      for name,category in [('other',0),('media',11),('movie',10)] for v in [current,100]]
dump(ROOT/'plan-categories.json',dict(method='Independent IAudioClient2 renderer; explicit categories; shared, non-offloaded, RAW disabled',trials=plan))
with Session() as s:
    for i,item in enumerate(plan):
        p=ROOT/'captures'/(item['label']+'.json')
        if p.exists() and json.loads(p.read_text()).get('valid_acquisition'):continue
        print('CATEGORY',i+1,'/',len(plan),flush=True);s.capture(**item);time.sleep(.3)
