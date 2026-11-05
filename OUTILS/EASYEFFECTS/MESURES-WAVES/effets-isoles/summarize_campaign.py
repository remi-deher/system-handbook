import csv,json,pathlib
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parent
def load(name):return list(csv.DictReader((ROOT/'analysis'/name).open(encoding='utf-8')))
def main():
    tones=load('tone-comparisons.csv');transfers=load('transfers.csv');noise=load('noise-stereo.csv')
    captures=sorted(set(v['capture'] for v in tones))
    dynamics=[]
    for name in captures:
        for frequency in [80,125,250,997,6000]:
            rows=sorted([v for v in tones if v['capture']==name and int(v['frequency'])==frequency],key=lambda v:float(v['input_level']))
            if len(rows)!=3:continue
            xx=np.array([float(v['input_level']) for v in rows]);yy=np.array([float(v['fundamental_peak_dbfs']) for v in rows])
            slopes=np.diff(yy)/np.diff(xx)
            dynamics.append(dict(capture=name,frequency=frequency,input_levels=xx.tolist(),output_fundamental_peak_dbfs=yy.tolist(),gain_db=[float(v['gain_db']) for v in rows],delta_gain_vs_zero_db=[float(v['delta_gain_from_zero_db']) for v in rows],harmonics_relative_db=[float(v['harmonics_relative_db']) for v in rows],interval_output_db_per_input_db=slopes.tolist(),global_apparent_compression_ratio=float((xx[-1]-xx[0])/(yy[-1]-yy[0])) if abs(yy[-1]-yy[0])>1e-6 else None))
    base={(v['input_level'],v['input_channel'],v['output_channel'],v['Hz']):v for v in transfers if v['capture']=='baseline-zero-first'}
    drift=[]
    for name in [n for n in captures if n.startswith('zero-') and n not in ['zero-v50','zero-v100']]:
        subset=[v for v in tones if v['capture']==name]
        spectral=[]
        for v in transfers:
            if v['capture']!=name or v['input_channel']!=v['output_channel']:continue
            b=base[(v['input_level'],v['input_channel'],v['output_channel'],v['Hz'])]
            if float(b['magnitude_db'])>-100:spectral.append(float(v['magnitude_db'])-float(b['magnitude_db']))
        drift.append(dict(capture=name,max_abs_tone_gain_difference_db=max(abs(float(v['delta_gain_from_zero_db'])) for v in subset),spectral_delta_median_db=float(np.median(spectral)),spectral_delta_abs_p95_db=float(np.percentile(abs(np.asarray(spectral)),95)),spectral_delta_max_abs_db=float(np.max(abs(np.asarray(spectral))))))
    volumes=[]
    for effect in ['bass','details','width']:
        nominal={k:v for k,v in [((v['input_level'],v['input_channel'],v['output_channel'],v['Hz']),v) for v in transfers if v['capture']==f'{effect}-050-v10']}
        nt={(v['frequency'],v['input_level']):v for v in tones if v['capture']==f'{effect}-050-v10'}
        for vol in [5,15,50,100]:
            name=f'{effect}-050-v{vol:02d}';tt=[v for v in tones if v['capture']==name]
            if not tt:continue
            ds=[]
            for v in transfers:
                if v['capture']!=name or v['input_channel']!=v['output_channel']:continue
                b=nominal[(v['input_level'],v['input_channel'],v['output_channel'],v['Hz'])]
                ds.append(float(v['magnitude_db'])-float(b['magnitude_db']))
            volumes.append(dict(effect=effect,endpoint_volume_percent=vol,max_abs_tone_gain_delta_db=max(abs(float(v['gain_db'])-float(nt[(v['frequency'],v['input_level'])]['gain_db'])) for v in tt),spectral_delta_abs_p95_db=float(np.percentile(abs(np.asarray(ds)),95)),spectral_delta_max_abs_db=float(np.max(abs(np.asarray(ds))))))
    control_references={'zero-v100':'baseline-zero-first','zero-v50':'baseline-zero-first','zero-return-v10':'baseline-zero-first','bass-050-v100-repeat':'bass-050-v100','bass-050-v10-repeat':'bass-050-v10'}
    controls=[]
    for name,reference in control_references.items():
        subset=[v for v in tones if v['capture']==name]
        if not subset:continue
        reference_tones={(v['frequency'],v['input_level']):v for v in tones if v['capture']==reference}
        reference_spectral={(v['input_level'],v['input_channel'],v['output_channel'],v['Hz']):v for v in transfers if v['capture']==reference}
        spectral=[]
        for v in transfers:
            if v['capture']==name and v['input_channel']==v['output_channel']:
                b=reference_spectral[(v['input_level'],v['input_channel'],v['output_channel'],v['Hz'])]
                spectral.append(float(v['magnitude_db'])-float(b['magnitude_db']))
        controls.append(dict(capture=name,reference=reference,max_abs_tone_gain_delta_db=max(abs(float(v['gain_db'])-float(reference_tones[(v['frequency'],v['input_level'])]['gain_db'])) for v in subset),spectral_delta_abs_p95_db=float(np.percentile(abs(np.asarray(spectral)),95)),spectral_delta_max_abs_db=float(np.max(abs(np.asarray(spectral))))))
    out=dict(captures=len(captures),dynamics=dynamics,zero_returns=drift,endpoint_volume=volumes,volume_controls=controls,
             limitations=['Digital loopback only; no acoustic validation','Three source levels and steady-state windows do not identify a unique compressor','Apparent transfers from a nonlinear system are condition dependent','Zero percent does not prove absence of all OEM processing','Cross-channel phase ratios are delay invariant; absolute phase across captures is not'])
    (ROOT/'analysis/model-diagnostics.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
    lines=['# Résumé numérique automatique','',f'{len(captures)} captures analysées. Gains ci-dessous : source mono, canal L, fenêtre 300–500 ms.','', '| Capture | Hz | Gain à -60 / -48 / -36 dBFS (dB) | Harmoniques à -36 dBFS (dB relatifs) |','|---|---:|---|---:|']
    for v in dynamics:
        name=v['capture']
        if name=='baseline-zero-first' or name=='master-off-zero' or (name.startswith('bass-') and v['frequency'] in [80,125]) or (name.startswith('details-') and v['frequency'] in [997,6000]) or (name.startswith('width-') and v['frequency']==997):
            gain=' / '.join(f'{z:.3f}' for z in v['gain_db'])
            lines.append(f"| {name} | {v['frequency']} | {gain} | {v['harmonics_relative_db'][-1]:.2f} |")
    lines+=['','Les ratios de compression apparents figurent dans model-diagnostics.json ; ils ne sont pas des paramètres internes Waves identifiés.','']
    (ROOT/'analysis/RESUME-NUMERIQUE.md').write_text('\n'.join(lines),encoding='utf-8')
    print('Summary written for',len(captures),'captures')
if __name__=='__main__':main()
