"""Prepare pinned Pixel Wheels source and unchanged official game assets."""
from pathlib import Path
import hashlib
import shutil
import subprocess
import urllib.request
import zipfile
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'.sources/pixelwheels'
revision='de6a692f3b6f2ade9e914982e0aeadb4aa2b1de3'
if not source.exists():
    subprocess.run(['git','clone','--branch','1.0.1','https://github.com/agateau/pixelwheels',str(source)],check=True)
if subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()!=revision:
    raise SystemExit('Preserve existing source and use a fresh pinned Pixel Wheels tree.')
archive=ROOT/'build/downloads/pixelwheels-itchio-1.0.1.apk';archive.parent.mkdir(parents=True,exist_ok=True)
if not archive.exists():urllib.request.urlretrieve('https://github.com/agateau/pixelwheels/releases/download/1.0.1/pixelwheels-itchio-1.0.1.apk',archive)
if hashlib.sha256(archive.read_bytes()).hexdigest()!='78fe17b60412358cb3b0b9e0052df3c9a8e2b42359bdca6d56a05982eb5a9a12':
    raise SystemExit('Pixel Wheels official APK checksum mismatch')
with zipfile.ZipFile(archive) as z:
    for entry in z.infolist():
        if entry.filename.startswith('assets/') and not entry.is_dir():
            target=source/'android'/entry.filename
            target.parent.mkdir(parents=True,exist_ok=True)
            # Refuse to overwrite changed source assets.
            data=z.read(entry)
            if target.exists() and target.read_bytes()!=data:
                status=subprocess.check_output(['git','-C',str(source),'status','--porcelain','--',str(target.relative_to(source))],text=True)
                if status.strip():raise SystemExit('Preserve changed asset: '+str(target))
            target.write_bytes(data)
for name in ('LICENSE.GPL-3','LICENSE.Apache-2.0','LICENSE.CC-BY-SA'):
    shutil.copy2(source/name,ROOT/'theme/licenses'/('PixelWheels-'+name+'.txt'))
print('Pixel Wheels source/data prepared; run embed-pixelwheels.py')
