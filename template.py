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

  print_array(trace, "trace")

  iteration = 1
  while True:
    vprint("\nRunning ptLTL init #%d..." % iteration)
    state = trace[0]
    print_state(0, state)

    # The next statement will be replaced by expressions to initialize state 0 under ptLTL interpretation
    template_init="template_init"

    if pre[0] == 0:
      return [1, 0] # Fail immediately if we start in a bad state

    print_array_rev(pre, "pre")
    print_array_rev(now, "now")

    # ptLTL interpretation loop
    vprint("\nRunning ptLTL loop interpretation #%d..." % iteration)
    for i, state in enumerate(trace[1:], start=1):
      print_state(i, state)

      # The next statement will be replaced by expressions to update states 1... under ptLTL interpretation
      template_loop="template_loop"

      print_array_rev(pre, "pre")
      print_array_rev(now, "now")
      if now[0] == 0:
        return [1, i] # Fail immediately w/o taking further states into account

      pre = now.copy()
      vprint()

    return [0]

