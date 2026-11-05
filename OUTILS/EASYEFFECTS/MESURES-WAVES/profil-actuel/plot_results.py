import pathlib,csv,json,os,re
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parent
os.environ['MPLCONFIGDIR']=str(ROOT/'tools/matplotlib-cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
def read(name):return list(csv.DictReader((ROOT/'analysis'/name).open(encoding='utf-8')))
def num(r,k):return float(r[k]) if r.get(k) not in ['',None] else np.nan
def save(fig,name):
    fig.savefig(ROOT/'analysis'/(name+'.png'),dpi=150);fig.savefig(ROOT/'analysis'/(name+'.pdf'));plt.close(fig)
def main():
    files=read('files.csv');mat=read('matrices.csv');tones=read('tones.csv');dyn=read('dynamics.csv');programmes=read('programmes.csv')
    initial=json.loads((ROOT/'inventory-initial.json').read_text());current=round(initial['volume_scalar']*100)
    selected=[(f'deep-v{current:03d}',f'Waves ON, {current} %','#0072B2','-'),('deep-v050','Waves ON, 50 %','#009E73','-'),('deep-v075','Waves ON, 75 %','#E69F00','-'),('deep-v100','Waves ON, 100 %','#D55E00','-'),(f'deep-off-v{current:03d}','Playback OFF','#777777','--')]
    fig,axs=plt.subplots(3,1,figsize=(12,11),layout='constrained')
    rr=sorted([r for r in files if re.fullmatch(r'probe-v\d{3}',r['label'])],key=lambda r:int(r['volume_percent']))
    xx=[int(r['volume_percent']) for r in rr]
    for key,label in [('lufs','Sonie intégrée (LUFS)'),('sample_peak_dbfs','Crête échantillon (dBFS)'),('rms_dbfs','RMS (dBFS)')]:axs[0].plot(xx,[num(r,key) for r in rr],label=label)
    axs[0].legend();axs[0].grid(alpha=.2);axs[0].set(xlabel='Volume Windows (%)',ylabel='Niveau électrique capturé')
    baseline={r['Hz']:float(r['magnitude_db']) for r in mat if r['label']==f'probe-v{current:03d}' and r['input_channel']=='0' and r['output_channel']=='0'}
    freqs=np.array(sorted(float(k) for k in baseline));heat=[]
    for v in xx:
        d={float(r['Hz']):float(r['magnitude_db'])-baseline[r['Hz']] for r in mat if r['label']==f'probe-v{v:03d}' and r['input_channel']=='0' and r['output_channel']=='0'};heat.append([d[f] for f in freqs])
    image=axs[1].pcolormesh(freqs,xx,np.array(heat),shading='auto',cmap='coolwarm',vmin=-6,vmax=6);axs[1].set(xscale='log',xlabel='Fréquence (Hz)',ylabel='Volume Windows (%)');fig.colorbar(image,ax=axs[1],label=f'Écart direct / volume {current} % (dB)')
    law=read('windows-volume-law.csv');axs[2].plot([num(r,'volume_percent') for r in law],[num(r,'endpoint_db') for r in law]);axs[2].grid(alpha=.2);axs[2].set(xlabel='Volume Windows (%)',ylabel='Gain endpoint lu dans l’API (dB)')
    fig.suptitle('101 positions de volume — sonde identique, profil Waves fixe\nLoopback électrique ; sortie physique muette, pas une courbe de SPL',fontsize=12);save(fig,'01-all-volumes')
    fig,axs=plt.subplots(2,3,figsize=(15,9),layout='constrained')
    for j,freq in enumerate([125,997,6000]):
        for name,label,color,style in selected:
            r=sorted([r for r in tones if r['label']==name and r['frequency']==str(freq) and r['channel']=='0' and r['window_start']=='0.35'],key=lambda r:num(r,'input_level'))
            if not r:continue
            x=[num(v,'input_level') for v in r]
            axs[0,j].plot(x,[num(v,'fundamental_peak_dbfs') for v in r],style+'o',color=color,label=label,ms=3)
            axs[1,j].plot(x,[num(v,'harmonics_relative_db') for v in r],style+'o',color=color,label=label,ms=3)
        axs[0,j].set(title=f'{freq} Hz',ylabel='Fondamentale sortie (dBFS crête)');axs[1,j].set(ylabel='Harmoniques / fondamentale (dB)',xlabel='Source mono (dBFS crête)')
        for i in [0,1]:axs[i,j].grid(alpha=.2);axs[i,j].legend(fontsize=7)
    fig.suptitle('Courbes entrée/sortie et harmoniques à niveaux réels\nHarmoniques limitées à H2..H8 et 20 kHz ; à 6 kHz : H2/H3 seulement',fontsize=12);save(fig,'02-levels-limiting-harmonics')
    fig,axs=plt.subplots(2,2,figsize=(13,9),layout='constrained')
    for lev,style in [(-48,':'),(-24,'-'),(-6,'--')]:
        for name,col in [(f'deep-v{current:03d}','#0072B2'),('deep-v100','#D55E00')]:
            subset=sorted([r for r in mat if r['label']==name and r['input_level']==str(lev) and r['input_channel']=='0'],key=lambda r:num(r,'Hz'))
            for out in [0,1]:
                rows=[r for r in subset if r['output_channel']==str(out)]
                axs[0,out].semilogx([num(r,'Hz') for r in rows],[num(r,'magnitude_db') for r in rows],style,color=col,label=f'{name}: {lev} dBFS')
            rows=[r for r in subset if r['output_channel']=='1']
            axs[1,0].semilogx([num(r,'Hz') for r in rows],[num(r,'cross_to_direct_db') for r in rows],style,color=col,label=f'{name}: {lev}')
            valid=[r for r in rows if num(r,'cross_to_direct_db')>-40]
            axs[1,1].semilogx([num(r,'Hz') for r in valid],[num(r,'cross_to_direct_phase_deg') for r in valid],style,color=col,label=f'{name}: {lev}')
    for ax in axs.flat:ax.grid(True,which='both',alpha=.2);ax.set_xlabel('Fréquence (Hz)');ax.legend(fontsize=6)
    axs[0,0].set_ylabel('Gain apparent L→L (dB)');axs[0,1].set_ylabel('Gain apparent L→R (dB)');axs[1,0].set_ylabel('Croisé / direct (dB)');axs[1,1].set_ylabel('Phase croisé/direct (degrés)')
    fig.suptitle('Stéréo : niveaux, volume et phase relative\nRéponses apparentes d’une chaîne non linéaire ; pas une convolution universelle',fontsize=12);save(fig,'03-stereo-complex')
    fig,axs=plt.subplots(2,2,figsize=(13,9),layout='constrained')
    for j,freq in enumerate([125,997]):
        plotted_source=False
        for name,col in [(f'deep-v{current:03d}','#0072B2'),('deep-v100','#D55E00'),(f'deep-off-v{current:03d}','#777777')]:
            r=[r for r in dyn if r['label']==name and r['frequency']==str(freq)]
            if not r:continue
            x=[num(v,'time_s') for v in r]
            axs[0,j].plot(x,[num(v,'output_left_dbfs') for v in r],color=col,label=name)
            axs[1,j].plot(x,[num(v,'left_gain_db') for v in r],color=col,label=name)
            if not plotted_source:axs[0,j].plot(x,[num(v,'source_fundamental_dbfs') for v in r],'k--',alpha=.5,label='Source');plotted_source=True
        axs[0,j].set(title=f'{freq} Hz',ylabel='Fondamentale (dBFS crête)');axs[1,j].set(ylabel='Gain sortie/source (dB)',xlabel='Temps dans la séquence (s)')
        for i in [0,1]:axs[i,j].grid(alpha=.2);axs[i,j].legend(fontsize=7)
    fig.suptitle('Compression et récupération après changements de niveau\nEstimation fenêtrée 40 ms / pas 20 ms ; retard résiduel inclus',fontsize=12);save(fig,'04-time-dynamics')
    wanted=[('speech_tts',-18,'Parole TTS, −18'),('speech_tts',-3,'Parole TTS, −3'),('synthetic_percussive_music',-3,'Musique percussive, −3'),('multisine_dense',-3,'Multisine dense, −3'),('pink_stereo',-3,'Bruit rose, −3'),('short_transient_bursts',-1,'Transitoires, −1')]
    fig,axs=plt.subplots(1,2,figsize=(14,7),layout='constrained');yy=np.arange(len(wanted));width=.23
    for i,(name,label,color,style) in enumerate([selected[0],selected[3],selected[4]]):
        lg=[];cd=[]
        for kind,level,_ in wanted:
            r=next((r for r in programmes if r['label']==name and r['name']==kind and num(r,'input_level')==level),None)
            lg.append(num(r,'loudness_gain_lu') if r else np.nan)
            cd.append(num(r,'crest_db')-(level-num(r,'source_rms_dbfs')) if r else np.nan)
        axs[0].barh(yy+(i-1)*width,lg,height=width,color=color,label=label);axs[1].barh(yy+(i-1)*width,cd,height=width,color=color,label=label)
    for ax in axs:ax.set_yticks(yy,[v[2] for v in wanted]);ax.invert_yaxis();ax.grid(axis='x',alpha=.2);ax.legend(fontsize=8)
    axs[0].set_xlabel('Gain de sonie électrique / source (LU)');axs[1].set_xlabel('Variation du facteur de crête (dB)')
    fig.suptitle('Puissance perçue : indices électriques selon le type de son\nMesure LUFS, pas SPL ; les signaux sont synthétiques et ne couvrent pas tous les genres',fontsize=12);save(fig,'05-programme-loudness')
    fig,axs=plt.subplots(1,3,figsize=(16,5),layout='constrained')
    for j,(kind,title) in enumerate([('tone_125_Hz','Après grave 125 Hz'),('tone_6000_Hz','Après aigu 6 kHz'),('broadband_pink','Après bruit rose')]):
        for name,col in [(f'deep-recovery-v{current:03d}','#0072B2'),('deep-recovery-v100','#D55E00'),('deep-recovery-native-v100','#CC79A7'),(f'deep-recovery-off-v{current:03d}','#777777')]:
            rows=[r for r in dyn if r['label']==name and r.get('after_stimulus')==kind and .04<=num(r,'time_s')<=14.9]
            if rows:
                vals=[np.nan if num(r,'time_s')>=5 and num(r,'left_fit_residual_relative_db')>-20 else num(r,'left_gain_db') for r in rows]
                axs[j].plot([num(r,'time_s') for r in rows],vals,color=col,label=name)
        axs[j].set(title=title,xlabel='Temps après retour du 997 Hz faible (s)',ylabel='Gain du 997 Hz à −36 dBFS (dB)');axs[j].grid(alpha=.2);axs[j].legend(fontsize=7)
    fig.suptitle('Mémoire et récupération entre bandes\nMême son faible après trois excitations fortes ; fenêtre 40 ms, pas 20 ms',fontsize=12)
    save(fig,'06-cross-band-recovery')
    print('Six comparison figures and PDFs written')
if __name__=='__main__':main()
