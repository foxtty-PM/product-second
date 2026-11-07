import hashlib,json,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SKIP_DIRS={'.git','__pycache__','locks','.nimbalyst-generated'}
SKIP_FILES={'.DS_Store','PACKAGE_MANIFEST.json','settings.local.json'}
def build(root=ROOT):
    root=Path(root).resolve();files={}
    for base,dirs,names in os.walk(root):
        dirs[:]=sorted(d for d in dirs if d not in SKIP_DIRS)
        for name in names:
            if name not in SKIP_FILES:
                p=Path(base)/name;files[p.relative_to(root).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
    manifest={'version':(root/'VERSION').read_text().strip(),'files':dict(sorted(files.items())),'scope':'release_integrity_not_security_signature'}
    (root/'PACKAGE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    return len(files)
if __name__=='__main__':print(json.dumps({'files':build()}))
