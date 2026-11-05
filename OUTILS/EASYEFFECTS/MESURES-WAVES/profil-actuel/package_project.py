"""Package measured data and scripts, excluding local tool installations."""
import pathlib,zipfile,json,hashlib,os
root=pathlib.Path(__file__).resolve().parent.parent
target=root.parent/(root.name+'.zip')
temporary=target.with_suffix('.new.zip')
manifest=json.loads((root/'Mesures-Profil-Actuel-20261030/manifest.json').read_text())
assert manifest['validation']['verified']==132
paths=[p for p in root.rglob('*') if p.is_file() and not any(v.lower() in ['tools','__pycache__','.git'] for v in p.relative_to(root).parts) and p.name!='Audio-endpoints.txt']
with zipfile.ZipFile(temporary,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
    for i,p in enumerate(paths):
        z.write(p,(pathlib.Path(root.name)/p.relative_to(root)).as_posix())
        if i%100==0:print('PACKAGED',i,'/',len(paths),flush=True)
with zipfile.ZipFile(temporary) as z:
    assert z.testzip() is None
    m=json.loads(z.read(root.name+'/Mesures-Profil-Actuel-20261030/manifest.json'))
    assert m['validation']['verified']==132
    assert root.name+'/PROMPT-OMARCHY-REFERENCE-APPROFONDIE.md' in z.namelist()
os.replace(temporary,target)
checksum=hashlib.sha256(target.read_bytes()).hexdigest()
target.with_suffix('.zip.sha256').write_text(checksum+'  '+target.name+'\n')
print('ARCHIVE VERIFIED',target,'bytes',target.stat().st_size,'sha256',checksum,flush=True)
