import csv,os,pathlib
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parent
os.environ['MPLCONFIGDIR']=str(ROOT.parent/'Mesures-Windows-WASAPI/tools/matplotlib-cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
def load(name):return list(csv.DictReader((ROOT/'analysis'/name).open(encoding='utf-8')))
def save(fig,name):
    fig.savefig(ROOT/'analysis'/(name+'.png'),dpi=150);fig.savefig(ROOT/'analysis'/(name+'.pdf'));plt.close(fig)
def series(ax,rows,y,label,**kwargs):
    rows=sorted(rows,key=lambda v:float(v['Hz']))
    if rows:ax.semilogx([float(v['Hz']) for v in rows],[float(v[y]) for v in rows],label=label,**kwargs)
def decorate(ax,ylabel):
    ax.grid(True,which='both',alpha=.2);ax.set(xlim=(80,16000),xlabel='Fréquence (Hz)',ylabel=ylabel);ax.legend(fontsize=7)
def main():
    rel=load('transfers-relative-to-zero.csv');raw=load('transfers.csv');tones=load('tone-comparisons.csv');ms=load('mid-side-apparent.csv')
    names=dict(bass='MaxxBass',details='Détails',width='Largeur')
    colors={0:'#737373',25:'#0072B2',50:'#009E73',75:'#E69F00',100:'#D55E00'}
    fig,axs=plt.subplots(3,3,figsize=(15,11),layout='constrained')
    for i,effect in enumerate(names):
        for j,level in enumerate([-60,-48,-36]):
            ax=axs[i,j]
            for value in [25,50,75,100]:
                rows=[v for v in rel if v['capture']==f'{effect}-{value:03d}-v10' and int(v['input_level'])==level and v['input_channel']=='0' and v['output_channel']=='0']
                series(ax,rows,'delta_from_zero_median_db',f'{value} %',color=colors[value])
            ax.axhline(0,color=colors[0],lw=.7);ax.set_title(f'{names[effect]}, source {level} dBFS crête')
            decorate(ax,'Écart L→L / tous effets à 0 (dB)')
    fig.suptitle('Effets isolés : autres boutons à 0, EQ plat, volume Windows 10 %, muet\nTransferts apparents par balayage — pas une mesure acoustique',fontsize=12)
    save(fig,'01-spectral-isolation')
    fig,axs=plt.subplots(1,2,figsize=(13,5),layout='constrained')
    for value in [0,25,50,75,100]:
        name='baseline-zero-first' if value==0 else f'width-{value:03d}-v10'
        rows=[v for v in raw if v['capture']==name and v['input_level']=='-48' and v['input_channel']=='0' and v['output_channel']=='1']
        series(axs[0],rows,'cross_to_direct_gain_db',f'{value} %',color=colors[value])
        rows=[dict(v,side_mid_db=float(v['side_gain_db'])-float(v['mid_gain_db'])) for v in ms if v['capture']==name and v['input_level']=='-48']
        series(axs[1],rows,'side_mid_db',f'{value} %',color=colors[value])
    decorate(axs[0],'Rapport L→R / L→L (dB)');decorate(axs[1],'Gain apparent Side / Mid (dB)')
    axs[0].set_ylim(-70,10);axs[1].set_ylim(-40,40)
    fig.suptitle('Largeur isolée : source −48 dBFS, volume 10 %, muet\nSide/Mid calculé à partir des balayages séparés : approximation locale',fontsize=12)
    save(fig,'02-width-stereo')
    fig,axs=plt.subplots(3,2,figsize=(12,11),layout='constrained')
    for i,(effect,freq) in enumerate([('bass',80),('details',6000),('width',997)]):
        for value in [0,25,50,75,100]:
            name='baseline-zero-first' if value==0 else f'{effect}-{value:03d}-v10'
            rows=sorted([v for v in tones if v['capture']==name and int(v['frequency'])==freq],key=lambda v:float(v['input_level']))
            if not rows:continue
            xx=[float(v['input_level']) for v in rows]
            axs[i,0].plot(xx,[float(v['delta_gain_from_zero_db']) for v in rows],'-o',label=f'{value} %',color=colors[value])
            axs[i,1].plot(xx,[float(v['harmonics_relative_db']) for v in rows],'-o',label=f'{value} %',color=colors[value])
        for j in range(2):axs[i,j].grid(True,alpha=.2);axs[i,j].legend(fontsize=7);axs[i,j].set_xlabel('Source mono corrélée (dBFS crête)');axs[i,j].set_title(f'{names[effect]} — {freq} Hz')
        axs[i,0].set_ylabel('Écart de gain / effets à 0 (dB)');axs[i,1].set_ylabel('Harmoniques 2–8 / fondamentale (dB)')
    fig.suptitle('Niveau et harmoniques : fenêtres de 300 à 500 ms\nÀ 6000 Hz, seules les harmoniques 2 et 3 sont retenues sous 20 kHz',fontsize=12)
    save(fig,'03-levels-harmonics')
    fig,axs=plt.subplots(3,1,figsize=(11,11),layout='constrained')
    for i,effect in enumerate(names):
        base={v['Hz']:float(v['magnitude_db']) for v in raw if v['capture']==f'{effect}-050-v10' and v['input_level']=='-48' and v['input_channel']=='0' and v['output_channel']=='0'}
        for vol in [5,10,15,50,100]:
            name=f'{effect}-050-v{vol:02d}'
            rows=[dict(v,volume_delta_db=float(v['magnitude_db'])-base[v['Hz']]) for v in raw if v['capture']==name and v['input_level']=='-48' and v['input_channel']=='0' and v['output_channel']=='0' and v['Hz'] in base]
            series(axs[i],rows,'volume_delta_db',f'Volume Windows {vol} %')
        decorate(axs[i],'Écart / volume 10 % (dB)');axs[i].set_title(f'{names[effect]} seul à 50 %')
    fig.suptitle('Dépendance au volume Windows, sortie muette pendant toutes les captures\nCes courbes ne décrivent pas le volume acoustique des haut-parleurs',fontsize=12)
    save(fig,'04-endpoint-volume')
    fig,axs=plt.subplots(2,1,figsize=(12,9),layout='constrained')
    base={(v['capture'],v['Hz']):float(v['magnitude_db']) for v in raw if v['input_level']=='-48' and v['input_channel']=='0' and v['output_channel']=='0'}
    for name,ref,label in [('zero-v100','baseline-zero-first','Tous effets à 0'),('bass-050-v100','bass-050-v10','MaxxBass seul à 50 %'),('details-050-v100','details-050-v10','Détails seul à 50 %'),('width-050-v100','width-050-v10','Largeur seule à 50 %')]:
        rows=[dict(v,delta=float(v['magnitude_db'])-base[(ref,v['Hz'])]) for v in raw if v['capture']==name and v['input_level']=='-48' and v['input_channel']=='0' and v['output_channel']=='0' and (ref,v['Hz']) in base]
        series(axs[0],rows,'delta',label)
    repeat_deltas=[]
    for name,ref,label in [('zero-return-v10','baseline-zero-first','Zéro : retour 10 % / référence initiale'),('bass-050-v100-repeat','bass-050-v100','MaxxBass : répétition à 100 %'),('bass-050-v10-repeat','bass-050-v10','MaxxBass : retour à 10 %')]:
        rows=[dict(v,delta=float(v['magnitude_db'])-base[(ref,v['Hz'])]) for v in raw if v['capture']==name and v['input_level']=='-48' and v['input_channel']=='0' and v['output_channel']=='0' and (ref,v['Hz']) in base]
        series(axs[1],rows,'delta',label)
        repeat_deltas += [abs(v['delta']) for v in rows]
    decorate(axs[0],'Écart volume 100 % / 10 % (dB)');decorate(axs[1],'Écart de répétition / retour (dB)')
    lim=max(.1,max(repeat_deltas,default=0)*1.1);axs[1].set_ylim(-lim,lim)
    fig.suptitle('Contre-mesures : influence du volume maximal et réversibilité\nSource −48 dBFS, sortie physique muette ; courbes L→L',fontsize=12)
    save(fig,'05-volume-controls')
    print('Five PNG/PDF figures generated')
if __name__=='__main__':main()
