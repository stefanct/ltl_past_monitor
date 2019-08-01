# based on PLY's calc.py

from debug import *
from collections import Iterable

class lexer(object):
  # global tokens

  tokens = (
      'NUMBER', 'SYM', # 0 INPUTS
      'NOT','S_PREV','W_PREV','S_NEXT','W_NEXT','ONCE','HIST','EVENTUALLY','ALWAYS', # 1 INPUTS
      'OR','AND','IMP','SINCE','UNTIL', # 2 INPUTS
      )

  # constructor
  def __init__(self,**kwargs):
    import ply.lex as lex
    self.lexlexer = lex.lex(module=self, **kwargs)

  # Define all keywords as functions to make sure they are ordered before t_SYM
  # We could also filter them out as reserved words in a t_SYM function (as suggested by the PLY docs)
  def t_NOT(self, t):
    r'(not)|(NOT)|(!)'
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
    r'(or)|(OR)|(v)'
    return t

  def t_AND(self, t):
    r'(and)|(AND)|(\^)'
    return t

  def t_IMP(self, t):
    r'(implies)|(IMP(LIES)?)|(->)'
    return t

  def t_SINCE(self, t):
    r'(since)|(SINCE)'
    return t

  def t_UNTIL(self, t):
    r'(until)|(UNTIL)'
    return t

  # Identifiers
  t_SYM     = r'[a-zA-Z_][a-zA-Z0-9_]*'

  t_ignore_comment = r'(//.*)|([#].*)'
  # FIXME: multiline please?
  # t_ignore_multi_comment = r'(/\*(.|\n)*?\*/)|(//.*)|([#].*)'

  literals = ['(', ')']

  def t_NUMBER(self, t):
      r'\d+'
      try:
          t.value = int(t.value)
      except ValueError:
          print("Integer value too large %d", t.value)
          t.value = 0
      except Error as e:
          print(e)
      return t

  # Ignored characters
  t_ignore = " \t"

  def t_newline(self, t):
      r'\n+'
      t.lexer.lineno += t.value.count("\n")
      
  def t_error(self, t):
      print("Illegal character '%s'" % t.value[0])
      t.lexer.skip(1)
      






# YACC rules
class ltl_parser(object):
  tokens = lexer.tokens
  precedence = (
    ('right','NOT','S_PREV','W_PREV','S_NEXT','W_NEXT','ONCE','HIST','EVENTUALLY','ALWAYS'),
    ('left','OR','AND','IMP','SINCE','UNTIL'),
  )

  # dictionary of symbols, supplied by set_variables
  syms = { }

  def __init__(self, debug, **kwargs):
    import ply.yacc as yacc
    self.lexer = lexer(debug=debug)
    self.parser = yacc.yacc(module=self, write_tables=debug, debug=debug)

  def set_variables(self, variables):
    for v,k in enumerate(variables):
      self.syms[k] = v

  # Print the tree in Polish notation in one line w/o a newline at the end
  def print_tree_oneline(self, tree):
    if isinstance(tree, Iterable):
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


  # YACC functions
  def p_expression_unop(self, t):
      '''expression : NOT expression
      '''
      t[0] = not t[2]

  def p_expression_unop_res(self, t):
      '''expression : S_PREV expression
                    | W_PREV expression
                    | S_NEXT expression
                    | W_NEXT expression
                    | ONCE expression
                    | HIST expression
                    | EVENTUALLY expression
                    | ALWAYS expression
      '''
      print("[1]: %s, [2]: %s" % (t[1], t[2]))

  def p_expression_binop(self, t):
      '''expression : expression OR expression
                    | expression AND expression
                    | expression IMP expression
                    | expression SINCE expression
                    | expression UNTIL expression
      '''
      if t[2] == '+'  : t[0] = t[1] + t[3]
      elif t[2] == '-': t[0] = t[1] - t[3]
      elif t[2] == '*': t[0] = t[1] * t[3]
      elif t[2] == '/': t[0] = t[1] / t[3]
      else:
        print("Unknown binop %s" % t[2])

  def p_expression_group(self, t):
      '''expression : '(' expression ')' '''
      t[0] = t[2]
      print("(((())))")

  def p_expression_number(self, t):
      'expression : NUMBER'
      t[0] = t[1]

  def p_expression_sym(self, t):
      'expression : SYM'
      try:
          t[0] = self.syms[t[1]]
      except LookupError:
          print("Undefined symbol '%s'" % t[1])
          t[0] = 0
      except Error as e:
          print("Unknown error in sym lookup: %s" % (e))

  def p_error(self, t):
      print("Syntax error at '%s'" % t.value)
