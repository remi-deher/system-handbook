import pathlib,json,csv
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parent
def read(name):return list(csv.DictReader((ROOT/'analysis'/name).open(encoding='utf-8')))
def write(name,rows):
    if not rows:return
    with (ROOT/'analysis'/name).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=sorted(set().union(*(v.keys() for v in rows))));w.writeheader();w.writerows(rows)
def main():
    initial=json.loads((ROOT/'inventory-initial.json').read_text());current=round(initial['volume_scalar']*100)
    law=[]
    for v in range(101):
        path=ROOT/'captures'/f'probe-v{v:03d}.json'
        if path.exists():
            m=json.loads(path.read_text());law.append(dict(volume_percent=v,scalar_actual=m['volume_scalar_actual'],endpoint_db=m['volume_db'],nominal_linear_gain_from_db=10**(m['volume_db']/20),physical_output_muted=True))
    write('windows-volume-law.csv',law)
    tones=read('tones.csv');programmes=read('programmes.csv');matrices=read('matrices.csv')
    compress=[]
    for label in sorted(set(v['label'] for v in tones if v['label'].startswith('deep-'))):
        for f in [125,997,6000]:
            rows=sorted([v for v in tones if v['label']==label and v['frequency']==str(f) and v['channel']=='0' and v['window_start']=='0.35'],key=lambda v:float(v['input_level']))
            if len(rows)<2:continue
            for a,b in zip(rows,rows[1:]):
                xx=float(b['input_level'])-float(a['input_level']);yy=float(b['fundamental_peak_dbfs'])-float(a['fundamental_peak_dbfs'])
                compress.append(dict(label=label,frequency=f,input_low=float(a['input_level']),input_high=float(b['input_level']),output_db_per_input_db=yy/xx,
                                     apparent_interval_ratio=xx/yy if abs(yy)>1e-6 else None,gain_low=float(a['gain_db']),gain_high=float(b['gain_db']),interpretation='Condition/history dependent, not a unique internal compressor ratio'))
    write('compression-intervals.csv',compress)
    comparison=[]
    for vol in [current,100]:
        ref={v['segment']:v for v in programmes if v['label']==f'deep-off-v{vol:03d}'}
        for v in programmes:
            if v['label']!=f'deep-v{vol:03d}' or v['segment'] not in ref:continue
            b=ref[v['segment']]
            comparison.append(dict(label=v['label'],reference=b['label'],name=v['name'],input_level=v['input_level'],loudness_delta_lu=float(v['lufs'])-float(b['lufs']) if v['lufs'] and b['lufs'] else None,rms_delta_db=float(v['rms_dbfs'])-float(b['rms_dbfs']),crest_delta_db=float(v['crest_db'])-float(b['crest_db']),correlation_on=v['stereo_correlation'],correlation_off=b['stereo_correlation']))
    write('programme-on-off.csv',comparison)
    repeats=[]
    for name,ref in [('probe-initial-b','probe-initial-a')]+[(f'probe-return-v{v:03d}',f'probe-v{v:03d}') for v in [100,75,50,25,0,28]]+[(f'deep-repeat-v{v:03d}',f'deep-v{v:03d}') for v in [current,100]]:
        aa=[v for v in matrices if v['label']==name];bb={(v['input_level'],v['input_channel'],v['output_channel'],v['Hz']):v for v in matrices if v['label']==ref}
        if not aa or not bb:continue
        dd=[float(v['magnitude_db'])-float(bb[(v['input_level'],v['input_channel'],v['output_channel'],v['Hz'])]['magnitude_db']) for v in aa if v['input_channel']==v['output_channel']]
        repeats.append(dict(label=name,reference=ref,direct_spectral_abs_p95_db=float(np.percentile(abs(np.asarray(dd)),95)),direct_spectral_max_abs_db=float(np.max(abs(np.asarray(dd))))))
    (ROOT/'analysis/repeatability.json').write_text(json.dumps(repeats,indent=2),encoding='utf-8')
    # Explicit source/target pairs for a later Linux capture; never feed targets
    # through the processing chain again when evaluating a model.
    pairs=[]
    for p in sorted((ROOT/'captures').glob('deep-*.json')):
        m=json.loads(p.read_text());pairs.append(dict(label=m['label'],source=m['source'],target=f'captures/{p.stem}.wav',source_sha256=m['source_sha256'],target_sha256=m['capture_sha256'],windows_volume_percent=m['volume_percent_requested'],windows_volume_db=m['volume_db'],waves_power=m['controls_before']['power'],notes='Electrical target before physical mute/attenuation; align time; keep absolute gains; no target reprocessing'))
    (ROOT/'analysis/linux-evaluation-pairs.json').write_text(json.dumps(pairs,indent=2),encoding='utf-8')
    print('Derived:',len(law),'volume points;',len(pairs),'deep targets;',len(comparison),'programme comparisons')
if __name__=='__main__':main()
