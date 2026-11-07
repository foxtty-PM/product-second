import json,hashlib
from pathlib import Path

def export_pack(root,sources,destination,sensitivity_reviewed=False):
    root=Path(root).resolve();dst=(root/destination).resolve()
    if root not in dst.parents or dst.exists():raise ValueError('new local destination required')
    if not sensitivity_reviewed:raise ValueError('human sensitivity review required, not DLP guarantee')
    snapshots=[]
    for rel in sources:
        p=(root/rel).resolve()
        if root not in p.parents or not p.is_file() or not str(p.relative_to(root)).startswith(('ideas/','artifacts/')):raise ValueError('invalid canonical source')
        snapshots.append((str(p.relative_to(root)),p.read_bytes()))
    dst.mkdir(parents=True);manifest=[]
    for rel,data in snapshots:
        p=dst/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);manifest.append({'path':rel,'sha256':hashlib.sha256(data).hexdigest()})
    (dst/'manifest.json').write_text(json.dumps({'version':'4.2.0','sources':manifest,'external_sent':False},indent=2))
    (dst/'CONTEXT.md').write_text('# Generated pack\n'+'\n'.join('- '+r['path'] for r in manifest)+'\n')
    return manifest
