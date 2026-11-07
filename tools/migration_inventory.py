import argparse,json,hashlib
from pathlib import Path
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('root');args=a.parse_args();root=Path(args.root).resolve();rows=[]
    for p in sorted(root.rglob('*.md')):
        if p.is_symlink() or root not in p.resolve().parents or '.git' in p.parts:continue
        rows.append({'path':str(p.relative_to(root)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'modified':False})
    print(json.dumps({'mode':'read_only_inventory','files':rows},ensure_ascii=False,indent=2))
