"""Keep the shipped operational surface English; source data may be multilingual."""
import json,re,unittest
from pathlib import Path

import yaml

from tools.backlog import COLUMNS

ROOT=Path(__file__).resolve().parents[1]
CYRILLIC=re.compile(r'[\u0400-\u04ff]')


class EnglishInstructionsTests(unittest.TestCase):
    def test_active_instruction_files_are_english(self):
        paths=[ROOT/name for name in (
            'AGENTS.md','KNOWLEDGE_MAP.md','ARCHITECTURE.md','SPEC.md',
            'START_HERE.md','README.md','GETTING_STARTED.md','DEPLOYMENT.md',
            'PUBLISHING.md','BOOTSTRAP_PROMPT_EN.md','signals/README.md',
            'backlog/README.md','profile/loops.md','tools/README.md',
        )]
        for folder,pattern in (
            ('agents','*.md'),('skills','*/SKILL.md'),('procedures','*.md'),
            ('templates','**/*.md'),('.claude/agents','*.md'),
            ('.claude/skills','*/SKILL.md'),('.codex/agents','*.toml'),
            ('.agents/skills','*/SKILL.md'),
        ):
            paths.extend((ROOT/folder).glob(pattern))
        for path in paths:
            with self.subTest(path=str(path.relative_to(ROOT))):
                text=path.read_text(encoding='utf-8')
                self.assertIsNone(CYRILLIC.search(text))
                self.assertNotIn('BOOTSTRAP_PROMPT_UA.md',text)

    def test_only_the_english_bootstrap_is_shipped(self):
        self.assertTrue((ROOT/'BOOTSTRAP_PROMPT_EN.md').is_file())
        self.assertFalse((ROOT/'BOOTSTRAP_PROMPT_UA.md').exists())

    def test_automation_prompts_request_english(self):
        for name in ('inbox-morning','inbox-afternoon','weekly-focus-backlog'):
            path=ROOT/'nimbalyst-local/automations'/f'{name}.md'
            with self.subTest(automation=name):
                text=path.read_text(encoding='utf-8')
                self.assertIsNone(CYRILLIC.search(text))
                self.assertIn('Work in English.',text.split('---',2)[2])

    def test_shipped_ui_labels_are_english(self):
        labels=json.loads((ROOT/'workflows/gates.json').read_text(encoding='utf-8'))['labels']
        self.assertIsNone(CYRILLIC.search(json.dumps(labels,ensure_ascii=False)))
        self.assertIsNone(CYRILLIC.search(' '.join(COLUMNS.values())))
        for path in (ROOT/'.nimbalyst/trackers').glob('*.yaml'):
            with self.subTest(tracker=path.name):
                config=yaml.safe_load(path.read_text(encoding='utf-8'))
                self.assertIsNone(CYRILLIC.search(json.dumps(config,ensure_ascii=False)))


if __name__=='__main__':
    unittest.main()
