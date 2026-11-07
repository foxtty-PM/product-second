"""Product backlog: cards stay canonical, backlog.csv and VIEW.md are generated. Coordinator writer for cooperating callers, not OS auth."""
import copy,csv,datetime as dt,hashlib,html,io,json,re,sys
from collections import Counter
from pathlib import Path
from urllib.parse import quote,urlsplit
from zoneinfo import ZoneInfo
import jsonschema,yaml
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.common import records,digest
from tools.runtime import GuardError,file_lock,atomic_replace,check_idea_transition
from tools.signals import load as load_signals,parts,_date
TABLE='backlog/backlog.csv';VIEW='backlog/VIEW.md';META='backlog/backlog.meta.json'
JOURNAL='state/backlog.transaction.json';RECEIPTS='state/backlog.operations.json'
COLUMNS={'title':'Title','parent_title':'Parent','priority':'Priority','stage':'Stage','approved':'Approved','next_gate':'Next approval','gate_tasks':'Current gate tasks','change_note':'Last change','changed_at':'When','changed_by':'Updated by',
'clickup_docs':'ClickUp documents','dev_knowledge_docs':'Development knowledge documents','id':'ID','item_type':'Type','summary':'Summary','domains':'Domain','features':"Related features",'parent_id':'Parent ID','path':'Path','queue_rank':'Queue rank','priority_reason':'Priority reason','stage_code':'Stage code','work_status':'Work status','outcome':'Outcome','next_gate_codes':'Next gate codes','gate_task_states':'Gate task states','gate_task_ids':'Gate task IDs','dossier':'Dossier','artifacts':'Artifacts','signals':'Signals','value':'Value','measurement':'Measurement','remainder':'Remaining work','blockers':'Blockers','defer_reason':'Deferral reason','revisit':'Revisit date or condition','revision':'Dossier revision','demo':'DEMO'}
DOCUMENT_FIELDS=('clickup_docs','dev_knowledge_docs')
COMPACT=list(COLUMNS)[:12]
RESOLVED={'approved','inherited','not_applicable'}
OWNER_DECISIONS={'approved','changes_requested','rejected'}
CLOSED_TASKS={'done','dropped'}
OPEN_BACKLOG={'deferred','due'}
IDEA_FIELDS={'title','summary','priority','queue_rank','priority_reason','remainder','blockers','value','artifact_refs','item_type','work_status',*DOCUMENT_FIELDS}
TASK_FIELDS={'status','title','summary','priority','gate_codes','expected_result','gate_criteria','result_ref'}
VALUE_KEYS=('expected_value','metric','target','data_source','deadline','evaluation_rule')
def _json(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def _sha(data):return hashlib.sha256(data).hexdigest()
def _now():return dt.datetime.now(dt.timezone.utc).isoformat()
def _moment(value):return dt.datetime.fromisoformat(value.replace('Z','+00:00'))
def _local(value):return dt.datetime.fromisoformat(value.replace('Z','+00:00')).astimezone(ZoneInfo('Europe/Kyiv')).strftime('%Y-%m-%d %H:%M') if value else ''
def _safe(s):return "'"+s if s.lstrip().startswith(('=','+','-','@')) or s.startswith(('\t','\r')) else s
def _document_url(url):
    try:
        parsed=urlsplit(url)
        if parsed.scheme not in ('http','https') or not parsed.hostname or parsed.username is not None or parsed.password is not None or re.search(r'[\s<>\\\x00-\x1f\x7f]',url):raise ValueError('unsupported document URL')
        parsed.port
    except (ValueError,TypeError) as e:raise GuardError('absolute HTTP(S) document URL without credentials required') from e
    return url

class State:
    def __init__(self,root):
        self.root=Path(root).resolve();self.cards={};self.pending=[];self.documents=[]
        for p,m in records(self.root,True):
            if m['id'] in self.cards:raise GuardError('duplicate ID '+m['id'])
            self.cards[m['id']]=(p,m)
        self.vocab=_json(self.root/'workflows/gates.json');self.routes=_json(self.root/'workflows/routes.json')
    def of(self,kind):return [m for p,m in self.cards.values() if m['entity_type']==kind]
    def card(self,id):return self.cards[id][1]

def parent_of(m):
    found=[l for l in m['links'] if l['rel'] in ('iteration_of','member_of')]
    if len(found)>1:raise GuardError('conflicting parents: '+m['id'])
    return found[0]['to'] if found else None
def ancestors(s,m):
    out=[];up=parent_of(m)
    while up is not None:
        if up in out or up==m['id']:raise GuardError('hierarchy cycle: '+m['id'])
        if up not in s.cards or s.card(up)['entity_type']!='idea':raise GuardError('unknown parent: '+up)
        out.append(up);up=parent_of(s.card(up))
    return out
def latest(m):
    out={}
    for e in m.get('gate_log') or []:
        out[e['gate']]=e
        for g in e.get('invalidates',[]):out[g]={'gate':g,'decision':'stale','at':e['at'],'reason':'Reapproval after '+e['gate']}
    return out
def evidence(m):
    return digest({k:m.get(k) for k in ('summary','work_type','feature_ids','links','value','risk_profile','scale','route','item_type')})
def _gate_tasks(s,m,gates):
    return [t for t in s.of('task') if t['idea_id']==m['id'] and set(t.get('gate_codes') or [])&set(gates)]
def _task_evidence(t):
    return digest({k:t.get(k) for k in ('status','gate_codes','expected_result','gate_criteria','result_ref','input_manifest')})
def _snapshot(s,m,gates):
    tasks=_gate_tasks(s,m,gates)
    refs=list(dict.fromkeys([*(m.get('artifact_refs') or []),*(t['result_ref'] for t in tasks if t.get('result_ref'))]))
    artifacts={}
    for ref in refs:
        p=_relative(s.root,ref,('artifacts/','ideas/','tasks/'))
        if not p.is_file():raise GuardError('missing gate artifact: '+ref)
        artifacts[ref]=_sha(p.read_bytes())
    return {'dossier_hash':evidence(m),'dossier_artifact_refs':list(m.get('artifact_refs') or []),'artifact_revisions':artifacts,'task_revisions':{t['id']:_task_evidence(t) for t in tasks}}
def current(s,m,seen=None):
    out=latest(m);seen=set(seen or ())
    if m['id'] in seen:raise GuardError('inherited decision cycle')
    seen.add(m['id'])
    for g,e in list(out.items()):
        if e.get('decision') not in RESOLVED:continue
        reason=None
        if e.get('dossier_hash')!=evidence(m):reason='Dossier inputs changed or snapshot is missing'
        if set(e.get('dossier_artifact_refs') or [])!=set(m.get('artifact_refs') or []):reason='Dossier document set changed'
        for ref,expected in e.get('artifact_revisions',{}).items():
            p=_relative(s.root,ref,('artifacts/','ideas/','tasks/'))
            if not p.is_file() or _sha(p.read_bytes())!=expected:reason='Artifact changed: '+ref
        if e.get('task_revisions',{})!={t['id']:_task_evidence(t) for t in _gate_tasks(s,m,e.get('joint_with') or [g])}:reason='Gate preparation changed'
        if e['decision']=='inherited':
            source=s.cards.get(e.get('inherited_from'),(None,None))[1]
            parent=current(s,source,seen).get(g,{}) if source else {}
            if parent.get('decision')!='approved' or e.get('inherited_decisions',{}).get(g)!=digest(parent):reason='Parent decision changed'
        if reason:out[g]={**e,'decision':'stale','reason':reason}
    positions={e['gate']:i for i,e in enumerate(m.get('gate_log') or [])}
    preceding=[]
    for stage in s.routes[m['route']]:
        for group in s.vocab['routes'][m['route']].get(stage,[]):
            for g in group:
                e=out.get(g,{})
                if e.get('decision') in RESOLVED and any(out.get(prior,{}).get('decision') not in RESOLVED or positions.get(prior,-1)>positions.get(g,-1) for prior in preceding):
                    out[g]={**e,'decision':'stale','reason':'Reapproval required after preceding gates'}
            preceding.extend(group)
    return out

def route_gates(s,m):return {g for groups in s.vocab['routes'][m['route']].values() for group in groups for g in group}
def next_gates(s,m):
    if m['route']=='L_parent' and m['status']=='delivering' and m['work_status']!='closed':
        plan=current(s,m).get('G3',{})
        for child in s.of('idea'):
            e=current(s,child).get('G7',{})
            if parent_of(child)==m['id'] and e.get('decision')=='approved' and e.get('choice')=='adjust_plan' and (not plan.get('at') or _moment(plan['at'])<=_moment(e['at'])):return ['G3'],'pending'
    if m['work_status']=='closed' or m['status']=='knowledge':return [],'closed'
    route=s.routes[m['route']];plan=s.vocab['routes'][m['route']];last=current(s,m);at=route.index(m['status'])
    for n,stage in enumerate(route):
        for group in plan.get(stage,[]):
            open_=[g for g in group if last.get(g,{}).get('decision') not in RESOLVED]
            if open_:return open_,'pending'
        if n>=at and plan.get(stage):return [],'await_transition'
    return [],'no_own_gate'
def _seq(m):return int(m['id'].rsplit('.',1)[1]) if '.' in m['id'] else 0
def siblings(s,m):
    up=parent_of(m);return sorted((x for x in s.of('idea') if x['item_type']=='iteration' and parent_of(x)==up),key=_seq)
def entry_block(s,m):
    parent=s.card(parent_of(m));plan=current(s,parent).get('G3',{})
    if plan.get('decision') not in RESOLVED:return f"Iteration plan {parent['id']} is not approved"
    older=[x for x in siblings(s,m) if _seq(x)<_seq(m)]
    if not older:return None
    g7=current(s,older[-1]).get('G7',{});choice=g7.get('choice')
    if g7.get('decision')!='approved':return f"Awaiting G7 of previous iteration {older[-1]['id']}"
    if choice=='next_iteration' or (choice=='adjust_plan' and _moment(plan['at'])>_moment(g7['at'])):return None
    return f"G7 {older[-1]['id']}: {choice}"
def stopped(s,m):return m['item_type']=='iteration' and any(latest(x).get('G7',{}).get('choice')=='stop' for x in siblings(s,m) if _seq(x)<_seq(m))
def value_complete(m):
    v=m.get('value') or {}
    return all(v.get(k) for k in VALUE_KEYS) and bool(v.get('baseline') or v.get('baseline_missing_reason'))
def _owner(s,b):
    src=s.cards.get(b['source_id'],(None,None))[1]
    if src is None:raise GuardError('unknown backlog source: '+b['id'])
    return src['idea_id'] if src['entity_type']=='task' else src['id']

def validate(s):
    sigids={r['signal_id'] for r in load_signals(s.root)[0]}
    ideas={m['id']:m for m in s.of('idea')};ranks=set()
    for path,m in s.cards.values():
        _schema(s.root,m)
        if s.root not in path.resolve().parents or path.is_symlink():raise GuardError('card path escape')
        for sig in m['signal_refs']:
            if sig not in sigids:raise GuardError('unknown signal reference: '+sig)
        for link in m['links']:
            if link['to'] not in s.cards and link['to'] not in sigids:raise GuardError('unknown linked ID: '+link['to'])
        for fid in m.get('feature_ids',[]):
            if fid not in s.cards or s.card(fid)['entity_type']!='feature':raise GuardError('unknown feature: '+fid)
            if not any(l['rel']=='affects' and l['to']==fid for l in m['links']):raise GuardError('missing affects link: '+fid)
    for m in ideas.values():
        for field in DOCUMENT_FIELDS:
            for document in m.get(field,[]):
                if not document['title'].strip():raise GuardError('document title required')
                _document_url(document['url'])
        if m['route'] not in s.vocab['routes'] or m['status'] not in s.routes[m['route']]:raise GuardError('stage outside route: '+m['id'])
        ancestors(s,m);parent=parent_of(m);rels={l['rel'] for l in m['links']}
        if 'iteration_of' in rels and (m['route']!='iteration' or ideas[parent]['route']!='L_parent'):raise GuardError('iteration route needs L_parent')
        if m['route']=='iteration' and m['item_type']!='iteration':raise GuardError('iteration route needs iteration item')
        if (m['item_type']=='iteration')!=('iteration_of' in rels):raise GuardError('iteration needs iteration_of and vice versa: '+m['id'])
        if 'member_of' in rels and (m['item_type'] not in ('feature','improvement','bug') or ideas[parent]['item_type']!='initiative'):raise GuardError('member_of links feature/improvement/bug to initiative: '+m['id'])
        rank=m.get('queue_rank')
        if rank is not None and m['work_status']!='closed':
            if rank in ranks:raise GuardError(f'duplicate queue_rank {rank}')
            ranks.add(rank)
    for t in s.of('task'):
        idea=ideas.get(t['idea_id'])
        if idea is None:raise GuardError('task without idea: '+t['id'])
        if not any(l['rel']=='implements' and l['to']==t['idea_id'] for l in t['links']):raise GuardError('task needs implements link: '+t['id'])
        if set(t.get('gate_codes') or [])-route_gates(s,idea):raise GuardError('gate outside route: '+t['id'])
    opened={b['source_id'] for b in s.of('backlog') if b['status'] in OPEN_BACKLOG}
    refs=set()
    for b in s.of('backlog'):
        _owner(s,b)
        if b['status'] in OPEN_BACKLOG:
            if b['source_id'] in refs:raise GuardError('duplicate open backlog reference: '+b['source_id'])
            refs.add(b['source_id'])
    for m in ideas.values():
        if (m['status']=='knowledge')!=(m['work_status']=='closed'):raise GuardError('knowledge and closed must match: '+m['id'])
        for entry in m.get('gate_log') or []:_date(entry['at'],True,True)
        if m.get('changed_at'):_date(m['changed_at'],True,True)
        if (m['work_status']=='paused')!=(m['id'] in opened):raise GuardError('paused idea and open backlog reference must match: '+m['id'])

def _approved(s,m):
    names=s.vocab['labels']['gate'];out=[]
    for g,e in current(s,m).items():
        name=f'{g} {names[g]}';when=_local(e['at'])[:10]
        if e['decision']=='approved':out.append(f"{name}: approved {when}"+(' jointly '+'+'.join(e['joint_with']) if e.get('joint_with') else '')+(f" (conditions: {e['conditions']})" if e.get('conditions') else ''))
        elif e['decision']=='inherited':out.append(f"{name}: inherited from {e['inherited_from']}")
        elif e['decision']=='not_applicable':out.append(f"{name}: not applicable ({e['reason']})")
        elif e['decision']=='rejected':out.append(f'{name}: rejected {when}')
        elif e['decision']=='stale':out.append(f"{name}: requires reapproval ({e['reason']})")
    return '; '.join(out)
def _next(s,m,gates,state):
    if state=='closed':return '—'
    if state=='await_transition':return 'Stage gates passed: awaiting transition'
    if state=='no_own_gate':return 'No own gate'
    names=s.vocab['labels']['gate'];last=current(s,m);text=' + '.join(names[g] for g in gates)
    for g in gates:
        e=last.get(g,{})
        if e.get('decision')=='changes_requested':return f"{text} (changes requested: {e.get('reason') or e['quote']})"
        if e.get('decision')=='stale':return f"{text} ({e['reason']})"
        if e.get('decision')=='rejected':return f'{text} (rejected: awaiting closure)'
    return text
def _measurement(s,m):
    links=[l['to'] for l in m['links'] if l['rel']=='measured_by']
    if not m.get('value'):return ('; '.join(links)) if links else ('Missing: required before G5' if m['work_type']=='product_feature' else 'Acceptance criteria in dossier')
    v=m['value'];base=f"baseline: {v['baseline']}" if v.get('baseline') else f"baseline missing: {v.get('baseline_missing_reason','')}"
    return '; '.join([f"metric: {v['metric']}",base,f"target: {v['target']}",f"source: {v['data_source']}",f"deadline: {v['deadline']}",f"evaluation: {v['evaluation_rule']}",*links])

def _row(s,m,sig):
    labels=s.vocab['labels'];parent=parent_of(m);gates,state=next_gates(s,m)
    tasks=sorted((t for t in s.of('task') if t['idea_id']==m['id']),key=lambda t:t['id'])
    current=[t for t in tasks if set(t.get('gate_codes') or [])&set(gates)]
    deferred=[b for b in s.of('backlog') if _owner(s,b)==m['id']];active=[b for b in deferred if b['status'] in OPEN_BACKLOG]
    stamp=max([m,*tasks,*deferred],key=lambda c:dt.datetime.fromisoformat(c['changed_at'].replace('Z','+00:00')) if c.get('changed_at') else dt.datetime.min.replace(tzinfo=dt.timezone.utc))
    count=Counter(t['status'] for t in current)
    states='; '.join(f"{labels['task_status'][k]}: {v}" for k,v in sorted(count.items())) if current else ('No tasks: readiness unconfirmed' if gates else '')
    features=[s.card(f) for f in m['feature_ids']]
    domains=[l['to'] for l in m['links'] if l['rel']=='belongs_to_domain']+[f['domain_id'] for f in features]
    block=[*(m.get('blockers') or [])]
    if m['route']=='iteration' and m['status']=='planned' and (text:=entry_block(s,m)):block.append(text)
    return {**{field:copy.deepcopy(m.get(field,[])) for field in DOCUMENT_FIELDS},'title':m['title'],'parent_title':s.card(parent)['title'] if parent else '','priority':labels['priority'][m['priority']],'stage':labels['stage'][m['status']],'approved':_approved(s,m),'next_gate':_next(s,m,gates,state),'gate_tasks':'; '.join(t['title'] for t in current),'change_note':stamp.get('change_note','No record'),'changed_at':_local(stamp.get('changed_at','')),'changed_by':stamp.get('changed_by',''),
    'id':m['id'],'item_type':labels['item_type'][m['item_type']],'summary':m['summary'],'domains':'; '.join(s.card(d)['title'] for d in dict.fromkeys(domains)),'features':'; '.join(f['title'] for f in features),'parent_id':parent or '','path':' → '.join([*(s.card(x)['title'] for x in reversed(ancestors(s,m))),m['title']]),'queue_rank':str(m.get('queue_rank') or ''),'priority_reason':m.get('priority_reason',''),'stage_code':m['status'],'work_status':labels['work_status'][m['work_status']],'outcome':labels['outcome'].get(m['outcome'],''),'next_gate_codes':'+'.join(gates),'gate_task_states':states,'gate_task_ids':'; '.join(t['id'] for t in current),'dossier':s.cards[m['id']][0].relative_to(s.root).as_posix(),'artifacts':'; '.join(dict.fromkeys([*(m.get('artifact_refs') or []),*(t['result_ref'] for t in tasks if t.get('result_ref'))])),'signals':'; '.join(dict.fromkeys([*m['signal_refs'],*sig.get(m['id'],[])])),'value':(m.get('value') or {}).get('expected_value',''),'measurement':_measurement(s,m),'remainder':m.get('remainder',''),'blockers':'; '.join(block),'defer_reason':'; '.join(b['reason'] for b in active),'revisit':'; '.join(str(b['revisit']) for b in active),'revision':str(m['revision']),'demo':'yes' if m['demo'] else ''}

def render(s):
    validate(s);sig={}
    for r in load_signals(s.root)[0]:
        for id in parts(r['related_ids']):sig.setdefault(id,[]).append(r['signal_id'])
    order=list(s.vocab['labels']['priority'])
    ideas=sorted(s.of('idea'),key=lambda m:(m['work_status']=='closed',m.get('queue_rank') or 10**9,order.index(m['priority']),m['id']))
    return [_row(s,m,sig) for m in ideas]
def _relative(root,relative,prefixes):
    if not isinstance(relative,str) or Path(relative).is_absolute():raise GuardError('relative workspace path required')
    p=(Path(root)/relative).resolve()
    if Path(root).resolve() not in p.parents or not p.relative_to(root).as_posix().startswith(prefixes):raise GuardError('protected/escaping path')
    return p
def fingerprint(root):
    root=Path(root).resolve();cards=records(root,True)
    paths={p for p,m in cards}|{root/'workflows/gates.json',root/'workflows/routes.json',root/'workflows/task-transitions.json',root/'signals/signals.csv'}
    paths.update((root/'schemas').glob('*.json'))
    for p,m in cards:
        refs=[*(m.get('artifact_refs') or []),*([m['result_ref']] if m.get('result_ref') else [])]
        for ref in refs:paths.add(_relative(root,ref,('artifacts/','ideas/','tasks/')))
    return digest(sorted((p.relative_to(root).as_posix(),_sha(p.read_bytes()) if p.is_file() else 'missing') for p in paths))
def _bytes(rows):
    buf=io.StringIO(newline='');w=csv.writer(buf);w.writerow(COLUMNS.values());w.writerows([_safe('\n'.join(d['url'] for d in r[k]) if k in DOCUMENT_FIELDS else r[k]) for k in COLUMNS] for r in rows)
    return buf.getvalue().encode('utf-8-sig')
def _view(rows):
    esc=lambda v:html.escape(v,quote=False).replace('\\','\\\\').replace('[','\\[').replace(']','\\]').replace('|','\\|').replace('\n',' ')
    def cell(row,key):
        if key=='title':return f"[{esc(row['title'])}](../{row['dossier']})"
        if key in DOCUMENT_FIELDS:
            return '; '.join(f"[{esc(document['title'])}]({quote(document['url'],safe=':/?#[]@!$&*+,;=%')})" for document in row[key])
        return esc(row[key])
    lines=['# Product backlog','Generated by tools/backlog.py; do not edit. Canonical cards: ideas/, tasks/, backlog/. All fields: backlog.csv.','','|'+'|'.join(COLUMNS[k] for k in COMPACT)+'|','|'+'---|'*len(COMPACT)]
    for r in rows:lines.append('|'+'|'.join(cell(r,k) for k in COMPACT)+'|')
    return '\n'.join(lines)+'\n'
def status(root):
    root=Path(root).resolve();table,view,meta=root/TABLE,root/VIEW,root/META
    if (root/JOURNAL).exists():return {'fresh':False,'reason':'canonical transaction pending; retry same operation or reconcile'}
    if not all(p.is_file() for p in (table,view,meta)):return {'fresh':False,'reason':'not generated, run sync'}
    try:
        stored=_json(meta)
        fresh=(stored['source_hash']==fingerprint(root) and stored['table_hash']==_sha(table.read_bytes()) and stored['view_hash']==_sha(view.read_bytes()))
        return {'fresh':fresh,'reason':'' if fresh else 'sources or generated views changed, run sync'}
    except (ValueError,KeyError,OSError,GuardError) as e:return {'fresh':False,'reason':'invalid view metadata: '+str(e)}
def _write(s):
    before=fingerprint(s.root);s=State(s.root);rows=render(s);data=_bytes(rows);view=_view(rows).encode('utf-8')
    atomic_replace(s.root/TABLE,data);atomic_replace(s.root/VIEW,view)
    if fingerprint(s.root)!=before:raise GuardError('sources changed during backlog generation; retry sync')
    atomic_replace(s.root/META,(json.dumps({'source_hash':before,'table_hash':_sha(data),'view_hash':_sha(view),'rows':len(rows)},indent=2)+'\n').encode('utf-8'))
    return {'rows':len(rows),'fresh':True,'reason':''}
def sync(root):
    root=Path(root).resolve()
    with file_lock(root,TABLE):
        _recover(root)
        return _write(State(root))
def rows(root,stage=None,parent=None):return [r for r in render(State(root)) if (stage is None or r['stage_code']==stage) and (parent is None or r['parent_id']==parent)]
def get(root,id):
    row=next((r for r in rows(root) if r['id']==id),None)
    if row is None:raise GuardError('unknown backlog row')
    return row

def _schema(root,m):
    try:jsonschema.Draft202012Validator(_json(Path(root)/'schemas'/f"{m['entity_type'] if m['entity_type'] in ('idea','task','feature','backlog') else 'node'}.schema.json")).validate(m)
    except jsonschema.ValidationError as e:raise GuardError('schema: '+e.message)
def _idea(m):
    if m['entity_type']!='idea':raise GuardError('op needs idea card')

def _fields(s,m,q,actor,stamp):
    _idea(m);fields=q.get('fields')
    if not isinstance(fields,dict) or not fields or set(fields)-IDEA_FIELDS:raise GuardError('allowed fields required')
    if 'work_status' in fields and not {fields['work_status'],m['work_status']}<={'active','blocked'}:raise GuardError('use defer/resume/stage for this work_status')
    m.update(fields)
def _parent(s,m,q,actor,stamp):
    _idea(m)
    if m['item_type']=='iteration':raise GuardError('iteration parent is iteration_of')
    m['links']=[l for l in m['links'] if l['rel']!='member_of']+([{'rel':'member_of','to':q['parent']}] if q.get('parent') else [])
def _gate(s,m,q,actor,stamp):
    _idea(m);gates,decision=q.get('gates'),q.get('decision');names=s.vocab['labels']['gate']
    if not isinstance(gates,list) or not gates or len(set(gates))!=len(gates) or set(gates)-set(names):raise GuardError('known gates required')
    pending=next_gates(s,m)[0];last=current(s,m)
    for g in gates:
        if decision in ('approved','rejected','not_applicable') and g not in pending:raise GuardError(g+' is not the next gate')
        if decision=='changes_requested' and g not in pending and last.get(g,{}).get('decision') not in RESOLVED:raise GuardError(g+' is not open for changes')
    entry={'decision':decision,'at':q.get('at') or _now(),'recorded_by':actor,'input_revision':m['revision'],**(_snapshot(s,m,gates) if decision in RESOLVED else {})};_date(entry['at'],True,True)
    if decision in ('inherited','not_applicable') and 'G7' in gates and m['work_type']=='product_feature':raise GuardError('product value G7 needs own outcome decision')
    for ref,expected in (q.get('artifact_revisions') or {}).items():
        p=_relative(s.root,ref,('artifacts/','ideas/','tasks/'))
        if not p.is_file() or _sha(p.read_bytes())!=expected:raise GuardError('stale artifact revision: '+ref)
    if decision=='approved' and m['risk_profile'] in ('high','critical') and q.get('human_risk_review') is not True:raise GuardError('human risk review required')
    if q.get('artifact_revisions'):entry.setdefault('artifact_revisions',{}).update(q['artifact_revisions'])
    if decision in OWNER_DECISIONS:
        if not q.get('quote') or not q.get('decided_by'):raise GuardError('verbatim quote and decided_by required')
        entry.update(quote=q['quote'],decided_by=q['decided_by'])
    elif decision=='not_applicable':
        if not q.get('reason'):raise GuardError('not_applicable needs reason')
    elif decision=='inherited':
        source=q.get('inherited_from')
        if source not in ancestors(s,m) or any(current(s,s.card(source)).get(g,{}).get('decision')!='approved' for g in gates):raise GuardError('inherited needs approved ancestor decision')
        entry['inherited_from']=source
        entry['inherited_decisions']={g:digest(current(s,s.card(source))[g]) for g in gates}
    else:raise GuardError('unknown gate decision')
    if decision=='changes_requested':
        ordered=[g for stage in s.routes[m['route']] for group in s.vocab['routes'][m['route']].get(stage,[]) for g in group]
        positions=[ordered.index(g) for g in gates if g in ordered]
        entry['invalidates']=[g for g in ordered[min(positions)+1:] if g not in gates and last.get(g,{}).get('decision') in RESOLVED] if positions else []
    for k in ('reason','conditions','choice'):
        if q.get(k):entry[k]=q[k]
    if len(gates)>1:entry['joint_with']=gates
    if decision=='approved' and 'G5' in gates and m['work_type']=='product_feature' and not value_complete(m):raise GuardError('value and measurement required before G5')
    if decision=='approved' and 'G7' in gates:
        kind='iteration' if m['route']=='iteration' else 'single'
        if q.get('choice') not in s.vocab['g7_choices'][kind]:raise GuardError('G7 choice required')
        if q['choice']=='next_iteration' and not [x for x in siblings(s,m) if _seq(x)>_seq(m) and x['status']=='planned']:raise GuardError('no planned next iteration')
    m['gate_log']=[*(m.get('gate_log') or []),*({'gate':g,**copy.deepcopy(entry)} for g in gates)]
def _stage(s,m,q,actor,stamp):
    _idea(m);to,outcome=q.get('to'),q.get('outcome');killed=to=='knowledge' and outcome=='killed';last=current(s,m)
    route=s.routes[m['route']];at=route.index(m['status'])
    own=[g for stage in route[:at+1] for group in s.vocab['routes'][m['route']].get(stage,[]) for g in group]
    if not killed and to=='dev' and m['work_type']=='product_feature' and not value_complete(m):raise GuardError('value and measurement required before dev')
    if not killed and to=='knowledge' and m['work_type']=='product_feature' and m['route'] not in ('L_parent','XL','discovery'):
        if m['status']!='validating' or current(s,m).get('G7',{}).get('decision')!='approved':raise GuardError('own G7 outcome decision required')
        if outcome not in ('validated','refuted','inconclusive'):raise GuardError('product outcome needs value evaluation')
    passed=all(last.get(g,{}).get('decision') in RESOLVED for g in own)
    for g in own:
        for ref,expected in last.get(g,{}).get('artifact_revisions',{}).items():
            p=_relative(s.root,ref,('artifacts/','ideas/','tasks/'))
            if not p.is_file() or _sha(p.read_bytes())!=expected:passed=False
    halted=any(e['decision']=='rejected' for e in last.values()) or stopped(s,m)
    children=[x for x in s.of('idea') if x['item_type']=='iteration' and parent_of(x)==m['id']]
    relevant=[t for t in s.of('task') if t['idea_id']==m['id'] and (not t.get('gate_codes') or set(t['gate_codes'])&set(own))]
    exclusions=q.get('task_exclusions') or {}
    taskless=(q.get('readiness') or {}).get('taskless_reason')
    tasks_closed=all((t['status']=='done' and (not t.get('gate_codes') or t.get('result_ref') and _relative(s.root,t['result_ref'],('artifacts/','ideas/','tasks/')).is_file())) or (t['status']=='dropped' and isinstance(exclusions.get(t['id']),str) and exclusions[t['id']].strip()) for t in relevant) if relevant else bool(isinstance(taskless,str) and taskless.strip())
    ready={**(q.get('readiness') or {}),'tasks_closed':tasks_closed,'gate_approved':passed or (killed and halted),'no_blockers':killed or not m.get('blockers'),'children_closed':all(x['work_status']=='closed' for x in children),'input_hash':digest(m)}
    if m['route']=='iteration' and m['status']=='planned' and to=='bdr' and (text:=entry_block(s,m)):raise GuardError(text)
    result=check_idea_transition(s.root,m,to,m['revision'],ready,outcome)
    result['transition_log']=[*(m.get('transition_log') or []),{'from':m['status'],'to':to,'recorded_by':actor,'at':_now(),'taskless_reason':taskless,'task_exclusions':exclusions}]
    m.clear();m.update(result)
def _task(s,m,q,actor,stamp):
    if m['entity_type']!='task':raise GuardError('op needs task card')
    fields=q.get('fields')
    if not isinstance(fields,dict) or not fields or set(fields)-TASK_FIELDS:raise GuardError('allowed fields required')
    moves=_json(s.root/'workflows/task-transitions.json')
    if fields.get('status',m['status'])!=m['status'] and fields['status'] not in moves[m['status']]:raise GuardError('invalid task transition')
    m.update(fields)
def _touch(s,card,q,actor,stamp):
    card.update(changed_at=_now(),changed_by=actor,change_note=q['note'],last_op=stamp);_schema(s.root,card)
    s.cards[card['id']]=(s.cards[card['id']][0] if card['id'] in s.cards else s.root/'backlog'/f"{card['id']}.md",card);s.pending.append(card['id'])
def _new_backlog_id(s):
    return 'BL-%04d'%(max([int(x.group(1)) for b in s.of('backlog') if (x:=re.fullmatch(r'BL-(\d+)',b['id']))]+[0])+1)
def _defer(s,m,q,actor,stamp):
    _idea(m)
    if m['work_status'] not in ('active','blocked'):raise GuardError('only open idea can be deferred')
    if not q.get('reason') or not q.get('revisit'):raise GuardError('defer needs reason and revisit')
    linked=[b for b in s.of('backlog') if b['source_id']==m['id']]
    if not any(b.get('last_op',{}).get('id')==stamp['id'] for b in linked):
        old=next((b for b in linked if b['status']!='closed'),None)
        card=copy.deepcopy(old) if old else {'schema_version':m['schema_version'],'id':_new_backlog_id(s),'entity_type':'backlog','title':'Deferred: '+m['title'],'revision':0,'status':'deferred','demo':m['demo'],'aliases':[],'summary':q['reason'],'sources':[],'links':[{'rel':'depends_on','to':m['id']}],'signal_refs':[],'trackerStatus':{'type':'pm-backlog'},'priority':m['priority'],'source_id':m['id']}
        card.update(status='deferred',reason=q['reason'],revisit=str(q['revisit']),defer_count=old.get('defer_count',1)+1 if old else 1,revision=card['revision']+1)
        _touch(s,card,q,actor,stamp)
    m['work_status']='paused'
def _resume(s,m,q,actor,stamp):
    _idea(m)
    if m['work_status']!='paused':raise GuardError('idea is not paused')
    linked=[b for b in s.of('backlog') if b['source_id']==m['id']]
    opened=[b for b in linked if b['status'] in OPEN_BACKLOG]
    if not opened and not any(b.get('last_op',{}).get('id')==stamp['id'] for b in linked):raise GuardError('no open backlog reference')
    for b in opened:
        card=copy.deepcopy(b);card.update(status='returned',revision=b['revision']+1);_touch(s,card,q,actor,stamp)
    m['work_status']='active'
def _artifact(s,m,q,actor,stamp):
    _idea(m);ref=q.get('path');p=_relative(s.root,ref,('artifacts/',))
    if 'text' in q:
        if not isinstance(q['text'],str) or 'expected_hash' not in q:raise GuardError('artifact text and expected_hash required')
        before=_sha(p.read_bytes()) if p.exists() else None
        if before!=q['expected_hash']:raise GuardError('artifact CAS conflict')
        s.documents.append((p,q['text']))
    elif not p.is_file():raise GuardError('artifact does not exist')
    m['artifact_refs']=list(dict.fromkeys([*(m.get('artifact_refs') or []),ref]))
OPS={'set_fields':_fields,'set_parent':_parent,'gate':_gate,'stage':_stage,'task':_task,'defer':_defer,'resume':_resume,'artifact':_artifact}
def _card_text(p,m):
    body=p.read_text(encoding='utf-8').split('\n---\n',1)[1] if p.exists() else f"\n# {m['title']}\n"
    return '---\n'+yaml.safe_dump(m,allow_unicode=True,sort_keys=False,width=10**6)+'---\n'+body
def _receipts(root):
    p=Path(root)/RECEIPTS
    return _json(p) if p.exists() else {}
def _recover(root):
    """Reconcile after-images against before hashes; never overwrite an unrelated edit."""
    root=Path(root);journal=root/JOURNAL
    if not journal.exists():return
    tx=_json(journal)
    for change in tx['changes']:
        p=_relative(root,change['path'],('ideas/','tasks/','backlog/','artifacts/'))
        actual=_sha(p.read_bytes()) if p.exists() else None
        if actual not in (change['before'],_sha(change['text'].encode('utf-8'))):raise GuardError('transaction conflict: '+change['path'])
    for change in tx['changes']:
        p=_relative(root,change['path'],('ideas/','tasks/','backlog/','artifacts/'))
        if not p.exists() or _sha(p.read_bytes())!=_sha(change['text'].encode('utf-8')):atomic_replace(p,change['text'].encode('utf-8'))
    receipts=_receipts(root);old=receipts.get(tx['op_id'])
    if old and old['hash']!=tx['hash']:raise GuardError('receipt conflict')
    receipts[tx['op_id']]={'hash':tx['hash'],'result':tx['result']}
    atomic_replace(root/RECEIPTS,(json.dumps(receipts,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    journal.unlink()
def _commit(root,changes,stamp,result):
    tx={'op_id':stamp['id'],'hash':stamp['hash'],'result':result,'changes':[]}
    for p,text in changes:
        relative=p.relative_to(root).as_posix();_relative(root,relative,('ideas/','tasks/','backlog/','artifacts/'))
        tx['changes'].append({'path':relative,'before':_sha(p.read_bytes()) if p.exists() else None,'text':text})
    atomic_replace(root/JOURNAL,(json.dumps(tx,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    _recover(root)
def apply(root,payload,actor):
    if actor!='coordinator':raise GuardError('only coordinator backlog writer')
    if not isinstance(payload,dict) or payload.get('op') not in {*OPS,'create'}:raise GuardError('unknown backlog op')
    if not payload.get('id') or not payload.get('op_id') or not payload.get('note') or type(payload.get('expected_revision')) is not int:raise GuardError('id/op_id/note/expected_revision required')
    id=payload['id'];stamp={'id':payload['op_id'],'hash':digest(payload)};root=Path(root).resolve()
    with file_lock(root,TABLE):
        _recover(root);s=State(root);receipts=_receipts(root);old=receipts.get(stamp['id'])
        if old:
            if old['hash']!=stamp['hash']:raise GuardError('op_id reused with different payload')
            result={**old['result'],'applied':False}
        else:
            if payload['op']=='create':
                if id in s.cards or payload['expected_revision']!=0:raise GuardError('create needs new ID and revision zero')
                new=copy.deepcopy(payload.get('card') or {});kind=new.get('entity_type')
                if kind not in ('idea','task') or new.get('id')!=id or not re.fullmatch(('I' if kind=='idea' else 'T')+r'-[A-Z0-9-]+(?:\.[0-9]+)?',id):raise GuardError('create needs matching idea/task ID')
                path=root/('ideas' if kind=='idea' else 'tasks')/(id+'.md')
                if path.exists():raise GuardError('create path exists')
                new['revision']=1
            else:
                if id not in s.cards:raise GuardError('unknown backlog card')
                path,m=s.cards[id]
                if m['revision']!=payload['expected_revision']:raise GuardError('backlog CAS conflict')
                new=copy.deepcopy(m);OPS[payload['op']](s,new,payload,actor,stamp)
                new['revision']=m['revision']+1
            new.update(changed_at=_now(),changed_by=actor,change_note=payload['note'],last_op=stamp)
            _schema(root,new);s.cards[id]=(path,new);validate(s)
            result={'id':id,'revision':new['revision'],'applied':True}
            changes=[(s.cards[extra][0],_card_text(*s.cards[extra])) for extra in s.pending]
            changes.append((path,_card_text(path,new)));changes.extend(s.documents)
            _commit(root,changes,stamp,result)
        try:return {**result,'synced':True,**_write(State(root))}
        except Exception as e:return {**result,'synced':False,'error':str(e),'fresh':False}

if __name__=='__main__':
    import argparse
    a=argparse.ArgumentParser();a.add_argument('--root',default=str(Path(__file__).resolve().parents[1]));sub=a.add_subparsers(dest='cmd',required=True)
    sub.add_parser('status');sub.add_parser('sync');ls=sub.add_parser('list');ls.add_argument('--stage');ls.add_argument('--parent');g=sub.add_parser('get');g.add_argument('id')
    q=sub.add_parser('apply');q.add_argument('--payload',required=True);q.add_argument('--actor',required=True)
    args=a.parse_args()
    if args.cmd=='status':result=status(args.root)
    elif args.cmd=='sync':result=sync(args.root)
    elif args.cmd=='list':result=rows(args.root,args.stage,args.parent)
    elif args.cmd=='get':result=get(args.root,args.id)
    else:result=apply(args.root,_json(args.payload),args.actor)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if isinstance(result,dict) and (result.get('synced') is False or result.get('fresh') is False):sys.exit(1)
