import pathlib,csv,json
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parent
def main():
    rows=list(csv.DictReader((ROOT/'analysis/dynamics.csv').open()));labels=sorted(set(v['label'] for v in rows if v.get('after_stimulus')))
    out=[]
    for label in labels:
        baseline=[v for v in rows if v['label']==label and v.get('after_stimulus')=='baseline' and float(v['time_s'])>=8]
        if not baseline:continue
        bg=float(np.median([float(v['left_gain_db']) for v in baseline]))
        for kind in ['tone_125_Hz','tone_6000_Hz','broadband_pink']:
            r=[v for v in rows if v['label']==label and v.get('after_stimulus')==kind]
            if not r:continue
            tt=np.array([float(v['time_s']) for v in r]);gg=np.array([float(v['left_gain_db']) for v in r]);late=float(np.median(gg[(tt>=13)&(tt<=14.9)]));early=float(np.median(gg[(tt>=.04)&(tt<=.14)]))
            residual=np.array([float(v.get('left_fit_residual_relative_db') or -200) for v in r]);unexplained=(tt>=5)&(tt<=14.9)&(residual>-20)
            close=(abs(gg-late)<=.5)&~unexplained;hold=25;settled=None
            for i in range(len(gg)-hold):
                if tt[i]>=.04 and np.all(close[i:i+hold]):settled=float(tt[i]);break
            out.append(dict(label=label,preceding_stimulus=kind,baseline_gain_db=bg,early_gain_40_140ms_db=early,late_gain_13_15s_db=late,late_minus_initial_baseline_db=late-bg,first_within_half_db_for_half_second_s=settled,
                            window_ms=40,hop_ms=20,unexplained_late_windows=int(np.sum(unexplained)),unexplained_late_times_s=tt[unexplained].tolist(),last_100ms_excluded=True,interpretation='Apparent recovery with residual alignment/fade/window effects; not a unique internal release time. High-residual late windows are anomalies, not interpreted as gain control.'))
    (ROOT/'analysis/recovery-summary.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
    with (ROOT/'analysis/recovery-summary.csv').open('w',newline='',encoding='utf-8') as f:
        if out:w=csv.DictWriter(f,fieldnames=out[0].keys());w.writeheader();w.writerows(out)
    print('Recovery summaries:',len(out))
if __name__=='__main__':main()
