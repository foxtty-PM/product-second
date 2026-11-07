import unittest
from pathlib import Path

import jsonschema

from tools.check_package import validate_node
from tools.common import frontmatter


ROOT = Path(__file__).resolve().parents[1]


class TaskCompletionTests(unittest.TestCase):
    def task(self, status='done'):
        task = frontmatter(ROOT / 'tasks/T-DEMO-0001.md')
        task['status'] = status
        return task

    def test_done_requires_result_even_without_gate_fields(self):
        with self.assertRaises(jsonschema.ValidationError):
            validate_node(ROOT, self.task())

    def test_done_rejects_null_empty_or_blank_result(self):
        for result in (None, '', '  \t\n', 42):
            with self.subTest(result=result):
                task = self.task()
                task['result_ref'] = result
                with self.assertRaises(jsonschema.ValidationError):
                    validate_node(ROOT, task)

    def test_simple_done_accepts_result_without_separate_plan(self):
        task = self.task()
        task['result_ref'] = 'artifacts/completion.md'
        validate_node(ROOT, task)

    def test_ready_needs_no_plan_or_completion_result(self):
        validate_node(ROOT, self.task('ready'))


if __name__ == '__main__':
    unittest.main()
