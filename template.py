from debug import *

# vprint all variable assignments of the given state
def print_state(i, state):
  stmts = map(lambda k: k+'='+str(state[k]), state.keys())
  vprint("state[%d]: %s" % (i, ', '.join(stmts)))

def print_array(arr, name):
  for i, v in enumerate(arr):
    vprint("%s[%d] = %s" % (name, i, v))

def print_array_rev(arr, name):
  for i, v in reversed(list(enumerate(arr))):
    vprint("%s[%d] = %s" % (name, i, v))

# Tries to satisfy the formula it is built for with the given trace
# The input trace needs to be an iterator pointing to the initial state
# in form of a dictionary mapping variable names to their (boolean) value.
def solve(trace, term_cnt):
  pre = [None]*term_cnt
  now = [None]*term_cnt

  # Initialization
  state = trace[0]
  print_array(trace, "trace")
  vprint()

  # The next statement will be replaced by expressions to initialize pre
  template_init="template_init"

  if pre[0] == 0:
    return [1, 0] # Fail immediately if we start in a bad state

  # Event interpretation loop
  iteration = 1
  for i, state in enumerate(trace[1:], start=1):
    print_state(i, state)

    # The next statement will be replaced by expressions to update now according to state
    template_loop="template_loop"

    if now[0] == 0:
      return [1, i] # Fail immediately w/o taking further states into account

    pre = now.copy()

    print_array_rev(pre, "pre")
    print_array_rev(now, "now")

  return [0]
