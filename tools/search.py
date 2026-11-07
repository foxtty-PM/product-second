import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.common import records
from tools.signals import load,get,parts
from tools.runtime import GuardError
ROOT=Path(__file__).resolve().parents[1]
def resolve(root,id):
    root=Path(root).resolve()
    if id.startswith('SIG-'):return {'kind':'csv_row','path':'signals/signals.csv','row':get(root,id)}
    matches=[(p,m) for p,m in records(root) if m['id']==id]
    if len(matches)!=1:raise GuardError('unknown/ambiguous ID')
    p,m=matches[0];return {'kind':'markdown','path':str(p.relative_to(root)),'metadata':m}
def search(root,query,include_demo=False,related_id=None):
    root=Path(root).resolve();terms=query.casefold().split();out=[]
    if not terms and related_id is None:return []
    for p,m in records(root):
        if m.get('demo') and not include_demo:continue
        if m.get('status') in ('retired','superseded'):continue
        if related_id is not None:continue
        text=p.read_text().casefold()
        if all(t in text for t in terms):out.append({'kind':'markdown','id':m['id'],'path':str(p.relative_to(root))})
    rows,h=load(root)
    for r in rows:
        if related_id is not None and related_id not in parts(r['related_ids']):continue
        if all(t in ' '.join(r.values()).casefold() for t in terms):out.append({'kind':'csv_row','id':r['signal_id'],'path':'signals/signals.csv','row':r})
    return out[:20]
if __name__=='__main__':
    import argparse
    a=argparse.ArgumentParser();a.add_argument('query');a.add_argument('--resolve',action='store_true');a.add_argument('--related');a.add_argument('--include-demo',action='store_true');args=a.parse_args()
    print(json.dumps(resolve(ROOT,args.query) if args.resolve else search(ROOT,args.query,args.include_demo,args.related),ensure_ascii=False,indent=2))
