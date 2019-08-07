import distutils.util
from debug import *

# vprint all variable assignments of the given state
def print_state(i, state):
  stmts = map(lambda k: k+'='+str(state[k]), state.keys())
  vprint("state[%d]: %s" % (i, ', '.join(stmts)))

# Convert a state tuple to boolean values
def normalize_state(state):
  for k,s in state.items():
    state[k] = distutils.util.strtobool(state[k])

def solve(trace, term_cnt):
  pre = [None]*term_cnt
  now = [None]*term_cnt

  # Initialization
  state = next(trace)
  normalize_state(state)
  print_state(0, state)

  # The next statement will be replaced by expressions to initialize pre
  template_init="template_init"

  if not pre[0]:
    return 1 # Fail immediately if we start in a bad state

  # Event interpretation loop
  for i, state in enumerate(trace, start=1):
    normalize_state(state)
    print_state(i, state)

    # The next statement will be replaced by expressions to update now according to state
    template_loop="template_loop"

    if now[0] == 0:
      return 1 # Fail immediately w/o taking further states into account

    pre = now
  return 0
