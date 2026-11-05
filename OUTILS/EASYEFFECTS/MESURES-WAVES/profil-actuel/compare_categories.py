import pathlib,csv,json,numpy as np
ROOT=pathlib.Path(__file__).resolve().parent
rows=list(csv.DictReader((ROOT/'analysis/matrices.csv').open()));files=list(csv.DictReader((ROOT/'analysis/files.csv').open()))
initial=json.loads((ROOT/'inventory-initial.json').read_text());current=round(initial['volume_scalar']*100)
comparisons=[]
for v in [current,100]:
    labels=[f'probe-v{v:03d}']+[f'category-{name}-v{v:03d}' for name in ['other','media','movie']]
    reference=[r for r in rows if r['label']==labels[0]]
    baseline={(r['input_channel'],r['output_channel'],r['Hz']):r for r in reference}
    bf=next(r for r in files if r['label']==labels[0])
    for label in labels[1:]:
        subset=[r for r in rows if r['label']==label];delta=[];cross_delta=[];phase_delta=[]
        if not subset:continue
        for r in subset:
            b=baseline[(r['input_channel'],r['output_channel'],r['Hz'])]
            if r['input_channel']==r['output_channel']:delta.append(float(r['magnitude_db'])-float(b['magnitude_db']))
            elif float(b['cross_to_direct_db'])>-40 and float(r['cross_to_direct_db'])>-40:
                cross_delta.append(float(r['cross_to_direct_db'])-float(b['cross_to_direct_db']))
                phase_delta.append((float(r['cross_to_direct_phase_deg'])-float(b['cross_to_direct_phase_deg'])+180)%360-180)
        f=next(r for r in files if r['label']==label)
        comparisons.append(dict(label=label,reference=labels[0],loudness_delta_lu=float(f['lufs'])-float(bf['lufs']),spectral_abs_p95_db=float(np.percentile(abs(np.asarray(delta)),95)),spectral_max_abs_db=float(np.max(abs(np.asarray(delta)))),cross_gain_abs_p95_db=float(np.percentile(abs(np.asarray(cross_delta)),95)) if cross_delta else None,cross_phase_abs_p95_degrees=float(np.percentile(abs(np.asarray(phase_delta)),95)) if phase_delta else None))
out=dict(comparisons=comparisons,media_material_difference=any('category-media-' in r['label'] and (r['spectral_abs_p95_db']>.3 or abs(r['loudness_delta_lu'])>.2 or (r['cross_gain_abs_p95_db'] or 0)>.3 or (r['cross_phase_abs_p95_degrees'] or 0)>5) for r in comparisons),criteria='Exploratory thresholds 0.3 dB direct/cross spectral P95, 5 degrees cross phase or 0.2 LU; not proof of equivalent implementations')
(ROOT/'analysis/category-comparison.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out,indent=2))
