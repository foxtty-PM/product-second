"""Local cooperating helpers, not production authorization or Nimbalyst UI hooks."""
import contextlib,copy,hashlib,json,os,tempfile,time,uuid
from pathlib import Path
from .common import digest
class GuardError(ValueError):pass
@contextlib.contextmanager
def file_lock(root,key,timeout=3):
    base=Path(root)/'state/locks';base.mkdir(parents=True,exist_ok=True)
    lock=base/hashlib.sha256(key.encode()).hexdigest();deadline=time.monotonic()+timeout
    while True:
        try:lock.mkdir();break
        except FileExistsError:
            if time.monotonic()>=deadline:raise GuardError('lock busy; stale crash locks require operator reconciliation')
            time.sleep(.01)
    try:yield
    finally:lock.rmdir()

def atomic_replace(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);fd,tmp=tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)

def safe_write(root,relative,text,expected_hash,actor='executor'):
    root=Path(root).resolve();p=(root/relative).resolve()
    if Path(relative).is_absolute() or root not in p.parents:raise GuardError('root escape')
    relative=p.relative_to(root).as_posix()
    if not relative.startswith(('ideas/','tasks/','backlog/','knowledge/','artifacts/','briefs/')):raise GuardError('protected path; signals require signal-specific writer')
    if relative.startswith('knowledge/') and not relative.startswith('knowledge/_drafts/') and actor!='keeper':raise GuardError('keeper required')
    with file_lock(root,relative):
        old=hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None
        if old!=expected_hash:raise GuardError('CAS conflict')
        atomic_replace(p,text.encode('utf-8'))
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def check_idea_transition(root,idea,to,expected_revision,readiness,outcome=None):
    if idea['revision']!=expected_revision or idea['work_status']!='active':raise GuardError('stale/not active')
    route=json.loads((Path(root)/'workflows/routes.json').read_text())[idea['route']]
    if idea['status'] not in route or idea['status']=='knowledge':raise GuardError('bad stage')
    ix=route.index(idea['status']);normal=route[ix+1:ix+2]
    if to not in normal and not(to=='knowledge' and outcome=='killed'):raise GuardError('route skip')
    if not all(readiness.get(k) is True for k in ['tasks_closed','artifacts_valid','reviews_current','gate_approved','no_blockers','inputs_current']):raise GuardError('not ready')
    if readiness.get('input_hash')!=digest(idea):raise GuardError('input hash mismatch')
    if idea['risk_profile'] in ('high','critical') and readiness.get('human_risk_review') is not True:raise GuardError('human review required')
    if idea['status']=='delivering' and readiness.get('children_closed') is not True:raise GuardError('children open')
    obj=copy.deepcopy(idea);obj.update(status=to,revision=expected_revision+1)
    if to=='knowledge':
        if not outcome or not readiness.get('outcome_evidence'):raise GuardError('outcome evidence required')
        if outcome=='go' and idea['scale']!='XL':raise GuardError('go reserved for XL')
        if idea['scale']=='XL' and outcome not in ('go','killed','inconclusive'):raise GuardError('XL is investment decision')
        obj.update(work_status='closed',outcome=outcome)
    elif outcome is not None:raise GuardError('outcome only on closure')
    return obj

class ApprovalSimulation:
    def __init__(self):self.approvals={};self.keys=set()
    def approve(self,envelope,ttl=300):
        k=str(uuid.uuid4());self.approvals[k]=[digest(envelope),time.time()+ttl,False];return k
    def run(self,envelope,key):
        a=self.approvals.get(key)
        if not a or a[2] or a[1]<=time.time() or a[0]!=digest(envelope):raise GuardError('invalid approval simulation')
        if envelope['idempotency_key'] in self.keys:raise GuardError('duplicate action')
        a[2]=True;self.keys.add(envelope['idempotency_key']);return {'external_action_performed':False,'status':'simulated'}
def send_external(*args,**kwargs):raise GuardError('external sender absent')
