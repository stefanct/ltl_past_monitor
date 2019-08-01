# based on PLY's calc.py

import re
from debug import *
from collections import Iterable

class lexer(object):
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

  # Identifiers
  t_SYM     = r'[a-zA-Z_][a-zA-Z0-9_]*'

  t_ignore_comment = r'(//.*)|([#].*)'
  # FIXME: multiline please?
  # t_ignore_multi_comment = r'(/\*(.|\n)*?\*/)|(//.*)|([#].*)'

  literals = ['(', ')']

  def t_BOOL(self, t):
      r'0|1|true|false'
      if len(t.value) == 1:
        try:
            t.value = int(t.value)
            t.value = bool(t.value)
        except ValueError as e:
            raise Exception("Not a boolean value: %s" % t.value, e)
      return t

  # Ignored characters
  t_ignore = " \t"

  def t_NEWLINE(self, t):
      r'\n+'
      t.lexer.lineno += t.value.count("\n")
      return t

  def t_error(self, t):
      print("Illegal character '%s'" % t.value[0])
      t.lexer.skip(1)
      






# YACC rules
class ltl_parser(object):
  start = 'formula' # Make sure we use the right rule as root of the grammar
  tokens = lexer.tokens
  precedence = (
    ('left', 'NEWLINE'),
    ('right','NOT','S_PREV','W_PREV','S_NEXT','W_NEXT','ONCE','HIST','EVENTUALLY','ALWAYS'),
    ('left','OR','AND','IMP','SINCE','UNTIL'),
  )

  # dictionary of symbols
  #   keys are supplied by set_variables
  #   values are assigned by the parser
  syms = { }
  sym_nxt = 0

  def __init__(self, debug, **kwargs):
    import ply.yacc as yacc
    self.lexer = lexer(debug=debug)
    self.parser = yacc.yacc(module=self, write_tables=debug, debug=debug)

  def set_variables(self, variables):
    for v,k in enumerate(variables):
      self.syms[k] = -1

  # Print the tree in Polish notation in one line w/o a newline at the end
  def print_tree_oneline(self, tree):
    if isinstance(tree, Iterable):
      # Test for forest instead of tree and print individual trees separately
      if tree[0] == '\n':
        for c in tree[1:-1]:
          self.print_tree_oneline(c)
          vprintn(", ")
        else:
          self.print_tree_oneline(tree[-1])
        return

      vprintn(tree[0])
      if len(tree) > 1:
        vprintn("(")
      for c in tree[1:-1]:
        self.print_tree_oneline(c)
        vprintn(",")
      if len(tree) > 1:
        self.print_tree_oneline(tree[-1])
        vprintn(")")
    else:
      vprintn(tree)

  def print_tree(self, tree, cur_indent=0, indent_guides=False):
    _INDENT = 4
    # Test for forest instead of tree and print individual trees separately
    if isinstance(tree, Iterable) and tree[0] == '\n':
      for c in tree[1:]:
        self.print_tree(c, cur_indent, indent_guides)
        vprint()
      return

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
        self.print_tree(c, cur_indent, indent_guides)
    else:
      vprint(tree)

  ######### Helper functions #########
  def p_error(self, t):
      s=""
      if t == None:
        s = 'Unexpected end of input. Probably unbalanced parentheses.'
      else:
        s = "Syntax error at line %d: '%s'" % (t.lineno, t.value)
      raise Exception("Parser error: %s" % s)

  def p_formula(self, t):
      '''formula : start exlist'''
      vvprint("Finished parsing")
      t[0] = t[2]

  def p_start(self, t):
      '''start :'''
      vvprint("Starting parsing")

  ## Expression lists + newlines
  def p_exlist_nl_exl(self, t):
      '''exlist : NEWLINE exlist'''
      t[0] = t[2]

  def p_exlist_exl_nl_exl(self, t):
      '''exlist : exlist NEWLINE exlist'''
      t[0] = ('\n', t[1], t[3])

  def p_exlist(self, t):
      '''exlist : expression
                | exlist NEWLINE
      '''
      t[0] = t[1]

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
        raise LookupError("Symbol found in formula that is not contained in trace: '%s'" % t[1])
      val = self.syms[t[1]]
      if (val == -1):
        val = self.sym_nxt
        self.syms[t[1]] = val
        self.sym_nxt += 1
        vvprint("new sym: %s (%d)" % (t[1], val))
      t[0] = t[1]

  ######### UNARY OPs #########
  def p_expression_unop(self, t):
      '''expression : NOT expression'''
      if isinstance(t[2], int):
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
      if isinstance(t[1], int) and isinstance(t[3], int):
        t[0] = t[1] or t[3]
      else:
        t[0] = ("OR", t[1], t[3])

  def p_expression_binop_and(self, t):
      '''expression : expression AND expression'''
      if isinstance(t[1], int) and isinstance(t[3], int):
        t[0] = t[1] and t[3]
      else:
        t[0] = ("AND", t[1], t[3])

  def p_expression_binop_imp(self, t):
      '''expression : expression IMP expression'''
      if isinstance(t[1], int) and isinstance(t[3], int):
        t[0] = not t[1] or t[3]
      else:
        t[0] = ("IMP", t[1], t[3])

  def p_expression_binop_since(self, t):
      '''expression : expression SINCE expression'''
      t[0] = ("SINCE", t[1], t[3])

  def p_expression_binop_until(self, t):
      '''expression : expression UNTIL expression'''
      t[0] = ("UNTIL", t[1], t[3])
