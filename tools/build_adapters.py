import json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def build(root=ROOT):
    root=Path(root);roles=json.loads((root/'policy/agents.json').read_text())
    for role,cfg in roles.items():
        text=(root/cfg['contract']).read_text();tools='Read, Grep, Glob'+('' if cfg['read_only'] else ', Edit, Write')
        if role=='researcher':tools+=', WebSearch, WebFetch'
        if cfg.get('shell')=='scoped':tools+=', Bash'
        p=root/'.claude/agents'/f'{role}.md';p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text('---\nname: '+role+'\ndescription: '+json.dumps(cfg['description'],ensure_ascii=False)+'\ntools: '+tools+'\nmodel: inherit\n---\n'+text,encoding='utf-8')
        p=root/'.codex/agents'/f'{role}.toml';p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text('name = '+json.dumps(role)+'\ndescription = '+json.dumps(cfg['description'],ensure_ascii=False)+'\ndeveloper_instructions = '+json.dumps(text,ensure_ascii=False)+'\n[features]\nshell_tool = false\napps = false\nplugins = false\n',encoding='utf-8')
    for host in ['.claude/skills','.agents/skills']:
        for p in (root/'skills').glob('*/SKILL.md'):
            dst=root/host/p.parent.name/'SKILL.md';dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dst)
    return len(roles)
if __name__=='__main__':print(json.dumps({'generated_agents_per_host':build(),'live_verified':False}))
