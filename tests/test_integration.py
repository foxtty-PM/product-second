import json,os,shutil,tempfile,unittest
from pathlib import Path
import yaml
from tools.common import frontmatter
from tools.signals import capture,load
from tools.build_indices import build
from tools.build_manifest import build as build_manifest
from tools.verify_manifest import verify
from tools.check_package import check
ROOT=Path(__file__).resolve().parents[1]
RELEASE_ONLY=unittest.skipUnless(os.environ.get('PMOS_RELEASE_CHECK')=='1','release-state check, needs PMOS_RELEASE_CHECK=1')
class FullIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)/'os';shutil.copytree(ROOT,self.root,ignore=shutil.ignore_patterns('__pycache__','PACKAGE_MANIFEST.json','AUDIT_SUMMARY.json'))
    def tearDown(self):self.tmp.cleanup()
    def patch_card(self,rel,**fields):
        p=self.root/rel;text=p.read_text();m=frontmatter(p);m.update(fields)
        p.write_text('---\n'+yaml.safe_dump(m,allow_unicode=True,sort_keys=False)+'---\n'+text.split('---',2)[2])
    def change_task(self,refs):self.patch_card('tasks/T-DEMO-0001.md',signal_refs=refs)
    def test_end_to_end_signal_to_work_registry_graph_checker(self):
        before=len(load(self.root)[0])
        r=capture(self.root,{'summary':'Draft feedback','type':'request','source':'test','source_ref':'test:1','related_ids':'F-DEMO-0001;I-DEMO-0001.1'},load(self.root)[1],'coordinator')
        sig=r['row']['signal_id'];self.change_task([sig]);build(self.root);report=check(self.root)
        self.assertEqual(report['status'],'PASS');self.assertEqual(report['counts']['signals'],before+1)
        self.assertIn('T-DEMO-0001,supported_by,'+sig,(self.root/'knowledge/graph/edges.csv').read_text())
    def test_unknown_card_signal_ref_rejected(self):
        self.change_task(['SIG-999999'])
        with self.assertRaises((AssertionError,ValueError)):build(self.root)
    def test_parent_needs_l_route(self):
        self.patch_card('ideas/I-DEMO-0001.md',scale='S',route='S',work_type='operational')
        with self.assertRaises(AssertionError):check(self.root)
    def test_placeholder_rejected(self):
        self.patch_card('tasks/T-DEMO-0001.md',goal='TO_FILL')
        with self.assertRaises(AssertionError):check(self.root)
    def test_card_without_entity_type_is_reported_and_keeps_signals(self):
        (self.root/'tasks/ui-card.md').write_text('---\nid: pt_01\ntitle: from ui\n---\n')
        self.assertTrue(load(self.root)[1])
        with self.assertRaises(ValueError):build(self.root)
        with self.assertRaises(ValueError):check(self.root)
    def test_drafts_are_not_nodes(self):
        shutil.copy(self.root/'ideas/I-DEMO-0001.md',self.root/'knowledge/_drafts/I-DEMO-0001.md')
        build(self.root);self.assertEqual(check(self.root)['status'],'PASS')
    def test_manifest_roundtrip(self):
        build_manifest(self.root);self.assertEqual(verify(self.root)['status'],'PASS')
        (self.root/'VERSION').write_text('changed\n');self.assertEqual(verify(self.root)['errors'],['VERSION'])
    @RELEASE_ONLY
    def test_original_signal_table_stays_empty(self):self.assertEqual(load(ROOT)[0],[])
