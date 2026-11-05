import pathlib,json,subprocess,re,hashlib,sys
ROOT=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT))
import metrics
import soundfile as sf
def main():
    exe=next((ROOT/'tools/ffmpeg').rglob('ffmpeg.exe'))
    version=subprocess.check_output([str(exe),'-version'],text=True,encoding='utf-8',errors='replace')
    (ROOT/'tools/ffmpeg-version.txt').write_text(version,encoding='utf-8')
    paths=[ROOT/'reference/volume-probe.wav',ROOT/'captures/probe-initial-a.wav']
    for name in ['deep-v028.wav','deep-v100.wav','deep-off-v028.wav']:
        p=ROOT/'captures'/name
        if p.exists():paths.append(p)
    rows=[]
    for p in paths:
        cmd=[str(exe),'-nostdin','-hide_banner','-loglevel','info','-i',str(p),'-af','ebur128=peak=true:framelog=verbose','-f','null','-']
        completed=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',errors='replace',check=True)
        log=completed.stderr;(ROOT/'analysis'/('ffmpeg-'+p.stem+'.txt')).write_text(log,encoding='utf-8')
        li=re.findall(r'\bI:\s*(-?[\d.]+)\s*LUFS',log);tp=re.findall(r'\bPeak:\s*(-?[\d.]+)\s*dBFS',log)
        y,r=sf.read(p,always_2d=True);measured=metrics.programme(y,with_tp=True)
        row=dict(file=p.relative_to(ROOT).as_posix(),ffmpeg_lufs=float(li[-1]) if li else None,ffmpeg_true_peak_dbfs=float(tp[-1]) if tp else None,pyloudnorm_lufs=measured['lufs'],scipy_4x_peak_dbfs=measured['estimated_true_peak_4x_dbfs'])
        if row['ffmpeg_lufs'] is not None and row['pyloudnorm_lufs'] is not None:row['lufs_difference']=row['pyloudnorm_lufs']-row['ffmpeg_lufs']
        if row['ffmpeg_true_peak_dbfs'] is not None:row['peak_difference']=row['scipy_4x_peak_dbfs']-row['ffmpeg_true_peak_dbfs']
        rows.append(row);print(row,flush=True)
    provenance=dict(source_url='https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip',distribution_reference='https://ffmpeg.org/download.html',binary_sha256=hashlib.sha256(exe.read_bytes()).hexdigest(),version=version.splitlines()[0])
    (ROOT/'analysis/independent-crosscheck.json').write_text(json.dumps(dict(tool=provenance,measurements=rows),indent=2),encoding='utf-8')
if __name__=='__main__':main()
