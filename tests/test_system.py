import concurrent.futures,hashlib,json,os,shutil,tempfile,unittest
from pathlib import Path
import jsonschema
from tools.common import records,frontmatter,digest
from tools.check_package import check,validate_node
from tools.runtime import GuardError,safe_write,check_idea_transition,ApprovalSimulation,send_external
from tools.search import search,resolve
from tools.export_pack import export_pack
ROOT=Path(__file__).resolve().parents[1]
RELEASE_ONLY=unittest.skipUnless(os.environ.get('PMOS_RELEASE_CHECK')=='1','release-state check, needs PMOS_RELEASE_CHECK=1')
class PackageTests(unittest.TestCase):
    def test_package_integrity(self):self.assertEqual(check(ROOT)['status'],'PASS')
    def test_all_context_classes(self):self.assertTrue((ROOT/'knowledge/domains/INDEX.md').exists());self.assertTrue((ROOT/'knowledge/product/features/INDEX.md').exists())
    def test_four_trackers(self):self.assertEqual(check(ROOT)['counts']['tracker_types'],4)
    def test_child_links(self):
        m=frontmatter(ROOT/'ideas/I-DEMO-0001.1.md');self.assertIn({'rel':'iteration_of','to':'I-DEMO-0001'},m['links'])
    def test_nested_tracker_status_rejected(self):
        m=frontmatter(ROOT/'tasks/T-DEMO-0001.md');m['trackerStatus']['status']='ready'
        with self.assertRaises(jsonschema.ValidationError):validate_node(ROOT,m)
    def test_duplicate_stage_rejected(self):
        m=frontmatter(ROOT/'ideas/I-DEMO-0001.md');m['stage']='new'
        with self.assertRaises(jsonschema.ValidationError):validate_node(ROOT,m)
    def test_ready_requires_contract(self):
        m=frontmatter(ROOT/'tasks/T-DEMO-0001.md');m['status']='ready';del m['goal']
        with self.assertRaises(jsonschema.ValidationError):validate_node(ROOT,m)
    def test_demo_ready_contract_valid(self):
        m=frontmatter(ROOT/'tasks/T-DEMO-0001.md');m['status']='ready';validate_node(ROOT,m)
    @RELEASE_ONLY
    def test_only_synthetic_context_samples(self):self.assertTrue(all(m['demo'] for p,m in records(ROOT)))
    def test_demo_default_exclusion(self):
        demo={m['id'] for p,m in records(ROOT) if m.get('demo')}
        self.assertFalse(demo&{r['id'] for r in search(ROOT,'DEMO')})
    def test_demo_can_be_inspected(self):self.assertTrue(search(ROOT,'DEMO',True))
    @RELEASE_ONLY
    def test_profiles_unconfigured(self):
        for p in (ROOT/'profile').glob('*.md'):
            if p.name!='INDEX.md':self.assertIn('unconfigured',p.read_text())
    def test_every_template_signal_refs(self):
        for p in (ROOT/'templates').glob('*.md'):self.assertIn('signal_refs',frontmatter(p))
    def test_no_signal_tracker_type(self):self.assertFalse((ROOT/'.nimbalyst/trackers/pm-signal.yaml').exists())
    def test_domain_template_node(self):validate_node(ROOT,frontmatter(ROOT/'templates/domain.md'))
    def test_sig_resolve_unknown(self):
        with self.assertRaises(GuardError):resolve(ROOT,'SIG-999999')
class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);shutil.copytree(ROOT/'workflows',self.root/'workflows');self.idea=frontmatter(ROOT/'ideas/I-DEMO-0001.md')
        self.ready=dict.fromkeys(['tasks_closed','artifacts_valid','reviews_current','gate_approved','no_blockers','inputs_current'],True)|{'input_hash':digest(self.idea)}
    def tearDown(self):self.tmp.cleanup()
    def test_valid_transition_proposal(self):self.assertEqual(check_idea_transition(self.root,self.idea,'research',1,self.ready)['status'],'research');self.assertEqual(self.idea['status'],'new')
    def test_route_skip(self):
        with self.assertRaises(GuardError):check_idea_transition(self.root,self.idea,'dev',1,self.ready)
    def test_stale_revision(self):
        with self.assertRaises(GuardError):check_idea_transition(self.root,self.idea,'research',2,self.ready)
    def test_missing_gate(self):
        with self.assertRaises(GuardError):check_idea_transition(self.root,self.idea,'research',1,self.ready|{'gate_approved':False})
    def test_hash_mismatch(self):
        with self.assertRaises(GuardError):check_idea_transition(self.root,self.idea,'research',1,self.ready|{'input_hash':'bad'})
    def test_high_risk(self):
        self.idea['risk_profile']='high';self.ready['input_hash']=digest(self.idea)
        with self.assertRaises(GuardError):check_idea_transition(self.root,self.idea,'research',1,self.ready)
    def test_open_children_block_parent(self):
        self.idea['status']='delivering';self.ready['input_hash']=digest(self.idea)
        with self.assertRaises(GuardError):check_idea_transition(self.root,self.idea,'knowledge',1,self.ready|{'outcome_evidence':'x'},outcome='completed')
    def test_early_kill(self):self.assertEqual(check_idea_transition(self.root,self.idea,'knowledge',1,self.ready|{'outcome_evidence':'Owner stop'},outcome='killed')['work_status'],'closed')
    def test_closure_evidence(self):
        with self.assertRaises(GuardError):check_idea_transition(self.root,self.idea,'knowledge',1,self.ready,outcome='killed')
    def test_file_cas(self):
        h=safe_write(self.root,'artifacts/a.md','one',None)
        with self.assertRaises(GuardError):safe_write(self.root,'artifacts/a.md','two',None)
        self.assertNotEqual(h,safe_write(self.root,'artifacts/a.md','two',h))
    def test_keeper_boundary(self):
        with self.assertRaises(GuardError):safe_write(self.root,'knowledge/a.md','x',None)
        safe_write(self.root,'knowledge/a.md','x',None,'keeper')
    def test_draft_allowed(self):safe_write(self.root,'knowledge/_drafts/a.md','x',None)
    def test_path_escape(self):
        with self.assertRaises(GuardError):safe_write(self.root,'artifacts/../../x.md','x',None)
    def test_normalized_protected_path(self):
        with self.assertRaises(GuardError):safe_write(self.root,'knowledge/../policy/x.md','x',None)
    def test_draft_traversal(self):
        with self.assertRaises(GuardError):safe_write(self.root,'knowledge/_drafts/../confirmed.md','x',None)
    def test_symlink_escape(self):
        with tempfile.TemporaryDirectory() as outside:
            (self.root/'artifacts').mkdir();(self.root/'artifacts/link').symlink_to(outside,target_is_directory=True)
            with self.assertRaises(GuardError):safe_write(self.root,'artifacts/link/x.md','x',None)
    def test_concurrent_cas(self):
        def worker(n):
            try:safe_write(self.root,'artifacts/shared.md',str(n),None);return True
            except GuardError:return False
        with concurrent.futures.ThreadPoolExecutor(2) as pool:self.assertEqual(sum(pool.map(worker,[1,2])),1)
    def test_external_denied(self):
        with self.assertRaises(GuardError):send_external('x')
    def test_approval_binding(self):
        a=ApprovalSimulation();e={'idempotency_key':'x','body':'one'};k=a.approve(e);e['body']='changed'
        with self.assertRaises(GuardError):a.run(e,k)
    def test_approval_replay(self):
        a=ApprovalSimulation();e={'idempotency_key':'x'};k=a.approve(e);a.run(e,k)
        with self.assertRaises(GuardError):a.run(e,k)
    def test_approval_expiry(self):
        a=ApprovalSimulation();e={'idempotency_key':'x'};k=a.approve(e,-1)
        with self.assertRaises(GuardError):a.run(e,k)
    def test_idempotency(self):
        a=ApprovalSimulation();e={'idempotency_key':'x'};a.run(e,a.approve(e))
        with self.assertRaises(GuardError):a.run(e,a.approve(e))
    def test_export_review(self):
        with self.assertRaises(ValueError):export_pack(self.root,[],'artifacts/pack')
    def test_export_manifest(self):
        safe_write(self.root,'artifacts/spec.md','sanitized',None);r=export_pack(self.root,['artifacts/spec.md'],'artifacts/pack',True)
        self.assertEqual(r[0]['sha256'],hashlib.sha256((self.root/'artifacts/pack/artifacts/spec.md').read_bytes()).hexdigest())
    def test_export_immutable(self):
        export_pack(self.root,[],'artifacts/pack',True)
        with self.assertRaises(ValueError):export_pack(self.root,[],'artifacts/pack',True)
if __name__=='__main__':unittest.main()
