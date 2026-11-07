"""PreToolUse guard for the coordinator scoped shell; a cooperating check, not an OS sandbox."""
import json,re,shlex,sys
PYTHON='~/.venvs/pm-os/bin/python'
SCRIPTS={'tools/signals.py','tools/search.py','tools/build_indices.py','tools/check_package.py','tools/backlog.py'}
TESTS=(['-m','unittest','discover','-s','tests'],['-m','unittest','discover','-s','tests','-v'])
META=re.compile(r'[;&|<>`$(){}\\\n\r]')
def allowed(command):
    if META.search(command):return False
    try:argv=shlex.split(command)
    except ValueError:return False
    if len(argv)<2:return False
    args=argv[1:]
    if any(a.startswith(('--ro','/','~')) or '..' in a.split('/') for a in args):return False
    if argv[0]==PYTHON:return args[0] in SCRIPTS or args in TESTS
    return argv[:3]==['shasum','-a','256'] and len(argv)>3

def main():
    command=json.load(sys.stdin).get('tool_input',{}).get('command','')
    if allowed(command):return 0
    print('Blocked: command is outside the coordinator scoped shell, see tools/README.md',file=sys.stderr)
    return 2
if __name__=='__main__':sys.exit(main())
