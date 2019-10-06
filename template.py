import math
import functools
from debug import *

# vprint all variable assignments of the given state
def print_state(i, state):
  stmts = map(lambda k: k+'='+str(state[k]), state.keys())
  vvprint("state[%d]: %s" % (i, ', '.join(stmts)))

# Print the data matrix (transposed for better readability)
def print_matrix(mat):
  t_width = int(math.log10(len(mat[0]))+1)
  field_indent = t_width + 1

  vvprintn("%sT%s" % (' '*(t_width-1), ' '*(field_indent - t_width)))
  for i in range(len(mat)):
    vvprintn("%d" % (i%10))
  vvprint()

  for i in range(len(mat[0])):
    vvprintn("%*d|" % (t_width, i))
    for j in range(len(mat)):
      v = mat[j][i]
      vvprintn("%s" % (' ' if v is None else int(v)))
    vvprintn("|%d" % (i))
    vvprint()

  vvprintn("%sS" % (' '*(t_width)))
  for i in range(len(mat)):
    vvprintn("%d" % (i%10))
  vvprint()

def print_array(arr, name):
  for i, v in enumerate(arr):
    vvprint("%s[%d] = %s" % (name, i, v))

def print_array_rev(arr, name):
  for i, v in reversed(list(enumerate(arr))):
    vvprint("%s[%d] = %s" % (name, i, v))

# Tries to satisfy the formula it is built for with the given trace
# The input trace needs to be an iterator pointing to the initial state
# in form of a dictionary mapping variable names to their (boolean) value.
def solve(trace, term_cnt):
  state_cnt = len(trace)
  d = [[None for j in range(term_cnt)] for i in range(state_cnt)]

  print_matrix(d)

  iteration = 1
  while True:
    vprint("\nRunning ptLTL init #%d..." % iteration)
    i = 0
    state = trace[i]
    print_state(i, state)

    # The next statement will be replaced by expressions to initialize state 0 under ptLTL interpretation
    template_init="template_init"

    if d[i][0] == 0:
      return 1 # Fail immediately if we start in a bad state

    print_matrix(d)

    # ptLTL interpretation loop
    vprint("\nRunning ptLTL loop interpretation #%d..." % iteration)
    for i, state in enumerate(trace[1:], start=1):
      print_state(i, state)

      # The next statement will be replaced by expressions to update states 1... under ptLTL interpretation
      template_loop="template_loop"

      print_matrix(d)

      if d[i][0] == 0:
        return 1 # Fail immediately if we start in a bad state

      vvprint()

    vvprint("ptLTL #%d done:" % iteration)
    print_matrix(d)

    i = state_cnt-1
    vprint("\nRunning ftLTL init #%d..." % iteration)
    # The next statement will be replaced by expressions to initialize state 0 under ftLTL interpretation
    template_ltl_init="template_ltl_init"

    print_matrix(d)

    # ftLTL interpretation loop
    vprint("\nRunning ftLTL loop interpretation #%d..." % iteration)
    for i, state in reversed(list(enumerate(trace[:-1]))):
      print_state(i, state)

      # The next statement will be replaced by expressions to update states n-1-1... under ftLTL interpretation
      template_future_loop="template_future_loop"

      print_matrix(d)


    # Check result, i.e., test the value in the first row of the first column of d.
    # If is still indeterminate (None), continue the algorithm.
    # Else the satisfiability of the trace is determined by the value of d[i][0].
    if d[i][0] != None:
      return not d[i][0]

    iteration += 1
