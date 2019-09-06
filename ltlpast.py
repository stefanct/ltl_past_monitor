import ast
import pathlib
from debug import *


####################
# Helper functions #
####################

# S_PREV, W_PREV a: "now[i] = pre[a]"
def prev(target, term, term_i, args):
  return ast.parse("pre[{a}]".format(a=args[0]))

# Simply set target[i] = target[a]
def init_target(target, term, term_i, args):
  return ast.parse("{t}[{a}]".format(t=target, a=args[0]))

######################################
# Hashmap of initialization routines #
######################################
init_dict = {
  ###################################################################################################
  # Nullary operators (atoms, truth values)                                                         #
  ###################################################################################################
  # boolean: target[i] = b
  'bool': lambda target, term, term_i, b:
    ast.parse("{b}".format(b=b)),

  # $atom: target[i] = state['atom']
  'atom': lambda target, term, term_i, atom:
    ast.parse("state['{atom}']".format(atom=atom)),

  ###################################################################################################
  # Unary operators ('NOT','S_PREV','W_PREV','S_NEXT','W_NEXT','ONCE','HIST','EVENTUALLY','ALWAYS') #
  # To initialize pre[i] we simply need to take into account pre[args[0]] (args[1] is ignored)      #
  ###################################################################################################
  # NOT: "target[i] = not target[args[0]]"
  'NOT': lambda target, term, term_i, args:
    ast.parse("not {0}[{1[0]}] if {0}[{1[0]}] is not None else None".format(target, args)),

  # S_PREV: "target[i] = 0"
  'S_PREV': lambda target, term, term_i, args:
    ast.parse("False"),

  # W_PREV: "target[i] = a" - This is actually the only difference to S_PREV
  'W_PREV': init_target,

  # ONCE a: "target[i] = a"
  'ONCE': init_target,

  # HIST a: "target[i] = a"
  'HIST': init_target,

  # W_NEXT a: "target[i] = None"
  'W_NEXT': lambda target, term, term_i, args:
    ast.parse("None"),

  #######################################################
  # Binary operators ('OR','AND','IMP','SINCE','UNTIL') #
  #######################################################
  # Binops need a bit more context to gather their inputs.
  # This needs to be done at build-time so this becomes relatively easy again:
  # We assume here to simply get the two respective indices as inputs.
  
  # $a OR $b: "target[i] = target[a] or target[b]"
  'OR': lambda target, term, term_i, args:
    ast.parse("{0}[{a}] or {0}[{b}] if None not in [{0}[{a}],{0}[{b}]] else None".format(target, a=args[0], b=args[1])),

  # $a AND $b: "target[i] = target[a] and target[b]"
  'AND': lambda target, term, term_i, args:
    ast.parse("{0}[{a}] and {0}[{b}] if None not in [{0}[{a}],{0}[{b}]] else None".format(target, a=args[0], b=args[1])),

  # $a IMP $b: "target[i] = (not target[a]) or target[b]"
  'IMP': lambda target, term, term_i, args:
    ast.parse("not {0}[{a}] or {0}[{b}] if None not in [{0}[{a}],{0}[{b}]] else None".format(target, a=args[0], b=args[1])),

  # $a SINCE $b: "target[i] = target[b]"
  'SINCE': lambda target, term, term_i, args:
    ast.parse("{0}[{b}]".format(target, b=args[1])),
}

###############################
# Hashmap of loop assignments #
###############################
loop_dict = {
  'bool': init_dict['bool'],
  'atom': init_dict['atom'],
  'NOT': init_dict['NOT'],
  'AND': init_dict['AND'],
  'OR': init_dict['OR'],
  'IMP': init_dict['IMP'],

  'S_PREV': prev,
  'W_PREV': prev,

  # $a SINCE $b: "target[i] = target[b] or (target[a] and pre[i])"
  'SINCE': lambda target, term, term_i, args:
    ast.parse("{t}[{b}] or ({t}[{a}] and pre[{i}]) if None not in [{t}[{a}],{t}[{b}],pre[{i}]] else None".format(t=target, a=args[0], b=args[1], i=term_i)),

  # ONCE a: "target[i] = pre[i] or target[a]"
  'ONCE': lambda target, term, term_i, args:
    ast.parse("pre[{i}] or {t}[{a}] if None not in [{t}[{a}],pre[{i}]] else None".format(i=term_i, t=target, a=args[0])),

  # HIST a: "target[i] = pre[i] and target[a]"
  'HIST': lambda target, term, term_i, args:
    ast.parse("pre[{i}] and {t}[{a}] if None not in [{t}[{a}],pre[{i}]] else None".format(i=term_i, t=target, a=args[0])),
}

def generate_solver(terms, atoms):
  namespace = {}
  # The template needs to reside in the same directory as this very file.
  # There is not much we can do on errors so we simply pass the exception up.
  with pathlib.Path(__file__).parent.joinpath('template.py').open() as f:
    temp_tree = ast.parse(f.read())
  trans = transformer(terms, atoms)
  trans.visit(temp_tree)
  exec(compile(temp_tree, f.name, "exec"), namespace)
  return namespace['solve']

class transformer(ast.NodeTransformer):
  def __init__(
                self,
                terms,
                variables,
              ):
    assert(terms != None and variables != None)

    self.variables = variables

    self.terms = terms
    self.term_cnt = len(self.terms)

    super().__init__()

  def template_modifier(self, op_dict, target, node):
    nodes = []
    for i, tt in enumerate(reversed(self.terms)):
      # tt[0] is the actual term while
      # tt[1] the offset of the second argument (if any)
      t = tt[0]
      newvalue = None
      term_idx = self.term_cnt-1-i
      if isinstance(t, str):
        vprint("%s[%d] = state[%s]" % (target, term_idx, t))
        newvalue = op_dict['atom'](target, t, term_idx, t)
      elif isinstance(t, tuple):
        op = t[0]
        try:
          assign = op_dict[op]
        except KeyError as e:
          print("FIXME: Unknown operation '%s'" % (op))
          continue

        a = term_idx + 1
        b = term_idx + 1 + tt[1]
        vprint("%s[%d] = %s(..., %s[%d], %s[%d])" % (target, term_idx, op, target, a, target, b))
        newvalue = assign(target, t, term_idx, [a, b])
      elif isinstance(t, bool):
        vprint("%s[%d] = %s" % (target, term_idx, str(t)))
        newvalue = op_dict['bool'](target, t, term_idx, t)
      else:
        raise Exception("Unknown term type at %d: %s (%s)" % (i, type(t), t))

      newnode = ast.Assign(
        targets=[ast.Subscript(value=ast.Name(id=target, ctx=ast.Load()), slice=ast.Index(value=ast.Num(n=term_idx)), ctx=ast.Store())],
        # The parsed ASTs contain a whole module that we need to unwrap
        value=newvalue.body[0].value
      )
      newnode.lineno = node.lineno
      newnode.col_offset = node.col_offset
      ast.fix_missing_locations(newnode)
      nodes.append(newnode)
    return nodes

  def visit_Assign(self, node):
    target = node.targets[0]

    if (isinstance(target, ast.Name) and target.id =='template_init' and node.value.s == 'template_init'):
      vprint("Generating initialization")
      return self.template_modifier(init_dict, 'pre', node)

    if (isinstance(target, ast.Name) and target.id =='template_loop' and node.value.s == 'template_loop'):
      vprint("\nGenerating loop assignments")
      return self.template_modifier(loop_dict, 'now', node)

    return node
