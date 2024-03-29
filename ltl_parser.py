# based on PLY's calc.py

import re
import distutils.util
from debug import *
from collections.abc import Iterable

class _lexer(object):
  # global tokens
  tokens = (
      'BOOL', 'SYM', 'NEWLINE', # 0 INPUTS
      'NOT','S_PREV','W_PREV','S_NEXT','W_NEXT','ONCE','HIST','EVENTUALLY','ALWAYS', # 1 INPUTS
      'OR','AND','IMP','SINCE','UNTIL', # 2 INPUTS
      )

  # constructor
  def __init__(self,**kwargs):
    import ply.lex as lex
    self.lexlexer = lex.lex(module=self, reflags=re.IGNORECASE, **kwargs)

  # Define all keywords as functions to make sure they are ordered before t_SYM
  # We could also filter them out as reserved words in a t_SYM function (as suggested by the PLY docs)
  def t_NOT(self, t):
    r'(not)|(!)'
    return t

  def t_S_PREV(self, t):
    r's_prev'
    return t

  def t_W_PREV(self, t):
    r'w_prev'
    return t

  def t_S_NEXT(self, t):
    r's_next'
    return t

  def t_W_NEXT(self, t):
    r'w_next'
    return t

  def t_ONCE(self, t):
    r'once'
    return t

  def t_HIST(self, t):
    r'hist(orically)?'
    return t

  def t_EVENTUALLY(self, t):
    r'eventually'
    return t

  def t_ALWAYS(self, t):
    r'always'
    return t

  def t_OR(self, t):
    r'(or)|(v)'
    return t

  def t_AND(self, t):
    r'(and)|(\^)'
    return t

  def t_IMP(self, t):
    r'(imp(lies)?)|(->)'
    return t

  def t_SINCE(self, t):
    r'(since)'
    return t

  def t_UNTIL(self, t):
    r'(until)'
    return t

  def t_BOOL(self, t):
    r'0|1|true|false'
    # NB: this should never throw ValueError due to the RE above
    t.value = bool(distutils.util.strtobool(t.value))
    return t

  # Identifiers
  t_SYM     = r'[a-zA-Z_][a-zA-Z0-9_]*'

  t_ignore_comment = r'(//.*)|([#].*)'
  # FIXME: multiline please?
  # t_ignore_multi_comment = r'(/\*(.|\n)*?\*/)|(//.*)|([#].*)'

  literals = ['(', ')']

  # Ignored characters
  t_ignore = " \t"

  def t_NEWLINE(self, t):
      r'\n+'
      t.lexer.lineno += t.value.count("\n")
      return t

  def t_error(self, t):
      print("Illegal character '%s'" % t.value[0])
      t.lexer.skip(1) # Try continuing with the next one
      





def print_forest_oneline(tree):
  for c in tree:
    print_tree_oneline(c)
    vprint()

# Print the tree in Polish notation in one line w/o a newline at the end
def print_tree_oneline(tree):
  if isinstance(tree, Iterable):
    vprintn(tree[0])
    if len(tree) > 1:
      vprintn("(")
    for c in tree[1:-1]:
      print_tree_oneline(c)
      vprintn(",")
    if len(tree) > 1:
      print_tree_oneline(tree[-1])
      vprintn(")")
  else:
    vprintn(tree)

def print_forest(tree, indent_guides=False):
  for c in tree[:-1]:
    print_tree(c, 0, indent_guides)
    vprint()
  print_tree(tree[-1], 0, indent_guides)

def print_tree(tree, cur_indent=0, indent_guides=False):
  _INDENT = 4
  for _ in range(1, (cur_indent) // _INDENT):
    if indent_guides:
      # FIXME: we need to check if the respective level is done already
      #        by keeping a list of numbers of \\ not yet printed at
      #        each level.
      vprintn('.')
      vprintn(' '*(_INDENT-1))
    else:
      vprintn(' '*_INDENT)
  else:
    if cur_indent > 0 and indent_guides:
      vprintn('\\')
      vprintn(' '*(_INDENT-1))
  cur_indent += _INDENT

  if isinstance(tree, Iterable):
    vprint(tree[0])
    for c in tree[1:]:
      print_tree(c, cur_indent, indent_guides)
  else:
    vprint(tree)

# Returns a list of list of terms
def get_terms(ltl_asts):
  lot = []
  for a in ltl_asts:
    lot.append(_get_terms(a))
  return lot

# Create a list of terms encountered when stepping through the AST.
# Additionally, for each term the number of subelements contained in its
# first branch is stored. This allows to directly infer the index of
# the second argument to a binary function (the first argument always
# follows immediately after the operation in the list).
#
# NB: The return value is only valid if terms is not given explicitly.
# In other cases it is to be used in recursive fashion internally.
def _get_terms(ltl_ast, terms=None, cnt=0):
  ret_terms = False
  if terms == None:
    terms = []
    ret_terms = True
  cur = [ltl_ast, 1]
  cnt += 1
  terms.append(cur)
  if not isinstance(ltl_ast, bool):
    children = len(ltl_ast)-1
    if children > 0:
      cnts = [0]*children
      for i, c in enumerate(ltl_ast[1:]):
        cnts[i] = _get_terms(c, terms, 0)
        cnt += cnts[i]
      cur[1] = cnts[0]
  return terms if ret_terms else cnt

# PLY does try too much recovery when raising an ordinary SyntaxError
# within grammer productions. By throwing a different type errors are
# escalated appropriately. Defining a dedicated eases their handling.
class ForcedSyntaxError(Exception):
  pass

# YACC rules
class parser(object):
  start = 'formula' # Make sure we use the right rule as root of the grammar
  tokens = _lexer.tokens
  precedence = (
    ('left','OR','AND','IMP','SINCE','UNTIL'),
    ('right','NOT','S_PREV','W_PREV','S_NEXT','W_NEXT','ONCE','HIST','EVENTUALLY','ALWAYS'),
    ('left', 'NEWLINE'),
  )

  # dictionary of symbols
  #   keys are supplied by set_variables
  #   values are assigned by the parser
  syms = { }
  sym_nxt = 0

  def __init__(self, debug, **kwargs):
    import ply.yacc as yacc
    self.lexer = _lexer(debug=debug)
    self.parser = yacc.yacc(module=self, write_tables=debug, debug=debug)

  def set_variables(self, variables):
    for v,k in enumerate(variables):
      self.syms[k] = -1

  ######### Helper functions #########
  def p_error(self, t):
      s=""
      if t == None:
        s = 'Unexpected end of input. Maybe there are unbalanced parentheses?'
      else:
        s = "Syntax error at line %d near '%s'" % (t.lineno, t.value)
      raise ForcedSyntaxError("LTL Parser error: %s" % s)

  def p_formula(self, t):
      '''formula : start expressions'''
      vvprint("Finished parsing")
      t[0] = t[2]

  def p_start(self, t):
      '''start : newlines
               |
      '''
      vvprint("Starting parsing") # and trim leading newlines

  def p_expressions(self, t):
      '''expressions : exlist
                     | single_expression
      '''
      t[0] = t[1]
      t[0].reverse() # Output them as found in the input

  def p_single_expression(self, t):
      '''single_expression : expression'''
      t[0] = [t[1]]

  def p_exlist(self, t):
      '''exlist : exlist_iter
                | exlist_end
      '''
      t[0] = t[1]

  def p_exlist_iter(self, t):
      '''exlist_iter : expression newlines exlist
      '''
      t[0] = t[3]
      t[0].append(t[1])

  def p_exlist_end(self, t):
      '''exlist_end : expression newlines
      '''
      t[0] = [t[1]]

  def p_newlines(self, t):
      '''newlines : NEWLINE
                  | newlines NEWLINE
      '''
      pass

  ######### NULLARY OPs #########
  def p_expression_group(self, t):
      '''expression : '(' expression ')' '''
      t[0] = t[2]

  def p_expression_bool(self, t):
      '''expression : BOOL'''
      t[0] = t[1]

  def p_expression_sym(self, t):
      '''expression : SYM'''
      if not t[1] in self.syms:
        raise ForcedSyntaxError("Syntax error: symbol found in formula at line %d that is not contained in trace: '%s'" % (t.lexer.lineno, t[1]))
      val = self.syms[t[1]]
      if (val == -1):
        val = self.sym_nxt
        self.syms[t[1]] = val
        self.sym_nxt += 1
        vvprint("new sym: %s (%d)" % (t[1], val))
      t[0] = t[1]

  ######### UNARY OPs #########
  def p_expression_unop_not(self, t):
      '''expression : NOT expression'''
      if isinstance(t[2], bool):
        t[0] = not t[2]
      else:
        t[0] = ("NOT", t[2])

  def p_expression_unop_eventually(self, t):
      '''expression : EVENTUALLY expression'''
      t[0] = ("EVENTUALLY", t[2])

  def p_expression_unop_always(self, t):
      '''expression : ALWAYS expression'''
      t[0] = ("ALWAYS", t[2])

  def p_expression_unop_s_prev(self, t):
      '''expression : S_PREV expression'''
      t[0] = ("S_PREV", t[2])

  def p_expression_unop_w_prev(self, t):
      '''expression : W_PREV expression'''
      t[0] = ("W_PREV", t[2])

  def p_expression_unop_s_next(self, t):
      '''expression : S_NEXT expression'''
      t[0] = ("S_NEXT", t[2])

  def p_expression_unop_w_next(self, t):
      '''expression : W_NEXT expression'''
      t[0] = ("W_NEXT", t[2])

  def p_expression_unop_once(self, t):
      '''expression : ONCE expression'''
      t[0] = ("ONCE", t[2])

  def p_expression_unop_hist(self, t):
      '''expression : HIST expression'''
      t[0] = ("HIST", t[2])

  ######### BINARY OPs #########
  def p_expression_binop_or(self, t):
      '''expression : expression OR expression'''
      if isinstance(t[1], bool) and isinstance(t[3], bool):
        t[0] = t[1] or t[3]
      elif (isinstance(t[1], bool) and t[1]) or (isinstance(t[3], bool) and t[3]):
        t[0] = True
      elif isinstance(t[1], bool):
        t[0] = t[3]
      elif isinstance(t[3], bool):
        t[0] = t[1]
      else:
        t[0] = ("OR", t[1], t[3])

  def p_expression_binop_and(self, t):
      '''expression : expression AND expression'''
      if isinstance(t[1], bool) and isinstance(t[3], bool):
        t[0] = t[1] and t[3]
      elif (isinstance(t[1], bool) and not t[1]) or (isinstance(t[3], bool) and not t[3]):
        t[0] = False
      elif isinstance(t[1], bool):
        t[0] = t[3]
      elif isinstance(t[3], bool):
        t[0] = t[1]
      else:
        t[0] = ("AND", t[1], t[3])

  def p_expression_binop_imp(self, t):
      '''expression : expression IMP expression'''
      if isinstance(t[1], bool) and isinstance(t[3], bool):
        t[0] = not t[1] or t[3]
      elif isinstance(t[1], bool) and t[1]:
        t[0] = t[3]
      elif isinstance(t[1], bool) and not t[1]:
        t[0] = True
      else:
        t[0] = ("IMP", t[1], t[3])

  # FIXME: SINCE and UNTIL could be optimized similarly
  def p_expression_binop_since(self, t):
      '''expression : expression SINCE expression'''
      t[0] = ("SINCE", t[1], t[3])

  def p_expression_binop_until(self, t):
      '''expression : expression UNTIL expression'''
      t[0] = ("UNTIL", t[1], t[3])
