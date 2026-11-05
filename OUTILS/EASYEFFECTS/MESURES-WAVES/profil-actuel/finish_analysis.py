"""Regenerate summaries and verify offline tooling; no audio playback."""
import pathlib,subprocess,sys,json,py_compile
root=pathlib.Path(__file__).resolve().parent
for name in ['derive_summary.py','recovery_summary.py','ffmpeg_check.py','plot_results.py','finalize.py','write_report.py']:
    subprocess.run([sys.executable,str(root/name)],cwd=root,check=True)
test=root/'tests';test.mkdir(exist_ok=True)
subprocess.run([sys.executable,str(root/'compare_linux.py'),'--source',str(root/'reference/deep-suite.wav'),'--windows',str(root/'captures/deep-v028.wav'),'--linux',str(root/'captures/deep-v028.wav'),'--out',str(test/'comparison-selfcheck.json')],check=True)
v=json.loads((test/'comparison-selfcheck.json').read_text())
for r in v['comparisons']:
    for k in ['linux_minus_windows_lu','linux_minus_windows_rms_db','linux_minus_windows_crest_db']:
        assert r[k] is None or abs(r[k])<1e-10,(k,r)
    assert all(abs(x)<1e-10 for x in r['linux_minus_windows_bands_db'].values())
for p in root.glob('*.py'):py_compile.compile(str(p),doraise=True)
(root/'requirements-analysis.txt').write_text('numpy==2.5.4\nscipy==1.18.1\nsoundfile==0.14.0\nmatplotlib==3.11.2\npyloudnorm==0.2.0\n',encoding='utf-8')
(test/'verification.json').write_text(json.dumps({'offline_same_file_comparison_zero_deltas':True,'actual_linux_comparison':False,'python_scripts_compile':True},indent=2))
print('FINAL ANALYSIS AND OFFLINE CHECKS PASSED',flush=True)
