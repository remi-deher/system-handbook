import sys,pathlib,json,csv,hashlib,argparse
ROOT=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT))
import numpy as np
import soundfile as sf
from scipy import signal
import metrics
SIGNATURE=hashlib.sha256((ROOT/'metrics.py').read_bytes()+pathlib.Path(__file__).read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
def writecsv(name,rows):
    if not rows:return
    with (ROOT/'analysis'/name).open('w',newline='',encoding='utf-8') as f:
        keys=sorted(set().union(*(v.keys() for v in rows)));w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
def analyze_one(path,reference):
    meta=json.loads(path.with_suffix('.json').read_text());x,rate,ref=reference
    y,r=sf.read(path,dtype='float32',always_2d=True);assert r==rate
    segments=ref['segments'];s=next(v for v in segments if v['name']=='sweep');a=s['start'];n=s['frames']
    c=signal.correlate(y[:a+n+rate//3,0],x[a:a+n,0],mode='valid',method='fft');lag=int(np.argmax(abs(c)))-a
    z=np.zeros_like(x);lo=max(0,-lag);hi=min(len(x),len(y)-lag);z[lo:hi]=y[lo+lag:hi+lag]
    useful=[s for s in segments if s['name'] not in ['gap','tail','conditioning_pink','sync']]
    covered=lo<=min(v['start'] for v in useful) and hi>=max(v['start']+v['frames'] for v in useful)
    full=meta['label'].startswith('deep-')
    base=dict(label=path.stem,volume_percent=meta['volume_percent_requested'],power=meta['controls_before']['power'])
    fm=metrics.programme(y,with_tp=full)
    file_row=dict(**base,source=pathlib.Path(meta['source']).name,lag_samples=lag,source_coverage_start=lo,source_coverage_end=hi,useful_segments_covered=covered,**{k:v for k,v in fm.items() if not isinstance(v,dict)},
                  samples_at_full_scale=meta['samples_at_or_above_full_scale'],valid_acquisition=meta['valid_acquisition'],callback_incidents=len(meta['callback_events']))
    freq,levels,H,matrices=metrics.apparent_matrices(x,z,segments)
    matrices=[dict(**base,**v) for v in matrices]
    if full:
        np.savez_compressed(ROOT/'analysis/cache'/(path.stem+'-complex.npz'),frequency_hz=freq,input_levels_dbfs=levels,H_output_input=H,valid_frequency_mask=(freq>=80)&(freq<=16000),axis_order=['input_level','output_channel','input_channel','frequency'],sample_rate=rate,lag_samples=lag,phase_reference='First left sweep correlation; not acoustic delay; condition-dependent apparent transfer; raw bins outside valid mask must not be used as a filter')
    programmes=[];tones=[];dynamics=[];imds=[]
    for index,s in enumerate(segments):
        a=s['start'];b=a+s['frames'];name=s['name'];v=z[a:b];src=x[a:b]
        prefix=dict(**base,segment=index,name=name,input_level=s.get('input_level'))
        if 'after_stimulus' in s:prefix['after_stimulus']=s['after_stimulus']
        if name in ['gap','tail','conditioning_pink','sync','sweep']:continue
        if name=='tone':
            for begin,end in [(.12,.25),(.35,min(.60,len(v)/rate))] if full else [(.10,.40)]:
                fitted=metrics.harmonic_fit(v[round(begin*rate):round(end*rate)],s['frequency'])
                for ch in [0,1]:
                    row=dict(**prefix,frequency=s['frequency'],channel=ch,window_start=begin,window_end=end,
                             fundamental_peak_dbfs=fitted['fundamental_peak_dbfs'][ch],gain_db=fitted['fundamental_peak_dbfs'][ch]-s['input_level'],harmonics_relative_db=fitted['harmonics_relative_db'][ch],residual_rms_dbfs=fitted['residual_rms_dbfs'][ch])
                    row.update({f'h{j+1}_peak_dbfs':amp[ch] for j,amp in enumerate(fitted['harmonics_peak_dbfs'])});tones.append(row)
        elif name in ['level_steps','recovery_tone']:
            out=metrics.envelopes(v,s['frequency']);inp=metrics.envelopes(src,s['frequency'])
            for ov,iv in zip(out,inp):
                dynamics.append(dict(**prefix,frequency=s['frequency'],time_s=ov[0],source_fundamental_dbfs=iv[1],output_left_dbfs=ov[1],output_right_dbfs=ov[2],left_gain_db=ov[1]-iv[1],right_gain_db=ov[2]-iv[2],left_fit_residual_relative_db=ov[3],right_fit_residual_relative_db=ov[4],window_ms=40,hop_ms=20))
        elif name=='intermodulation':
            fitted=metrics.imd(v[round(.2*rate):round(.8*rate)],s['kind'],s['f1'],s['f2'])
            for ch in [0,1]:
                row=dict(**prefix,kind=s['kind'],channel=ch,selected_product_ratio_db=fitted['product_to_second_carrier_db'][ch])
                row.update({f'component_{f}_Hz_dbfs':amp[ch] for f,amp in zip(fitted['frequencies'],fitted['components_peak_dbfs'])});imds.append(row)
        else:
            pm=metrics.programme(v);sm=metrics.programme(src)
            row=dict(**prefix,**{k:val for k,val in pm.items() if not isinstance(val,dict)},source_lufs=sm['lufs'],source_rms_dbfs=sm['rms_dbfs'],rms_gain_db=pm['rms_dbfs']-sm['rms_dbfs'],loudness_gain_lu=pm['lufs']-sm['lufs'] if pm['lufs'] is not None and sm['lufs'] is not None else None)
            for band,val in pm['bands_power_dbfs'].items():row['gain_band_'+band+'_db']=val-sm['bands_power_dbfs'][band]
            programmes.append(row)
    return dict(signature=SIGNATURE,raw_sha256=meta['capture_sha256'],file=file_row,matrices=matrices,programmes=programmes,tones=tones,dynamics=dynamics,imd=imds)
def main():
    cache=ROOT/'analysis/cache';cache.mkdir(exist_ok=True)
    parser=argparse.ArgumentParser();parser.add_argument('--scan-only',action='store_true');args=parser.parse_args()
    references={};results=[]
    for path in sorted((ROOT/'captures').glob('*.wav')):
        if args.scan_only and not path.stem.startswith('probe-'):continue
        mp=path.with_suffix('.json')
        if not mp.exists():continue
        try:meta=json.loads(mp.read_text())
        except json.JSONDecodeError:continue
        if not meta.get('valid_acquisition'):continue
        cp=cache/(path.stem+'.json');cached=json.loads(cp.read_text()) if cp.exists() else None
        if cached and cached.get('signature')==SIGNATURE and cached.get('raw_sha256')==meta['capture_sha256']:
            results.append(cached);continue
        source=ROOT/meta['source']
        if source.name not in references:
            x,rate=sf.read(source,dtype='float32',always_2d=True);ref=json.loads(source.with_suffix('.json').read_text());references[source.name]=(x,rate,ref)
        value=analyze_one(path,references[source.name]);dump(cp,value);results.append(value);print('ANALYZED',path.stem,flush=True)
    for key,name in [('file','files.csv'),('matrices','matrices.csv'),('programmes','programmes.csv'),('tones','tones.csv'),('dynamics','dynamics.csv'),('imd','intermodulation.csv')]:
        rows=[r[key] for r in results] if key=='file' else [v for r in results for v in r[key]]
        writecsv(name,rows)
    # Detect where the dense volume grid changes from the current-volume response.
    initial=json.loads((ROOT/'inventory-initial.json').read_text());anchor=round(initial['volume_scalar']*100)
    by_label={v['file']['label']:v for v in results};anchor_result=by_label.get(f'probe-v{anchor:03d}',by_label.get('probe-initial-b'))
    scan=[]
    if anchor_result:
        def direct(r):return np.array([v['magnitude_db'] for v in r['matrices'] if v['input_channel']==v['output_channel']])
        base=direct(anchor_result)
        for vol in range(101):
            result=by_label.get(f'probe-v{vol:03d}')
            if result:
                delta=direct(result)-base;scan.append(dict(volume_percent=vol,spectral_delta_p95_db=float(np.percentile(abs(delta),95)),spectral_delta_median_db=float(np.median(delta)),peak_dbfs=result['file']['sample_peak_dbfs'],lufs=result['file']['lufs']))
        writecsv('volume-grid.csv',scan)
        changed=[v['volume_percent'] for v in scan if v['spectral_delta_p95_db']>.3 and v['volume_percent']>anchor]
        suggested=[max(anchor+1,min(changed)-1),min(changed)] if changed else []
        dump(ROOT/'analysis/adaptive-volumes.json',dict(anchor=anchor,threshold_db=.3,suggested=suggested,first_detected_change=min(changed) if changed else None,complete_integer_scan=len(scan)==101))
    dump(ROOT/'analysis/progress.json',dict(analyzed_captures=len(results),integer_volumes=len(scan),all_useful_segments_covered=all(r['file']['useful_segments_covered'] for r in results),mathematical_metrics='LUFS via pyloudnorm DeMan; true peak is a 4x oversampling estimate, independently checked with FFmpeg'))
    print('RESULTS',len(results),'captures;',len(scan),'integer volumes',flush=True)
if __name__=='__main__':main()
