import concurrent.futures,csv,hashlib,io,json,shutil,tempfile,unittest
from pathlib import Path
from tools.signals import capture,update,load,get,filter_rows,validate,spreadsheet_export,COLUMNS
from tools.common import node_registry,records
from tools.runtime import GuardError,safe_write
from tools.search import resolve,search
from tools.build_indices import build
ROOT=Path(__file__).resolve().parents[1]
class SignalTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        for d in ['knowledge','ideas','tasks','backlog','workflows','schemas','signals']:shutil.copytree(ROOT/d,self.root/d)
        (self.root/'signals/signals.csv').write_text(','.join(COLUMNS)+'\n')
        for p,m in records(self.root):
            if not m.get('demo'):p.unlink()
    def tearDown(self):self.tmp.cleanup()
    def h(self):return load(self.root)[1]
    def add(self,**extra):return capture(self.root,{'type':'request','summary':'Чернетка звернення','source':'mail','source_ref':'message:1',**extra},self.h(),'coordinator')
    def test_initial_empty(self):self.assertEqual(load(self.root)[0],[])
    def test_capture_minimal(self):
        r=capture(self.root,{'type':'request','summary':'Need draft','source':'manual'},self.h(),'coordinator');self.assertEqual(r['row']['signal_id'],'SIG-000001');self.assertEqual(r['row']['status'],'new')
    def test_date_only_observed(self):self.assertEqual(self.add(observed_at='2026-11-07')['row']['observed_at'],'2026-11-07')
    def test_unlinked_allowed(self):self.assertEqual(self.add()['row']['related_ids'],'')
    def test_blank_summary_reject(self):
        with self.assertRaises(GuardError):self.add(summary=' ')
    def test_blank_source_reject(self):
        with self.assertRaises(GuardError):self.add(source='')
    def test_invalid_type(self):
        with self.assertRaises(GuardError):self.add(type='initiative')
    def test_writer_role(self):
        with self.assertRaises(GuardError):capture(self.root,{'summary':'x','type':'error','source':'manual'},self.h(),'keeper')
    def test_no_given_capture_id(self):
        with self.assertRaises(GuardError):self.add(signal_id='SIG-000009')
    def test_no_given_capture_status(self):
        with self.assertRaises(GuardError):self.add(status='reviewed')
    def test_capture_cas(self):
        old=self.h();self.add()
        with self.assertRaises(GuardError):capture(self.root,{'summary':'x','source':'manual','type':'error'},old,'coordinator')
    def test_dedup_same_source_issue(self):
        first=self.add();second=self.add();self.assertFalse(second['created']);self.assertEqual(first['row']['signal_id'],second['row']['signal_id']);self.assertEqual(len(load(self.root)[0]),1)
    def test_independent_source_retained(self):
        self.add();self.add(source_ref='message:2');self.assertEqual(len(load(self.root)[0]),2)
    def test_different_issues_same_message(self):
        self.add();self.add(summary='Показати статус');self.assertEqual(len(load(self.root)[0]),2)
    def test_unknown_ref_not_blind_dedup(self):
        self.add(source_ref='');self.add(source_ref='');self.assertEqual(len(load(self.root)[0]),2)
    def test_multiline_quoting(self):
        s='Текст, із "лапками"\nі новим рядком';self.assertEqual(self.add(summary=s)['row']['summary'],get(self.root,'SIG-000001')['summary'])
    def test_exact_related_filter(self):
        self.add(related_ids='F-DEMO-0001;I-DEMO-0001.1');self.assertEqual(len(filter_rows(self.root,'F-DEMO-0001')),1);self.assertEqual(filter_rows(self.root,'F-DEMO-000'),[])
    def test_unknown_related(self):
        with self.assertRaises(GuardError):self.add(related_ids='F-999999')
    def test_wrong_related_entity(self):
        with self.assertRaises(GuardError):self.add(related_ids='T-DEMO-0001')
    def test_unknown_action_id(self):
        with self.assertRaises(GuardError):self.add(action_ref='T-NOT-EXIST')
    def test_reviewed_requires_evidence_or_reason(self):
        self.add(source_ref='')
        with self.assertRaises(GuardError):update(self.root,'SIG-000001',{'status':'reviewed'},self.h(),'coordinator')
    def test_reviewed_source(self):
        self.add();self.assertEqual(update(self.root,'SIG-000001',{'status':'reviewed'},self.h(),'coordinator')['row']['status'],'reviewed')
    def test_reviewed_explicit_source_gap(self):
        self.add(source_ref='');r=update(self.root,'SIG-000001',{'status':'reviewed','context':'missing_source_ref: усна розмова без запису'},self.h(),'coordinator');self.assertEqual(r['row']['source_ref'],'')
    def test_actioned_needs_result(self):
        self.add()
        with self.assertRaises(GuardError):update(self.root,'SIG-000001',{'status':'actioned'},self.h(),'coordinator')
    def test_actioned_work_id(self):
        self.add();r=update(self.root,'SIG-000001',{'status':'actioned','action_ref':'T-DEMO-0001'},self.h(),'coordinator');self.assertEqual(r['row']['action_ref'],'T-DEMO-0001')
    def test_dismissed_reason(self):
        self.add();r=update(self.root,'SIG-000001',{'status':'dismissed','action_ref':'reason: out of current scope'},self.h(),'coordinator');self.assertEqual(r['row']['status'],'dismissed')
    def test_reopen_requires_reason(self):
        self.add();update(self.root,'SIG-000001',{'status':'dismissed','action_ref':'reason: duplicate'},self.h(),'coordinator')
        with self.assertRaises(GuardError):update(self.root,'SIG-000001',{'status':'reviewed'},self.h(),'coordinator')
    def test_status_cannot_reset_to_new(self):
        self.add();update(self.root,'SIG-000001',{'status':'reviewed'},self.h(),'coordinator')
        with self.assertRaises(GuardError):update(self.root,'SIG-000001',{'status':'new'},self.h(),'coordinator')
    def test_immutable_id_update(self):
        self.add()
        with self.assertRaises(GuardError):update(self.root,'SIG-000001',{'signal_id':'SIG-000002'},self.h(),'coordinator')
    def test_update_cas(self):
        self.add();h=self.h();update(self.root,'SIG-000001',{'context':'city'},h,'coordinator')
        with self.assertRaises(GuardError):update(self.root,'SIG-000001',{'context':'other'},h,'coordinator')
    def test_bad_observed_date(self):
        with self.assertRaises(GuardError):self.add(observed_at='not-a-date')
    def test_captured_requires_timezone(self):
        r=self.add()['row'];r['captured_at']='2026-11-07T01:00:00'
        with self.assertRaises(GuardError):validate([r],node_registry(self.root))
    def test_duplicate_sig_ids(self):
        r=self.add()['row']
        with self.assertRaises(GuardError):validate([r,r],node_registry(self.root))
    def test_duplicate_related_id(self):
        with self.assertRaises(GuardError):self.add(related_ids='F-DEMO-0001;F-DEMO-0001')
    def test_header_order_reject(self):
        (self.root/'signals/signals.csv').write_text(','.join(reversed(COLUMNS))+'\n')
        with self.assertRaises(GuardError):load(self.root)
    def test_sig_resolver_csv(self):
        self.add();self.assertEqual(resolve(self.root,'SIG-000001')['kind'],'csv_row')
    def test_relevant_signal_search(self):
        self.add(related_ids='F-DEMO-0001');r=search(self.root,'чернетка',related_id='F-DEMO-0001');self.assertEqual(r[0]['id'],'SIG-000001')
    def test_index_registry_includes_sig(self):
        self.add();build(self.root);reg=json.loads((self.root/'knowledge/graph/id-registry.json').read_text());self.assertEqual(reg['SIG-000001']['key_column'],'signal_id')
    def test_graph_has_signal_relation(self):
        self.add(related_ids='F-DEMO-0001');build(self.root);self.assertIn('SIG-000001,relates_to,F-DEMO-0001',(self.root/'knowledge/graph/edges.csv').read_text())
    def test_formula_safe_export_without_corrupting_canon(self):
        raw='=HYPERLINK("unsafe")';self.add(summary=raw);h=self.h();spreadsheet_export(self.root,'artifacts/signals-safe.csv')
        with (self.root/'artifacts/signals-safe.csv').open(newline='') as f:row=list(csv.DictReader(f))[0]
        self.assertEqual(row['summary'],"'"+raw);self.assertEqual(get(self.root,'SIG-000001')['summary'],raw);self.assertEqual(h,self.h())
    def test_export_needs_new_artifact_path(self):
        with self.assertRaises(GuardError):spreadsheet_export(self.root,'signals/second.csv')
    def test_generic_writer_cannot_modify_csv(self):
        with self.assertRaises(GuardError):safe_write(self.root,'signals/signals.csv','bad',self.h(),'coordinator')
    def test_concurrent_capture_one_wins(self):
        h=self.h()
        def worker(n):
            try:capture(self.root,{'summary':str(n),'type':'error','source':'manual'},h,'coordinator');return True
            except GuardError:return False
        with concurrent.futures.ThreadPoolExecutor(2) as pool:self.assertEqual(sum(pool.map(worker,[1,2])),1)
        self.assertEqual(len(load(self.root)[0]),1)
    def test_failed_validation_preserves_file(self):
        before=(self.root/'signals/signals.csv').read_bytes()
        with self.assertRaises(GuardError):self.add(related_ids='NOPE')
        self.assertEqual(before,(self.root/'signals/signals.csv').read_bytes())
if __name__=='__main__':unittest.main()
