import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def verify(root=ROOT):
    root=Path(root).resolve();manifest=json.loads((root/'PACKAGE_MANIFEST.json').read_text());errors=[]
    for rel,h in manifest['files'].items():
        p=(root/rel).resolve()
        if root not in p.parents or not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=h:errors.append(rel)
    return {'status':'PASS' if not errors else 'FAIL','checked':len(manifest['files']),'errors':errors,'scope':'integrity_not_security_signature'}
if __name__=='__main__':
    r=verify();print(json.dumps(r,indent=2));sys.exit(0 if r['status']=='PASS' else 1)
