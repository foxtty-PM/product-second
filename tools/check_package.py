import json,re,sys,tomllib,csv
from pathlib import Path
import yaml,jsonschema
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.common import records,frontmatter
from tools.signals import load,COLUMNS,parts
ROOT=Path(__file__).resolve().parents[1]
REQUIRED=['knowledge/domains','knowledge/product/features','knowledge/product/interfaces','knowledge/product/systems','knowledge/product/integrations','knowledge/metrics','knowledge/decisions','knowledge/sources','knowledge/_drafts','ideas','tasks','backlog','signals','profile','agents','skills','procedures','templates','.nimbalyst/trackers','.claude/agents','.codex/agents','.agents/skills']
TOKENS=['AGENTS.md','KNOWLEDGE_MAP.md','ARCHITECTURE.md','profile/INDEX.md','knowledge/domains/','knowledge/product/features/','ideas/','tasks/','backlog/','signals/signals.csv','signals/README.md']
ID_PREFIX={'domain':'D','feature':'F','idea':'I','task':'T','backlog':'BL','decision':'DEC','metric':'M','integration':'INT','interface':'IF','system':'SYS','source':'SRC'}
SCOPE_DENY={'Edit(signals/signals.csv)','Edit(.claude/**)','Edit(.codex/**)','Edit(policy/**)','Edit(tools/**)','Edit(**/*.py)'}
SHELL_RULES=('Bash(~/.venvs/pm-os/bin/python tools/','Bash(~/.venvs/pm-os/bin/python -m unittest discover -s tests','Bash(shasum -a 256 ')
NON_MODULES=('independent_review','qualified_expert_where_applicable')
def validate_node(root,m):
    typ=m['entity_type'] if m['entity_type'] in ['idea','task','feature','backlog'] else 'node'
    jsonschema.Draft202012Validator(json.loads((Path(root)/'schemas'/f'{typ}.schema.json').read_text())).validate(m)

def check(root=ROOT):
    root=Path(root).resolve();checks=[]
    def mark(name,ok):
        if not ok:raise AssertionError(name)
        checks.append(name)
    for d in REQUIRED:mark('dir:'+d,(root/d).is_dir())
    for p in ['START_HERE.md','SPEC.md','AGENTS.md','ARCHITECTURE.md','KNOWLEDGE_MAP.md','IMPLEMENTATION_STATUS.md','DEPLOYMENT.md','BOOTSTRAP_PROMPT_EN.md','signals/README.md','signals/signals.csv']:
        mark('core:'+p,(root/p).is_file())
    mark('short_core',len((root/'AGENTS.md').read_text().splitlines())<=200)
    mark('claude_import',(root/'CLAUDE.md').read_text().strip()=='@AGENTS.md')
    for p in root.rglob('*.json'):json.loads(p.read_text())
    for p in root.rglob('*.toml'):tomllib.loads(p.read_text())
    for p in (root/'schemas').glob('*.json'):jsonschema.Draft202012Validator.check_schema(json.loads(p.read_text()))
    mark('syntax_schemas',True)
    trackers={}
    for p in (root/'.nimbalyst/trackers').glob('*.yaml'):
        cfg=yaml.safe_load(p.read_text());trackers[cfg['type']]=cfg
        names={f['name'] for f in cfg['fields']}
        mark('tracker_roles:'+cfg['type'],set(cfg['roles'].values())<=names)
        mark('tracker_document:'+cfg['type'],cfg['modes']['fullDocument'] is True and cfg['modes']['inline'] is False)
    mark('four_trackers',set(trackers)=={'pm-idea','pm-task','pm-backlog','pm-feature'})
    rows=records(root,True);byid={}
    for p,m in rows:
        validate_node(root,m);mark('unique:'+m['id'],m['id'] not in byid);byid[m['id']]=(p,m)
        mark('id_format:'+m['id'],bool(re.fullmatch(ID_PREFIX.get(m['entity_type'],'UNKNOWN')+r'-[A-Z0-9-]+(\.[0-9]+)?',m['id'])))
        mark('no_placeholder:'+m['id'],'TO_FILL' not in json.dumps(m,ensure_ascii=False,default=str))
        if 'trackerStatus' in m:
            mark('shape:'+m['id'],set(m['trackerStatus'])=={'type'} and all(k in m for k in ['title','status','priority']))
            options=next(f['options'] for f in trackers[m['trackerStatus']['type']]['fields'] if f['name']=='status')
            mark('status:'+m['id'],m['status'] in {o['value'] for o in options})
    signals,h=load(root);sigids={r['signal_id'] for r in signals}
    for r in signals:jsonschema.Draft202012Validator(json.loads((root/'schemas/signal.schema.json').read_text())).validate(r)
    mark('signals_valid_header_rows',True)
    for p,m in rows:
        for l in m['links']:mark('link:'+m['id']+'→'+l['to'],l['to'] in byid or l['to'] in sigids)
        for s in m['signal_refs']:mark('signal_ref:'+s,s in sigids)
        if m['entity_type']=='task':
            mark('task_idea:'+m['id'],m['idea_id'] in byid and byid[m['idea_id']][1]['entity_type']=='idea')
            mark('task_link:'+m['id'],any(l['rel']=='implements' and l['to']==m['idea_id'] for l in m['links']))
        if m['entity_type']=='idea':
            for fid in m['feature_ids']:
                mark('idea_feature:'+fid,fid in byid and byid[fid][1]['entity_type']=='feature')
                mark('idea_link:'+fid,any(l['rel']=='affects' and l['to']==fid for l in m['links']))
            for l in m['links']:
                if l['rel']=='iteration_of':
                    mark('iteration_parent:'+m['id'],byid[l['to']][1]['entity_type']=='idea')
                    mark('parent_route:'+l['to'],byid[l['to']][1]['route']=='L_parent')
                    mark('child_route:'+m['id'],m['route']=='iteration')
        if m['entity_type']=='feature':
            mark('feature_domain:'+m['id'],m['domain_id'] in byid and byid[m['domain_id']][1]['entity_type']=='domain')
            mark('feature_link:'+m['id'],any(l['rel']=='belongs_to_domain' and l['to']==m['domain_id'] for l in m['links']))
        if m['entity_type']=='backlog':mark('backlog_ref:'+m['id'],m['source_id'] in byid and bool(m['revisit']))
    from tools.backlog import State,validate as validate_backlog,status as backlog_status
    try:validate_backlog(State(root))
    except ValueError as e:raise AssertionError('backlog canonical integrity: '+str(e)) from e
    mark('backlog_canonical_integrity',True)
    mark('backlog_views_fresh',backlog_status(root)['fresh'])
    roles=json.loads((root/'policy/agents.json').read_text())
    for role,cfg in roles.items():
        text=(root/cfg['contract']).read_text();mark('agent_context:'+role,all(t in text for t in TOKENS))
        for line in text.splitlines():
            if line.startswith('- '):
                path=line[2:].strip()
                if '/' in path and ' ' not in path:mark('agent_path:'+path,(root/path).exists())
        c=(root/'.claude/agents'/f'{role}.md').read_text();cf=yaml.safe_load(c.split('---',2)[1]);xf=tomllib.loads((root/'.codex/agents'/f'{role}.toml').read_text())
        mark('claude_sync:'+role,c.split('---',2)[2].strip()==text.strip() and cf['name']==role)
        mark('codex_sync:'+role,xf['developer_instructions']==text and xf['name']==role)
        if cfg['read_only']:mark('review_readonly:'+role,'Write' not in cf['tools'] and 'Edit' not in cf['tools'])
        mark('shell_scope:'+role,('Bash' in cf['tools'])==(cfg.get('shell')=='scoped'))
        mark('codex_no_shell:'+role,xf['features']['shell_tool'] is False)
    mark('scoped_shell_single',[r for r,c in roles.items() if c.get('shell')]==['coordinator'])
    settings=json.loads((root/'.claude/settings.json').read_text());perm=settings['permissions']
    mark('shell_allowlist',all(r.startswith(SHELL_RULES) for r in perm['allow']))
    mark('shell_guard_hook','tools/shell_guard.py' in json.dumps(settings['hooks']) and SCOPE_DENY<=set(perm['deny']))
    skillfiles=list((root/'skills').glob('*/SKILL.md'));mark('twelve_skills',len(skillfiles)==12)
    for p in skillfiles:
        text=p.read_text();fm=yaml.safe_load(text.split('---',2)[1]);mark('skill_meta:'+p.parent.name,fm['name']==p.parent.name and bool(fm['description']))
        mark('skill_signals:'+p.parent.name,'signals/signals.csv' in text and 'signals/README.md' in text)
        for host in ['.claude/skills','.agents/skills']:mark('skill_sync:'+host+'/'+p.parent.name,(root/host/p.parent.name/'SKILL.md').read_bytes()==p.read_bytes())
    procs=json.loads((root/'workflows/procedures.json').read_text());mark('43_procedures',len(procs)==43)
    for proc in procs:
        mark('procedure:'+proc['name'],(root/proc['contract']).exists() and proc['role'] in roles)
        mark('template_ref:'+proc['name'],(root/proc['template']).exists())
        mark('procedure_signal_contract:'+proc['name'],'signals/signals.csv' in (root/proc['contract']).read_text())
    proc_text=json.dumps(procs)+''.join((root/proc['contract']).read_text() for proc in procs)
    for p in (root/'templates').glob('*.md'):
        fm=frontmatter(p)
        if 'entity_type' in fm:validate_node(root,fm)
        else:jsonschema.Draft202012Validator(json.loads((root/'schemas/artifact.schema.json').read_text())).validate(fm)
        mark('template_signal_refs:'+p.name,'signal_refs' in fm)
        mark('template_used:'+p.name,'templates/'+p.name in proc_text)
    idea_props=json.loads((root/'schemas/idea.schema.json').read_text())['properties']
    task_states=set(json.loads((root/'schemas/task.schema.json').read_text())['properties']['status']['enum'])
    task_options={o['value'] for o in next(f['options'] for f in trackers['pm-task']['fields'] if f['name']=='status')}
    transitions=json.loads((root/'workflows/task-transitions.json').read_text())
    mark('task_transitions',set(transitions)==task_states==task_options and all(set(v)<=task_states for v in transitions.values()))
    routes=json.loads((root/'workflows/routes.json').read_text())
    mark('route_enum',set(routes)==set(idea_props['route']['enum']) and all(set(v)<=set(idea_props['status']['enum']) for v in routes.values()))
    mark('budget_scales',set(json.loads((root/'policy/budgets.json').read_text()))==set(idea_props['scale']['enum']))
    models=json.loads((root/'policy/model-registry.json').read_text())['profiles']
    mark('role_models',all(c['model_profile'] in models for c in roles.values()))
    modules={p.stem for p in (root/'templates/modules').glob('*.md')}
    mark('applicability_modules',all(x in modules or x in NON_MODULES for v in json.loads((root/'workflows/applicability.json').read_text()).values() for x in v))
    for p,m in rows:
        if m['entity_type']=='task':
            mark('task_procedure:'+m['id'],m['procedure'] in {x['name'] for x in procs})
            mark('task_agent:'+m['id'],m['agent'] in roles)
            mark('task_model:'+m['id'],m['model_profile'] in models)
    registry=json.loads((root/'knowledge/graph/id-registry.json').read_text())
    mark('registry_complete',set(registry)==set(byid)|sigids)
    for id in sigids:mark('sig_resolve_registry:'+id,registry[id]['kind']=='csv_row' and registry[id]['key']==id)
    for id,(p,m) in byid.items():mark('node_registry:'+id,registry[id]['path']==str(p.relative_to(root)))
    for p in [*(root/'knowledge').rglob('INDEX.md'),root/'profile/INDEX.md',root/'ideas/INDEX.md',root/'tasks/INDEX.md',root/'backlog/INDEX.md']:
        for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if '://' not in target:mark('index_link:'+str(p.relative_to(root))+'→'+target,(p.parent/target).resolve().exists())
    defaults=json.loads((root/'policy/defaults.json').read_text())
    mark('signal_writer_coordinator',defaults['signal_writer']=='coordinator')
    mark('external_off',defaults['external_writes_enabled'] is False)
    mark('no_second_db',not list(root.rglob('*.sqlite')) and not list(root.rglob('*.db')))
    mark('no_signal_markdown_cards',not list((root/'signals').glob('SIG-*.md')))
    return {'status':'PASS','checks_passed':len(checks),'counts':{'roles':len(roles),'nodes':len(rows),'tracked_cards':sum('trackerStatus' in m for p,m in rows),'signals':len(signals),'tracker_types':len(trackers),'skills':len(skillfiles),'procedures':len(procs),'templates':len(list((root/'templates').glob('*.md'))),'modules':len(list((root/'templates/modules').glob('*.md')))},'live_nimbalyst_tested':False}
if __name__=='__main__':print(json.dumps(check(),ensure_ascii=False,indent=2))
