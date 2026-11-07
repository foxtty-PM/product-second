import json,unittest
from pathlib import Path
from tools.shell_guard import allowed
PY='~/.venvs/pm-os/bin/python '
class ShellGuardTests(unittest.TestCase):
    def test_allowlisted(self):
        for c in ['tools/signals.py hash','tools/signals.py list --related F-DEMO-0001 --status new','tools/signals.py capture --payload artifacts/sig.json --expected-hash abc --actor coordinator','tools/search.py "чернетка звернення"','tools/build_indices.py','tools/check_package.py']:self.assertTrue(allowed(PY+c),c)
        self.assertTrue(allowed('shasum -a 256 ideas/I-DEMO-0001.md'))
    def test_backlog_allowlisted(self):
        for c in ['status','sync','list --stage bdr','get I-DEMO-0001','apply --payload artifacts/backlog-op.json --actor coordinator']:self.assertTrue(allowed(PY+'tools/backlog.py '+c),c)
        for c in ['--root ideas status','apply --payload /tmp/x.json --actor coordinator','apply --payload ../x.json --actor coordinator','status; rm x']:self.assertFalse(allowed(PY+'tools/backlog.py '+c),c)
    def test_unittest_allowlisted(self):
        for c in ['-m unittest discover -s tests','-m unittest discover -s tests -v']:self.assertTrue(allowed(PY+c),c)
        for c in ['-m unittest','-m unittest discover','-m unittest discover -s ideas','-m unittest discover -s tests -p x.py','-m unittest discover -s tests -t ideas','-m unittest tests.test_signals','-m pytest','-m pip install x','-m unittest discover -s tests -v; rm x']:self.assertFalse(allowed(PY+c),c)
    def test_other_commands(self):
        for c in ['rm -rf ideas','ls','python tools/signals.py hash','python3 tools/check_package.py','shasum','shasum -a 1 VERSION',PY.strip(),PY+'-c print(1)',PY+'tools/build_manifest.py',PY+'tools/build_adapters.py',PY+'tools/shell_guard.py']:self.assertFalse(allowed(c),c)
    def test_chaining(self):
        for c in [';rm x','&& rm x','| sh','> signals/signals.csv','$(rm x)','`rm x`','\nrm x']:self.assertFalse(allowed(PY+'tools/signals.py hash '+c),c)
    def test_paths_stay_in_root(self):
        for c in [PY+'tools/signals.py --root ideas hash',PY+'tools/signals.py --roo ideas hash',PY+'tools/signals.py --root=ideas hash',PY+'tools/signals.py export ../x.csv','shasum -a 256 /etc/hosts','shasum -a 256 ~/.ssh/id_rsa','shasum -a 256 ../x']:self.assertFalse(allowed(c),c)
    def test_unbalanced_quote(self):self.assertFalse(allowed(PY+'tools/search.py "x'))
    @unittest.skipUnless(any(r.startswith('Bash(git ') for r in json.loads((Path(__file__).resolve().parents[1]/'.claude/settings.json').read_text())['permissions']['allow']),'operator git-readonly patch is not installed')
    def test_git_read_only(self):
        for c in ['git status','git status --short','git diff','git diff --stat HEAD','git diff --cached -- ideas/I-DEMO-0001.md','git diff HEAD~1 HEAD','git log','git log --oneline -20','git log -n5 --stat -- tools/signals.py','git log main..HEAD']:self.assertTrue(allowed(c),c)
    def test_git_blocked(self):
        for c in ['git','git add .','git commit -m x','git push','git restore ideas','git checkout .','git apply x','git -c core.fsmonitor=x status','git -C ideas status','git diff --output=x','git diff --outp=x','git log --output=x','git diff --ext-diff','git diff --no-index a b','git log -p','git log --format=x','git status --ignored','GIT_DIR=x git status','git diff /etc/hosts','git diff ../x','git status; rm x']:self.assertFalse(allowed(c),c)
if __name__=='__main__':unittest.main()
