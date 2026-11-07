import csv,io,json,os,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.common import records
from tools.signals import load,parts
ROOT=Path(__file__).resolve().parents[1]
SCOPES=['knowledge','knowledge/domains','knowledge/product','knowledge/product/features','knowledge/product/interfaces','knowledge/product/systems','knowledge/product/integrations','knowledge/metrics','knowledge/decisions','knowledge/sources','ideas','tasks','backlog']
def build(root=ROOT):
    root=Path(root).resolve();nodes=records(root,True);registry={};edges=[]
    for p,m in nodes:
        if any(k not in m for k in ('title','status','demo')):raise ValueError(f'card needs title/status/demo: {p.relative_to(root)}')
        if m['id'] in registry:raise ValueError('duplicate ID')
        registry[m['id']]={'kind':'markdown','path':str(p.relative_to(root)),'entity_type':m['entity_type']}
    signals,h=load(root)
    for row in signals:
        if row['signal_id'] in registry:raise ValueError('duplicate SIG ID')
        registry[row['signal_id']]={'kind':'csv_row','path':'signals/signals.csv','key_column':'signal_id','key':row['signal_id'],'entity_type':'signal'}
        edges += [(row['signal_id'],'relates_to',id) for id in parts(row['related_ids'])]
        edges += [(row['signal_id'],'actioned_as',ref) for ref in parts(row['action_ref']) if ref in registry]
    for p,m in nodes:
        edges += [(m['id'],l['rel'],l['to']) for l in m.get('links',[])]
        edges += [(m['id'],'supported_by',s) for s in m.get('signal_refs',[])]
    for a,rel,b in edges:
        if b not in registry:raise ValueError('dangling ID '+b)
    for scope in SCOPES:
        base=root/scope;base.mkdir(parents=True,exist_ok=True);lines=['# Generated index '+scope,'4.2.0; not manual state. DEMO synthetic, not real evidence.','']
        if scope=='knowledge':
            lines += [f'- [{s}]({s}/INDEX.md)' for s in ['domains','product','metrics','decisions','sources']]
            lines += ['- [Signals contract](../signals/README.md)']
        else:
            for p,m in nodes:
                if base in p.parents:lines.append(f"- [{m['id']}]({os.path.relpath(p,base)}) · {m['title']} · {m['status']} · DEMO={m['demo']}")
        (base/'INDEX.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    target=root/'knowledge/graph';target.mkdir(parents=True,exist_ok=True)
    b=io.StringIO();w=csv.writer(b);w.writerow(['from','rel','to']);w.writerows(edges)
    (target/'edges.csv').write_text(b.getvalue(),encoding='utf-8')
    (target/'id-registry.json').write_text(json.dumps(registry,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    from tools.backlog import sync
    backlog=sync(root)
    return {'nodes':len(nodes),'signals':len(signals),'backlog':backlog}
if __name__=='__main__':print(json.dumps(build()))
