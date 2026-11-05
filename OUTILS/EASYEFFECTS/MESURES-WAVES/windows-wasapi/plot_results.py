import csv,json,os,pathlib
ROOT=pathlib.Path(__file__).resolve().parent
os.environ['MPLCONFIGDIR']=str(ROOT/'tools/matplotlib-cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
r=list(csv.DictReader((ROOT/'analysis/apparent-transfers.csv').open()))
fig,axs=plt.subplots(2,1,figsize=(10,8),layout='constrained')
for name,label,color in [('pilot-off1','Waves OFF','#737373'),('pilot-on1','Waves ON, essai 1','#0072B2'),('pilot-on2','Waves ON, essai 2','#56B4E9')]:
    for outch,style,suffix in [('0','-','L → L'),('1','--','L → R')]:
        rows=[v for v in r if v['capture']==name and v['input']=='0' and v['output']==outch]
        if name=='pilot-off1' and outch=='1':continue
        axs[0].semilogx([float(v['Hz']) for v in rows],[float(v['magnitude_dB']) for v in rows],style,color=color,label=f'{label} : {suffix}')
axs[0].set(xlim=(100,16000),ylim=(-35,25),xlabel='Fréquence (Hz)',ylabel='Gain apparent / source (dB)',title='Loopback Realtek : balayages gauche seule, source à −30 dBFS crête')
axs[0].legend(fontsize=8);axs[0].grid(True,which='both',alpha=.25)
d=json.loads((ROOT/'analysis/dynamics.json').read_text())
for name,style in [('dynamics-off1','--'),('dynamics-on1','-'),('dynamics-on2',':')]:
    for freq,color in [(125,'#D55E00'),(997,'#009E73')]:
        rows=[v for v in d if v['capture']==name and v['frequency']==freq]
        # Average repeated -30 dBFS segments rather than hiding them.
        xx=sorted(set(v['input_peak_dbfs'] for v in rows))
        yy=[np.mean([v['windows'][-1]['fundamental_peak_dbfs'][0] for v in rows if v['input_peak_dbfs']==level]) for level in xx]
        axs[1].plot(xx,yy,style+'o',color=color,label=f'{name}, {freq} Hz',markersize=4)
axs[1].set(xlabel='Crête numérique de la source (dBFS)',ylabel='Fondamentale capturée, canal L (dBFS crête)',title='Tonalités mono corrélées : réponse à plusieurs niveaux, sortie physique muette')
axs[1].grid(True,alpha=.25);axs[1].legend(fontsize=8)
fig.suptitle('Mesures numériques WASAPI — pas une mesure acoustique des haut-parleurs',fontsize=12)
fig.savefig(ROOT/'analysis/resultats.png',dpi=160)
fig.savefig(ROOT/'analysis/resultats.pdf')
print('Plots written')
