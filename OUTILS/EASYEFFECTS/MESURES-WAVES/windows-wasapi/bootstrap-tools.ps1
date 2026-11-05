# Re-create a local Python runtime; no global Python installation or PATH change.
$ErrorActionPreference='Stop'
$taskRoot=$PSScriptRoot
$runtime=Join-Path $taskRoot 'tools\python'
New-Item -ItemType Directory -Path (Join-Path $taskRoot 'tools') -Force | Out-Null
if(-not (Test-Path (Join-Path $runtime 'python.exe'))){
 $archive=Join-Path $taskRoot 'tools\python-3.13.9-embed-amd64.zip'
 Invoke-WebRequest 'https://www.python.org/ftp/python/3.13.9/python-3.13.9-embed-amd64.zip' -OutFile $archive
 Expand-Archive -LiteralPath $archive -DestinationPath $runtime
 Add-Content (Join-Path $runtime 'python313._pth') "`nimport site"
}
$python=Join-Path $runtime 'python.exe'
& $python -m pip --version
if($LASTEXITCODE -ne 0){
 $bootstrap=Join-Path $taskRoot 'tools\get-pip.py'
 Invoke-WebRequest 'https://bootstrap.pypa.io/get-pip.py' -OutFile $bootstrap
 & $python $bootstrap --no-warn-script-location
 if($LASTEXITCODE -ne 0){throw 'pip bootstrap failed'}
}
& $python -m pip install --no-warn-script-location -r (Join-Path $taskRoot 'requirements-lock.txt')
if($LASTEXITCODE -ne 0){throw 'Dependency installation failed'}
