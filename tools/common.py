import json,hashlib
from pathlib import Path
import yaml
DATA_ROOTS=('knowledge','ideas','tasks','backlog')
def frontmatter(p):
    text=Path(p).read_text(encoding='utf-8')
    if not text.startswith('---\n'):return None
    header,separator,body=text[4:].partition('\n---\n')
    if not separator:raise ValueError('unterminated frontmatter: '+str(p))
    return yaml.safe_load(header)

def records(root,strict=False):
    root=Path(root).resolve();out=[]
    for d in DATA_ROOTS:
        for p in sorted((root/d).rglob('*.md')):
            if p.is_symlink() or root not in p.resolve().parents or '_drafts' in p.relative_to(root).parts:continue
            try:m=frontmatter(p)
            except yaml.YAMLError as e:
                if strict:raise ValueError(f'invalid frontmatter {p.relative_to(root)}: {e}')
                continue
            if not m:continue
            if strict and not(isinstance(m,dict) and m.get('id') and m.get('entity_type')):raise ValueError(f'card needs id and entity_type: {p.relative_to(root)}')
            if isinstance(m,dict) and m.get('id'):out.append((p,m))
    return out

def node_registry(root):
    root=Path(root).resolve()
    return {m['id']:{'path':str(p.relative_to(root)),'entity_type':m.get('entity_type','unknown')} for p,m in records(root)}
def digest(obj):return hashlib.sha256(json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
