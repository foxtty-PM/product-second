import concurrent.futures,csv,hashlib,shutil,tempfile,unittest,uuid
from pathlib import Path
from unittest import mock
import yaml
from tools.backlog import apply,get,rows,status,sync,COLUMNS,TABLE,VIEW,evidence
from tools.build_indices import build
from tools.common import frontmatter
from tools.runtime import GuardError
from tools.signals import capture,load
ROOT=Path(__file__).resolve().parents[1]
AT='2026-11-01T10:00:00+00:00'
READY={'artifacts_valid':True,'reviews_current':True,'inputs_current':True,'taskless_reason':'Синтетичний сценарій: роботу виконав координатор без окремої задачі'}
VALUE={'expected_value':'Менше втрачених звернень','metric':'Частка завершених','baseline_missing_reason':'немає подій','target':'+5%','data_source':'BI','deadline':'2027-01-01','evaluation_rule':'через 30 днів'}
def passed(*gates):return [{'gate':g,'decision':'approved','at':AT,'recorded_by':'coordinator','decided_by':'Owner','quote':'так'} for g in gates]
class BacklogTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name).resolve()
        for d in ['knowledge','ideas','tasks','backlog','workflows','schemas','signals']:shutil.copytree(ROOT/d,self.root/d)
        sync(self.root)
    def tearDown(self):self.tmp.cleanup()
    def card(self,folder,m):(self.root/folder/f"{m['id']}.md").write_text('---\n'+yaml.safe_dump(m,allow_unicode=True,sort_keys=False)+'---\n\n# тіло\n',encoding='utf-8')
    def idea(self,id='I-0001',**extra):
        m={'schema_version':'4.2.0','id':id,'entity_type':'idea','title':'Картка '+id,'revision':1,'status':'bdr','demo':False,'aliases':[],'summary':'Опис','sources':[],'links':[],'signal_refs':[],'trackerStatus':{'type':'pm-idea'},'priority':'high','scale':'M','work_type':'product_feature','risk_profile':'low','work_status':'active','outcome':None,'route':'M','feature_ids':[],'item_type':'feature','gate_log':passed('G1a','G1'),**extra}
        for entry in m.get('gate_log') or []:
            entry.setdefault('dossier_hash',evidence(m));entry.setdefault('artifact_revisions',{});entry.setdefault('task_revisions',{})
        self.card('ideas',m);sync(self.root);return m
    def task(self,id,gates,idea='I-0001',status='ready',result=None):
        m={'schema_version':'4.2.0','id':id,'entity_type':'task','title':'Задача '+id,'revision':1,'status':status,'demo':False,'aliases':[],'summary':'Опис','sources':[],'links':[{'rel':'implements','to':idea}],'signal_refs':[],'trackerStatus':{'type':'pm-task'},'priority':'high','idea_id':idea,'agent':'product-writer','procedure':'brd','model_profile':'standard','goal':'Мета','output_format':'md','input_manifest':[],'tools_allowed':['Read'],'allowed_write_paths':['artifacts/'],'no_gos':['external writes'],'acceptance':['ok'],'budget':{'max_retries':0,'max_parallel':1},'stop_conditions':['missing access'],'gate_codes':gates,'expected_result':'Артефакт','gate_criteria':['критерій'],'result_ref':result}
        if result:
            p=self.root/result;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('Синтетичний результат',encoding='utf-8')
        self.card('tasks',m);sync(self.root);return m
    def rev(self,id):
        folder='tasks' if id.startswith('T-') else 'backlog' if id.startswith('BL-') else 'ideas'
        return frontmatter(self.root/folder/f'{id}.md')['revision']
    def payload(self,op,id,**q):return {'op':op,'id':id,'expected_revision':self.rev(id),'op_id':uuid.uuid4().hex,'note':'Зміна '+op,**q}
    def op(self,op,id,**q):return apply(self.root,self.payload(op,id,**q),'coordinator')
    def gate(self,id,*gates,decision='approved',**q):
        if decision in ('approved','changes_requested','rejected'):q={'quote':'так','decided_by':'Owner',**q}
        return self.op('gate',id,gates=list(gates),decision=decision,**q)
    def row(self,id='I-0001'):return get(self.root,id)
    def meta(self,id='I-0001'):return frontmatter(self.root/'ideas'/f'{id}.md')
    def test_table_readable_outside_app(self):
        self.idea()
        with (self.root/TABLE).open(encoding='utf-8-sig',newline='') as f:data=list(csv.DictReader(f))
        row=next(r for r in data if r['ID']=='I-0001')
        self.assertEqual(list(data[0])[:4],['Title','Parent','Priority','Stage']);self.assertEqual(row['Stage'],'Requirements preparation');self.assertEqual(row['Next approval'],'Implementation option + Iteration scope')
        self.assertIn('Картка I-0001',(self.root/VIEW).read_text(encoding='utf-8'))
    def test_all_required_columns_kept(self):self.assertTrue({'Title','Path','Queue rank','Priority reason','Value','Measurement','Remaining work','Blockers','Deferral reason','Revisit date or condition','Updated by'}<=set(COLUMNS.values()))
    def test_external_documents_named_links_and_csv_urls(self):
        self.idea()
        clickup=[{'title':'Вимоги','url':'https://clickup.example.invalid/docs/one'},{'title':'Погодження','url':'https://clickup.example.invalid/docs/two'}]
        dev=[{'title':'Техспек | [чернетка]','url':'https://dev.example.invalid/knowledge/design(v2)?section=a|b'}]
        result=self.op('set_fields','I-0001',fields={'clickup_docs':clickup,'dev_knowledge_docs':dev})
        self.assertTrue(result['synced']);self.assertEqual(self.row()['clickup_docs'],clickup);self.assertEqual(self.row()['dev_knowledge_docs'],dev)
        view=(self.root/VIEW).read_text()
        self.assertIn('[Вимоги](https://clickup.example.invalid/docs/one)',view)
        self.assertIn('[Техспек \\| \\[чернетка\\]](https://dev.example.invalid/knowledge/design%28v2%29?section=a%7Cb)',view)
        with (self.root/TABLE).open(encoding='utf-8-sig',newline='') as f:row=next(r for r in csv.DictReader(f) if r['ID']=='I-0001')
        self.assertEqual(row['ClickUp documents'],'\n'.join(d['url'] for d in clickup));self.assertEqual(row['Development knowledge documents'],dev[0]['url'])
        self.assertEqual(self.meta()['clickup_docs'],clickup);self.assertTrue(status(self.root)['fresh'])
    def test_external_document_links_optional_for_existing_cards(self):
        self.idea();self.assertEqual(self.row()['clickup_docs'],[]);self.assertEqual(self.row()['dev_knowledge_docs'],[])
        self.assertIn('|ClickUp documents|Development knowledge documents|',(self.root/VIEW).read_text())
    def test_external_document_update_preserves_stage_and_approval(self):
        self.idea(value=VALUE,gate_log=passed('G1a','G1','G2','G4','G5'));before=self.meta()['gate_log']
        self.op('set_fields','I-0001',fields={'clickup_docs':[{'title':'Погоджені вимоги','url':'https://clickup.example.invalid/docs/spec'}]})
        self.assertEqual(self.meta()['gate_log'],before);self.assertEqual(self.row()['stage_code'],'bdr')
        self.assertEqual(self.row()['next_gate_codes'],'');self.assertEqual(self.row()['changed_by'],'coordinator')
    def test_invalid_external_document_links_reject_without_writes(self):
        self.idea();original=(self.root/'ideas/I-0001.md').read_bytes()
        for url in ['javascript:alert(1)','file:///etc/hosts','data:text/html,hello','https:///missing-host','https://[bad','https://user:secret@example.invalid/doc','https://dev.example.invalid/doc\nbad']:
            with self.subTest(url=url):
                with self.assertRaises(GuardError):self.op('set_fields','I-0001',fields={'dev_knowledge_docs':[{'title':'Документ','url':url}]})
                self.assertEqual((self.root/'ideas/I-0001.md').read_bytes(),original)
        for documents in [['https://example.invalid/doc'],[{'url':'https://example.invalid/doc'}],[{'title':'','url':'https://example.invalid/doc'}]]:
            with self.subTest(documents=documents):
                with self.assertRaises(GuardError):self.op('set_fields','I-0001',fields={'clickup_docs':documents})
                self.assertEqual((self.root/'ideas/I-0001.md').read_bytes(),original)
        self.assertTrue(status(self.root)['fresh'])
    def test_external_documents_stay_on_own_row(self):
        self.idea('I-0002',item_type='initiative',route='L_parent',scale='L',clickup_docs=[{'title':'План напряму','url':'https://clickup.example.invalid/docs/parent'}])
        self.idea('I-0002.1',status='planned',item_type='iteration',route='iteration',scale='S',links=[{'rel':'iteration_of','to':'I-0002'}],gate_log=[],dev_knowledge_docs=[{'title':'Iteration','url':'https://dev.example.invalid/knowledge/iteration'}])
        self.assertEqual(self.row('I-0002.1')['clickup_docs'],[]);self.assertEqual(self.row('I-0002')['dev_knowledge_docs'],[])
        self.assertEqual(len(self.row('I-0002.1')['dev_knowledge_docs']),1)
    def test_formula_neutralized_card_unchanged(self):
        self.idea(summary='=HYPERLINK("x")')
        self.assertIn("'=HYPERLINK",(self.root/TABLE).read_bytes().decode('utf-8-sig'));self.assertEqual(self.meta()['summary'],'=HYPERLINK("x")')
    def test_standalone_feature_has_no_parent(self):self.idea();r=self.row();self.assertEqual(r['parent_id'],'');self.assertEqual(r['path'],'Картка I-0001')
    def test_member_of_hierarchy(self):
        self.idea('I-0002',item_type='initiative',route='L_parent',scale='L');self.idea();self.op('set_parent','I-0001',parent='I-0002')
        r=self.row();self.assertEqual(r['parent_title'],'Картка I-0002');self.assertEqual(r['path'],'Картка I-0002 → Картка I-0001')
    def test_member_of_needs_initiative(self):
        self.idea('I-0002');self.idea()
        with self.assertRaises(GuardError):self.op('set_parent','I-0001',parent='I-0002')
    def test_unknown_parent_rejected(self):
        self.idea()
        with self.assertRaises(GuardError):self.op('set_parent','I-0001',parent='I-9999')
    def test_cycle_rejected(self):
        a=self.idea('I-0002',item_type='initiative',route='L_parent',scale='L')
        b=self.idea('I-0003',item_type='initiative',route='L_parent',scale='L')
        self.card('ideas',{**a,'links':[{'rel':'member_of','to':'I-0003'}]})
        self.card('ideas',{**b,'links':[{'rel':'member_of','to':'I-0002'}]})
        with self.assertRaisesRegex(GuardError,'hierarchy cycle'):sync(self.root)
    def test_conflicting_parents_rejected(self):
        self.idea('I-0002',item_type='initiative',route='L_parent',scale='L');m=self.idea();m['links']=[{'rel':'member_of','to':'I-0002'},{'rel':'iteration_of','to':'I-0002'}];self.card('ideas',m)
        with self.assertRaises(GuardError):sync(self.root)
    def test_spawned_from_is_not_parent(self):self.idea('I-0002');self.idea(links=[{'rel':'spawned_from','to':'I-0002'}]);self.assertEqual(self.row()['parent_id'],'')
    def test_one_row_per_item(self):
        self.idea();self.task('T-0001',['G2']);ids=[r['id'] for r in rows(self.root)]
        self.assertEqual(len(ids),len(set(ids)));self.assertFalse([x for x in ids if x.startswith(('T-','BL-','F-','SIG-'))])
    def test_old_backlog_reference_is_row_data_not_row(self):
        r=self.row('I-DEMO-0001.1');self.assertEqual(r['revisit'],'2099-01-01');self.assertIn('synthetic',r['defer_reason']);self.assertNotIn('BL-DEMO-0001',[x['id'] for x in rows(self.root)])
    def test_stage_matches_card(self):self.idea(status='research',gate_log=[]);self.assertEqual(self.row()['stage_code'],self.meta()['status'])
    def test_stage_code_is_unknown_to_csv_writer(self):
        self.idea()
        with self.assertRaises(GuardError):self.op('set_fields','I-0001',fields={'status':'dev'})
    def test_intermediate_gate_updates_without_stage(self):
        self.idea(status='research',gate_log=[]);self.gate('I-0001','G1a');r=self.row()
        self.assertEqual(r['stage_code'],'research');self.assertIn('G1a Current process: approved',r['approved']);self.assertEqual(r['next_gate_codes'],'G1')
    def test_approved_accumulates(self):self.idea();r=self.row();self.assertIn('G1a',r['approved']);self.assertIn('G1 ',r['approved'])
    def test_joint_gate_records_each(self):
        self.idea();self.gate('I-0001','G2','G4');log=self.meta()['gate_log']
        self.assertEqual([e['gate'] for e in log[-2:]],['G2','G4']);self.assertEqual(log[-1]['joint_with'],['G2','G4']);self.assertEqual(self.row()['next_gate_codes'],'G5');self.assertIn('jointly G2+G4',self.row()['approved'])
    def test_card_yaml_has_no_aliases(self):self.idea();self.gate('I-0001','G2','G4');self.assertNotIn('&id',(self.root/'ideas/I-0001.md').read_text(encoding='utf-8'))
    def test_changes_are_not_approval(self):
        self.idea();self.gate('I-0001','G2','G4',decision='changes_requested',reason='додати варіант');r=self.row()
        self.assertEqual(r['next_gate_codes'],'G2+G4');self.assertIn('changes requested: додати варіант',r['next_gate']);self.assertNotIn('G2',r['approved'])
    def test_not_applicable_needs_reason_and_is_labelled(self):
        self.idea()
        with self.assertRaises(GuardError):self.gate('I-0001','G4',decision='not_applicable')
        self.gate('I-0001','G4',decision='not_applicable',reason='одна дрібна зміна');r=self.row();self.assertIn('not applicable (одна дрібна зміна)',r['approved']);self.assertNotIn('approved спільно',r['approved'])
    def test_inherited_links_parent_decision(self):
        self.idea('I-0002',status='delivering',item_type='initiative',route='L_parent',scale='L',gate_log=passed('G1a','G1','G2','G3'));self.idea('I-0002.1',status='bdr',item_type='iteration',route='iteration',scale='S',links=[{'rel':'iteration_of','to':'I-0002'}],gate_log=[])
        self.gate('I-0002.1','G3',decision='inherited',inherited_from='I-0002');self.assertIn('inherited from I-0002',self.row('I-0002.1')['approved'])
    def test_inherited_needs_ancestor_approval(self):
        self.idea('I-0002')
        self.idea()
        with self.assertRaises(GuardError):self.gate('I-0001','G2',decision='inherited',inherited_from='I-0002')
    def test_approval_needs_quote(self):
        self.idea()
        with self.assertRaises(GuardError):self.op('gate','I-0001',gates=['G2'],decision='approved',decided_by='Owner')
    def test_gate_cannot_be_skipped(self):
        self.idea()
        with self.assertRaises(GuardError):self.gate('I-0001','G5')
    def test_closed_item_has_no_next_gate(self):
        self.idea(status='knowledge',work_status='closed',outcome='killed');r=self.row();self.assertEqual(r['next_gate'],'—');self.assertEqual(r['next_gate_codes'],'')
    def test_tasks_of_nearest_gate_only(self):
        self.idea();self.task('T-0001',['G2','G4']);self.task('T-0002',['G5']);self.task('T-0003',[]);r=self.row()
        self.assertEqual(r['gate_task_ids'],'T-0001');self.assertEqual(r['gate_tasks'],'Задача T-0001')
    def test_no_tasks_is_not_readiness(self):self.idea();self.assertIn('readiness unconfirmed',self.row()['gate_task_states'])
    def test_done_and_dropped_do_not_approve(self):
        self.idea();self.task('T-0001',['G2','G4'],status='done',result='artifacts/I-0001/a.md');self.task('T-0002',['G2','G4'],status='dropped');r=self.row()
        self.assertEqual(r['next_gate_codes'],'G2+G4');self.assertIn('Done: 1',r['gate_task_states']);self.assertIn('Dropped: 1',r['gate_task_states']);self.assertNotIn('G2',r['approved'])
    def test_done_gate_task_needs_result(self):
        self.idea();self.task('T-0001',['G2'],status='doing')
        with self.assertRaises(GuardError):self.op('task','T-0001',fields={'status':'done'})
    def test_task_change_keeps_stage_and_updates_row(self):
        self.idea();self.task('T-0001',['G2'],status='doing');self.op('task','T-0001',fields={'status':'done','result_ref':'artifacts/I-0001/a.md'})
        r=self.row();self.assertEqual(r['stage_code'],'bdr');self.assertEqual(r['change_note'],'Зміна task');self.assertEqual(r['changed_by'],'coordinator');self.assertIn('artifacts/I-0001/a.md',r['artifacts'])
    def test_tasks_switch_after_approval_history_kept(self):
        self.idea();self.task('T-0001',['G2','G4']);self.task('T-0002',['G5']);self.gate('I-0001','G2','G4')
        self.assertEqual(self.row()['gate_task_ids'],'T-0002');self.assertEqual(frontmatter(self.root/'tasks/T-0001.md')['gate_codes'],['G2','G4']);self.assertEqual(len(self.meta()['gate_log']),4)
    def test_operational_task_gets_no_gate(self):
        self.idea();self.task('T-0003',[]);self.assertEqual(frontmatter(self.root/'tasks/T-0003.md')['gate_codes'],[])
    def test_operational_done_without_result_rejects_without_writes(self):
        self.idea();self.task('T-0003',[],status='doing')
        path=self.root/'tasks/T-0003.md';before=path.read_bytes()
        with self.assertRaises(GuardError):self.op('task','T-0003',fields={'status':'done'})
        self.assertEqual(path.read_bytes(),before);self.assertTrue(status(self.root)['fresh'])
    def test_operational_done_with_result_keeps_product_stage(self):
        self.idea();ref='artifacts/I-0001/completion.md';self.task('T-0003',[],status='doing',result=ref)
        self.op('task','T-0003',fields={'status':'done'})
        task=frontmatter(self.root/'tasks/T-0003.md')
        self.assertEqual(task['status'],'done');self.assertEqual(task['result_ref'],ref)
        self.assertEqual(self.meta()['status'],'bdr');self.assertTrue(status(self.root)['fresh'])
    def test_task_gate_must_be_in_route(self):
        self.idea();self.card('tasks',self.task('T-0001',['G2'])|{'gate_codes':['GX1']})
        with self.assertRaises(GuardError):sync(self.root)
    def test_child_tasks_stay_on_child_row(self):
        self.idea('I-0002',status='delivering',item_type='initiative',route='L_parent',scale='L',gate_log=passed('G1a','G1','G2','G3'));self.idea('I-0002.1',status='bdr',item_type='iteration',route='iteration',scale='S',links=[{'rel':'iteration_of','to':'I-0002'}],gate_log=[]);self.task('T-0001',['G4'],idea='I-0002.1')
        self.assertEqual(self.row('I-0002')['gate_task_ids'],'');self.assertEqual(self.row('I-0002')['next_gate'],'No own gate');self.assertEqual(self.row('I-0002.1')['gate_task_ids'],'T-0001')
    def test_failed_handoff_creates_no_transition(self):
        self.idea(value=VALUE,gate_log=passed('G1a','G1','G2','G4'));self.gate('I-0001','G5');self.op('set_fields','I-0001',fields={'blockers':['Передача не підтверджена']})
        with self.assertRaises(GuardError):self.op('stage','I-0001',to='dev',readiness=READY)
        r=self.row();self.assertEqual(r['stage_code'],'bdr');self.assertIn('Передача не підтверджена',r['blockers']);self.assertEqual(r['next_gate'],'Stage gates passed: awaiting transition')
    def test_stage_needs_gates(self):
        self.idea()
        with self.assertRaises(GuardError):self.op('stage','I-0001',to='dev',readiness=READY)
    def test_stage_needs_closed_tasks(self):
        self.idea(value=VALUE,gate_log=passed('G1a','G1','G2','G4','G5'));self.task('T-0001',['G5'],status='doing')
        with self.assertRaises(GuardError):self.op('stage','I-0001',to='dev',readiness=READY)
    def test_full_cycle(self):
        self.idea(value=VALUE,status='bdr');self.task('T-0001',['G2','G4'],status='doing');self.assertEqual(self.row()['gate_tasks'],'Задача T-0001')
        p=self.root/'artifacts/I-0001/options.md';p.parent.mkdir(parents=True,exist_ok=True);p.write_text('Синтетичні варіанти')
        self.op('task','T-0001',fields={'status':'done','result_ref':'artifacts/I-0001/options.md'});self.assertEqual(self.row()['next_gate_codes'],'G2+G4')
        self.gate('I-0001','G2','G4');self.gate('I-0001','G5');self.op('stage','I-0001',to='dev',readiness=READY);r=self.row()
        self.assertEqual(r['stage_code'],'dev');self.assertEqual(r['next_gate_codes'],'G6');self.assertTrue(status(self.root)['fresh'])
    def iterations(self):
        self.idea('I-0002',status='delivering',item_type='initiative',route='L_parent',scale='L',gate_log=passed('G1a','G1','G2','G3'),feature_ids=[])
        self.idea('I-0002.1',status='validating',item_type='iteration',route='iteration',scale='S',links=[{'rel':'iteration_of','to':'I-0002'}],gate_log=passed('G4','G5','G6'),value=VALUE)
        self.idea('I-0002.2',status='planned',item_type='iteration',route='iteration',scale='S',links=[{'rel':'iteration_of','to':'I-0002'}],gate_log=[])
    def test_g7_next_iteration_opens_next(self):
        self.iterations();self.assertIn('Awaiting G7',self.row('I-0002.2')['blockers'])
        self.gate('I-0002.1','G7',choice='next_iteration');self.assertEqual(self.row('I-0002.2')['blockers'],'');self.op('stage','I-0002.2',to='bdr',readiness=READY);self.assertEqual(self.row('I-0002.2')['stage_code'],'bdr')
    def test_g7_stop_blocks_next_and_allows_kill(self):
        self.iterations();self.gate('I-0002.1','G7',choice='stop')
        with self.assertRaises(GuardError):self.op('stage','I-0002.2',to='bdr',readiness=READY)
        self.op('stage','I-0002.2',to='knowledge',outcome='killed',readiness={**READY,'outcome_evidence':'G7 stop'});self.assertEqual(self.row('I-0002.2')['next_gate'],'—')
    def test_g7_adjust_needs_new_plan(self):
        self.iterations();self.gate('I-0002.1','G7',choice='adjust_plan')
        with self.assertRaises(GuardError):self.op('stage','I-0002.2',to='bdr',readiness=READY)
    def test_g7_needs_choice(self):
        self.iterations()
        with self.assertRaises(GuardError):self.gate('I-0002.1','G7')
    def test_parent_waits_for_children(self):
        self.iterations()
        with self.assertRaises(GuardError):self.op('stage','I-0002',to='knowledge',outcome='inconclusive',readiness={**READY,'outcome_evidence':'x'})
    def test_product_route_s_rejected(self):
        self.idea(route='S_metric',scale='S',gate_log=[])
        self.card('ideas',{**self.meta(),'route':'S'})
        with self.assertRaises(GuardError):sync(self.root)
    def test_operational_route_s_allowed(self):self.idea(route='S',scale='S',work_type='operational',gate_log=[]);self.assertEqual(self.op('set_fields','I-0001',fields={'title':'y'})['applied'],True)
    def test_g5_needs_value(self):
        self.idea(gate_log=passed('G1a','G1','G2','G4'))
        with self.assertRaises(GuardError):self.gate('I-0001','G5')
    def test_mini_metric_is_enough(self):
        self.idea(gate_log=passed('G1a','G1','G2','G4'),value={**VALUE,'mini':True});self.gate('I-0001','G5');self.assertIn('metric:',self.row()['measurement'])
    def test_regulatory_not_forced_to_user_metric(self):self.idea(work_type='regulatory',gate_log=passed('G1a','G1','G2','G4'));self.assertTrue(self.gate('I-0001','G5')['applied']);self.assertEqual(self.row()['measurement'],'Acceptance criteria in dossier')
    def test_defer_retains_stage_with_reason(self):
        self.idea();self.op('defer','I-0001',reason='Чекаємо партнера',revisit='2027-01-15');r=self.row()
        self.assertEqual(r['stage_code'],'bdr');self.assertEqual(r['work_status'],'Deferred');self.assertEqual(r['defer_reason'],'Чекаємо партнера');self.assertEqual(r['revisit'],'2027-01-15')
    def test_defer_needs_reason_and_revisit(self):
        self.idea()
        with self.assertRaises(GuardError):self.op('defer','I-0001',reason='x')
    def test_resume_and_second_defer_reuse_reference(self):
        self.idea();self.op('defer','I-0001',reason='a',revisit='2027-01-15');self.op('resume','I-0001');self.assertEqual(self.row()['defer_reason'],'');self.op('defer','I-0001',reason='b',revisit='2027-02-01')
        self.assertEqual(frontmatter(self.root/'backlog/BL-0001.md')['defer_count'],2);self.assertFalse((self.root/'backlog/BL-0002.md').exists())
    def test_paused_without_reference_rejected(self):
        self.idea(work_status='paused') if False else None
        self.card('ideas',{**self.idea(),'work_status':'paused'})
        with self.assertRaises(GuardError):sync(self.root)
    def test_writer_role(self):
        self.idea()
        with self.assertRaises(GuardError):apply(self.root,self.payload('set_fields','I-0001',fields={'title':'x'}),'keeper')
    def test_field_allowlist(self):
        self.idea()
        with self.assertRaises(GuardError):self.op('set_fields','I-0001',fields={'gate_log':[]})
    def test_cas_conflict(self):
        self.idea();old=self.payload('set_fields','I-0001',fields={'priority':'low'});self.op('set_fields','I-0001',fields={'priority':'medium'})
        with self.assertRaises(GuardError):apply(self.root,old,'coordinator')
    def test_retry_is_idempotent(self):
        self.idea();p=self.payload('gate','I-0001',gates=['G2'],decision='approved',quote='так',decided_by='Owner')
        self.assertTrue(apply(self.root,p,'coordinator')['applied']);self.assertFalse(apply(self.root,p,'coordinator')['applied']);self.assertEqual(len(self.meta()['gate_log']),3)
    def test_op_id_reuse_rejected(self):
        self.idea();p=self.payload('set_fields','I-0001',fields={'priority':'low'});apply(self.root,p,'coordinator')
        with self.assertRaises(GuardError):apply(self.root,{**p,'fields':{'priority':'medium'}},'coordinator')
    def test_partial_failure_visible_and_recoverable(self):
        self.idea();p=self.payload('set_fields','I-0001',fields={'remainder':'Хвіст'})
        with mock.patch('tools.backlog._write',side_effect=OSError('disk')):r=apply(self.root,p,'coordinator')
        self.assertFalse(r['synced']);self.assertFalse(status(self.root)['fresh'])
        again=apply(self.root,p,'coordinator');self.assertFalse(again['applied']);self.assertTrue(again['synced']);self.assertTrue(status(self.root)['fresh']);self.assertEqual(self.row()['remainder'],'Хвіст')
    def test_defer_partial_failure_retry_keeps_one_reference(self):
        self.idea();p=self.payload('defer','I-0001',reason='a',revisit='2027-01-15')
        real=__import__('tools.backlog',fromlist=['atomic_replace']).atomic_replace
        def crash(path,data):
            if Path(path)==self.root/'ideas/I-0001.md':raise OSError('crash')
            return real(path,data)
        with mock.patch('tools.backlog.atomic_replace',side_effect=crash):
            with self.assertRaises(OSError):apply(self.root,p,'coordinator')
        self.assertFalse(status(self.root)['fresh'])
        self.assertFalse(apply(self.root,p,'coordinator')['applied'])
        self.assertEqual(self.row()['work_status'],'Deferred')
        self.assertEqual(len(list((self.root/'backlog').glob('BL-0*.md'))),1)
    def test_concurrent_write_one_wins(self):
        self.idea();base=self.payload('set_fields','I-0001',fields={'priority':'low'})
        def worker(n):
            try:apply(self.root,{**base,'op_id':str(n)},'coordinator');return True
            except GuardError:return False
        with concurrent.futures.ThreadPoolExecutor(2) as pool:self.assertEqual(sum(pool.map(worker,[1,2])),1)
        self.assertEqual(self.meta()['revision'],2);self.assertTrue(status(self.root)['fresh'])
    def test_direct_card_edit_is_visible_as_stale(self):
        self.card('ideas',{**self.idea(),'title':'Без writer'});self.assertFalse(status(self.root)['fresh']);sync(self.root);self.assertTrue(status(self.root)['fresh'])
    def test_manual_table_edit_is_visible_as_stale(self):
        with (self.root/TABLE).open('ab') as f:f.write(b'x\n')
        self.assertFalse(status(self.root)['fresh'])
    def test_sync_is_deterministic(self):first=(self.root/TABLE).read_bytes();sync(self.root);self.assertEqual(first,(self.root/TABLE).read_bytes())
    def test_quote_with_separator_survives(self):
        self.idea();self.gate('I-0001','G2',quote='так\n---\nале');self.assertEqual(self.meta()['gate_log'][-1]['quote'],'так\n---\nале');self.assertEqual(self.meta()['title'],'Картка I-0001')
    def test_signals_stay_separate(self):
        self.idea();before=(self.root/'signals/signals.csv').read_bytes();self.op('set_fields','I-0001',fields={'remainder':'x'});self.assertEqual(before,(self.root/'signals/signals.csv').read_bytes())
        h=load(self.root)[1];r=capture(self.root,{'type':'request','summary':'Є запит','source':'mail','related_ids':'I-0001'},h,'coordinator')
        self.assertFalse(status(self.root)['fresh']);build(self.root);row=self.row();self.assertEqual(row['signals'],r['row']['signal_id']);self.assertNotIn('Є запит',(self.root/TABLE).read_bytes().decode('utf-8-sig'));self.assertTrue(status(self.root)['fresh'])

    def test_manual_markdown_view_edit_is_stale(self):
        (self.root/VIEW).write_text('edited',encoding='utf-8')
        self.assertFalse(status(self.root)['fresh'])
        sync(self.root);self.assertTrue(status(self.root)['fresh'])
    def test_receipt_survives_intervening_operation(self):
        self.idea();p=self.payload('gate','I-0001',gates=['G2'],decision='approved',quote='так',decided_by='Owner')
        apply(self.root,p,'coordinator');self.op('set_fields','I-0001',fields={'priority':'low'})
        self.assertFalse(apply(self.root,p,'coordinator')['applied'])
        self.assertEqual(len(self.meta()['gate_log']),3);self.assertEqual(self.meta()['priority'],'low')
    def test_op_id_is_global(self):
        self.idea();self.idea('I-0002')
        p=self.payload('set_fields','I-0001',fields={'priority':'low'});apply(self.root,p,'coordinator')
        q=self.payload('set_fields','I-0002',fields={'priority':'medium'});q['op_id']=p['op_id']
        with self.assertRaises(GuardError):apply(self.root,q,'coordinator')
    def test_recovery_preserves_unrelated_edit(self):
        self.idea();p=self.payload('defer','I-0001',reason='a',revisit='2027-01-15')
        real=__import__('tools.backlog',fromlist=['atomic_replace']).atomic_replace
        def crash(path,data):
            if Path(path)==self.root/'ideas/I-0001.md':raise OSError('crash')
            return real(path,data)
        with mock.patch('tools.backlog.atomic_replace',side_effect=crash):
            with self.assertRaises(OSError):apply(self.root,p,'coordinator')
        self.card('ideas',{**self.meta(),'title':'Operator edit'})
        with self.assertRaises(GuardError):apply(self.root,p,'coordinator')
        self.assertEqual(self.meta()['title'],'Operator edit')
    def test_changes_invalidate_later_approvals(self):
        self.idea(value=VALUE,gate_log=passed('G1a','G1','G2','G4','G5'))
        self.gate('I-0001','G2',decision='changes_requested',reason='переробити')
        self.gate('I-0001','G2')
        self.assertEqual(self.row()['next_gate_codes'],'G4')
        with self.assertRaises(GuardError):self.op('stage','I-0001',to='dev',readiness=READY)
    def test_next_gate_waiver_cannot_skip_research(self):
        self.idea(status='research',gate_log=[])
        with self.assertRaises(GuardError):self.gate('I-0001','G5',decision='not_applicable',reason='skip')
    def test_stage_requires_previous_stage_gates(self):
        self.idea(value=VALUE,gate_log=passed('G2','G4','G5'))
        with self.assertRaises(GuardError):self.op('stage','I-0001',to='dev',readiness=READY)
    def test_product_g7_cannot_be_waived(self):
        self.idea(status='validating',value=VALUE,gate_log=passed('G1a','G1','G2','G4','G5','G6'))
        with self.assertRaises(GuardError):self.gate('I-0001','G7',decision='not_applicable',reason='small')
    def test_adjusted_parent_plan_opens_iteration(self):
        self.iterations();self.gate('I-0002.1','G7',choice='adjust_plan')
        self.assertEqual(self.row('I-0002')['next_gate_codes'],'G3')
        self.gate('I-0002','G3')
        self.op('stage','I-0002.2',to='bdr',readiness=READY)
        self.assertEqual(self.row('I-0002.2')['stage_code'],'bdr')
    def test_artifact_cas_and_attribution(self):
        self.idea()
        r=self.op('artifact','I-0001',path='artifacts/I-0001/options.md',text='options',expected_hash=None)
        self.assertTrue(r['synced']);self.assertEqual(self.row()['changed_by'],'coordinator')
        self.assertEqual(self.row()['stage_code'],'bdr')
        with self.assertRaises(GuardError):self.op('artifact','I-0001',path='artifacts/I-0001/options.md',text='lost',expected_hash=None)
        self.assertEqual((self.root/'artifacts/I-0001/options.md').read_text(),'options')
    def test_artifact_cannot_write_protected_path(self):
        self.idea()
        with self.assertRaises(GuardError):self.op('artifact','I-0001',path='artifacts/../../policy/defaults.json',text='x',expected_hash=None)
    def test_direct_artifact_edit_marks_view_stale(self):
        self.idea();self.op('artifact','I-0001',path='artifacts/I-0001/options.md',text='one',expected_hash=None)
        (self.root/'artifacts/I-0001/options.md').write_text('two')
        self.assertFalse(status(self.root)['fresh'])
    def test_gate_snapshot_requires_current_artifact(self):
        self.idea();self.op('artifact','I-0001',path='artifacts/I-0001/options.md',text='one',expected_hash=None)
        self.gate('I-0001','G1a');self.gate('I-0001','G1')
        with self.assertRaises(GuardError):self.gate('I-0001','G2',artifact_revisions={'artifacts/I-0001/options.md':'bad'})
    def test_stale_gate_snapshot_blocks_stage(self):
        self.idea(value=VALUE);self.op('artifact','I-0001',path='artifacts/I-0001/options.md',text='one',expected_hash=None)
        h=hashlib.sha256(b'one').hexdigest()
        self.gate('I-0001','G1a');self.gate('I-0001','G1')
        self.gate('I-0001','G2','G4',artifact_revisions={'artifacts/I-0001/options.md':h});self.gate('I-0001','G5')
        (self.root/'artifacts/I-0001/options.md').write_text('changed')
        with self.assertRaises(GuardError):self.op('stage','I-0001',to='dev',readiness=READY)
    def test_product_outcome_cannot_be_completed_without_evaluation(self):
        self.idea(status='validating',value=VALUE,gate_log=passed('G1a','G1','G2','G4','G5','G6'))
        self.gate('I-0001','G7',choice='close')
        with self.assertRaises(GuardError):self.op('stage','I-0001',to='knowledge',outcome='completed',readiness={**READY,'outcome_evidence':'x'})
    def test_create_is_atomic_and_idempotent(self):
        original=self.idea();path=self.root/'ideas/I-0001.md';path.unlink();sync(self.root)
        p={'op':'create','id':'I-0001','expected_revision':0,'op_id':uuid.uuid4().hex,'note':'Створено','card':original}
        self.assertTrue(apply(self.root,p,'coordinator')['applied'])
        self.assertFalse(apply(self.root,p,'coordinator')['applied'])
        self.assertEqual(self.rev('I-0001'),1);self.assertTrue(status(self.root)['fresh'])
    def test_unknown_links_rejected_before_commit(self):
        m=self.idea();m['links']=[{'rel':'affects','to':'F-9999'}]
        self.card('ideas',m)
        with self.assertRaises(GuardError):sync(self.root)


    def test_gate_snapshots_are_automatic(self):
        self.idea(value=VALUE);self.op('artifact','I-0001',path='artifacts/I-0001/a.md',text='one',expected_hash=None)
        self.gate('I-0001','G1a');self.gate('I-0001','G1')
        self.gate('I-0001','G2','G4');self.gate('I-0001','G5')
        self.op('artifact','I-0001',path='artifacts/I-0001/a.md',text='two',expected_hash=hashlib.sha256(b'one').hexdigest())
        with self.assertRaises(GuardError):self.op('stage','I-0001',to='dev',readiness=READY)
        self.assertIn('reapproval',self.row()['approved'])
    def test_value_change_invalidates_approval(self):
        self.idea(value=VALUE,gate_log=passed('G1a','G1','G2','G4','G5'))
        self.op('set_fields','I-0001',fields={'value':{**VALUE,'target':'інша ціль'}})
        with self.assertRaises(GuardError):self.op('stage','I-0001',to='dev',readiness=READY)
    def test_inherited_approval_rechecks_parent(self):
        self.idea('I-0002',item_type='initiative',route='L_parent',scale='L',gate_log=passed('G1a','G1','G2','G3'))
        self.idea(value=VALUE,links=[{'rel':'member_of','to':'I-0002'}])
        self.gate('I-0001','G2',decision='inherited',inherited_from='I-0002')
        self.gate('I-0001','G4');self.gate('I-0001','G5')
        self.gate('I-0002','G2',decision='changes_requested',reason='Переробити')
        with self.assertRaises(GuardError):self.op('stage','I-0001',to='dev',readiness=READY)
    def test_future_gate_tasks_do_not_block_current_transition(self):
        self.idea(value=VALUE,gate_log=passed('G1a','G1','G2','G4','G5'));self.task('T-0001',['G6'],status='ready')
        self.op('stage','I-0001',to='dev',readiness=READY)
        self.assertEqual(self.row()['stage_code'],'dev');self.assertEqual(self.row()['gate_task_ids'],'T-0001')
    def test_empty_tasks_need_explicit_reason(self):
        self.idea(value=VALUE,gate_log=passed('G1a','G1','G2','G4','G5'))
        with self.assertRaises(GuardError):self.op('stage','I-0001',to='dev',readiness={k:v for k,v in READY.items() if k!='taskless_reason'})
    def test_dropped_task_needs_explicit_exclusion(self):
        self.idea(value=VALUE,gate_log=passed('G1a','G1','G2','G4','G5'));self.task('T-0001',['G5'],status='dropped')
        self.gate('I-0001','G5')
        with self.assertRaises(GuardError):self.op('stage','I-0001',to='dev',readiness=READY)
        self.op('stage','I-0001',to='dev',readiness=READY,task_exclusions={'T-0001':'Owner explicitly removed this criterion'})
    def test_create_unknown_signal_ref_rejected(self):
        m=self.idea();(self.root/'ideas/I-0001.md').unlink();m['signal_refs']=['SIG-999999']
        p={'op':'create','id':'I-0001','expected_revision':0,'op_id':uuid.uuid4().hex,'note':'Створено','card':m}
        with self.assertRaises(GuardError):apply(self.root,p,'coordinator')
        self.assertFalse((self.root/'ideas/I-0001.md').exists())
    def test_create_task_requires_implements_link(self):
        self.idea();m=self.task('T-0001',[]);(self.root/'tasks/T-0001.md').unlink();m['links']=[]
        p={'op':'create','id':'T-0001','expected_revision':0,'op_id':uuid.uuid4().hex,'note':'Створено','card':m}
        with self.assertRaises(GuardError):apply(self.root,p,'coordinator')
        self.assertFalse((self.root/'tasks/T-0001.md').exists())


    def test_replacing_artifact_reference_invalidates_approvals(self):
        self.idea(value=VALUE)
        self.op('artifact','I-0001',path='artifacts/I-0001/a.md',text='A',expected_hash=None)
        self.gate('I-0001','G1a');self.gate('I-0001','G1');self.gate('I-0001','G2','G4');self.gate('I-0001','G5')
        self.op('artifact','I-0001',path='artifacts/I-0001/b.md',text='B',expected_hash=None)
        self.op('set_fields','I-0001',fields={'artifact_refs':['artifacts/I-0001/b.md']})
        with self.assertRaises(GuardError):self.op('stage','I-0001',to='dev',readiness=READY)
    def test_reapproving_changed_task_requires_renewed_handoff(self):
        self.idea(value=VALUE);self.task('T-0001',['G2'],status='done',result='artifacts/I-0001/result.md')
        self.gate('I-0001','G2','G4');self.gate('I-0001','G5')
        self.op('task','T-0001',fields={'gate_criteria':['Уточнений критерій']})
        self.gate('I-0001','G2','G4')
        self.assertEqual(self.row()['next_gate_codes'],'G5')
        with self.assertRaises(GuardError):self.op('stage','I-0001',to='dev',readiness=READY)

if __name__=='__main__':unittest.main()
