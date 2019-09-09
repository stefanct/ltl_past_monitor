import ast
import pathlib
from debug import *


####################
# Helper functions #
####################

# S_PREV, W_PREV a: "d[i-1][a]"
def prev(term, term_i, args):
  return ast.parse("d[i-1][{a}]".format(a=args[0]))

# Get value of other term with index a of current time step
def init_target(term, term_i, args):
  return ast.parse("d[i][{a}]".format(a=args[0]))

######################################
# Hashmap of initialization routines #
######################################
init_dict = {
  ###################################################################################################
  # Nullary operators (atoms, truth values)                                                         #
  ###################################################################################################
  # boolean: b
  'bool': lambda term, term_i, b:
    ast.parse("{0}".format(b)),

  # $atom: state['atom']
  'atom': lambda term, term_i, atom:
    ast.parse("state['{atom}']".format(atom=atom)),

  ###################################################################################################
  # Unary operators ('NOT','S_PREV','W_PREV','S_NEXT','W_NEXT','ONCE','HIST','EVENTUALLY','ALWAYS') #
  # To initialize pre[i] we simply need to take into account pre[args[0]] (args[1] is ignored)      #
  ###################################################################################################
  # NOT: not d[i][a]
  'NOT': lambda term, term_i, args:
    ast.parse("not d[i][{a}] if d[i][{a}] is not None else None".format(a=args[0])),

  # S_PREV: 0
  'S_PREV': lambda term, term_i, args:
    ast.parse("False"),

  # W_PREV: a - This is actually the only difference to S_PREV
  'W_PREV': init_target,

  # ONCE a: a
  'ONCE': init_target,

  # HIST a: a
  'HIST': init_target,

  # W_NEXT a: None
  'W_NEXT': lambda term, term_i, args:
    ast.parse("None"),

  #######################################################
  # Binary operators ('OR','AND','IMP','SINCE','UNTIL') #
  #######################################################
  # Binops need a bit more context to gather their inputs.
  # This needs to be done at build-time so this becomes relatively easy again:
  # We assume here to simply get the two respective indices as inputs.
  
  # $a OR $b: d[i][a] or d[i][b]"
  'OR': lambda term, term_i, args:
    ast.parse("d[i][{a}] or d[i][{b}] if None not in [d[i][{a}],d[i][{b}]] else None".format(a=args[0], b=args[1])),

  # $a AND $b: d[i][i] = d[i][a] and d[i][b]
  'AND': lambda term, term_i, args:
    ast.parse("d[i][{a}] and d[i][{b}] if None not in [d[i][{a}],d[i][{b}]] else None".format(a=args[0], b=args[1])),

  # $a IMP $b: not d[i][a]) or d[i][b]
  'IMP': lambda term, term_i, args:
    ast.parse("not d[i][{a}] or d[i][{b}] if None not in [d[i][{a}],d[i][{b}]] else None".format(a=args[0], b=args[1])),

  # $a SINCE $b: d[i][b]
  'SINCE': lambda term, term_i, args:
    ast.parse("d[i][{b}]".format(b=args[1])),
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

  # $a SINCE $b: d[i][b] or (d[i][a] and d[i-1][term_i])
  'SINCE': lambda term, term_i, args:
    ast.parse("d[i][{b}] or (d[i][{a}] and d[i-1][{term_i}]) if None not in [d[i][{a}],d[i][{b}],d[i-1][{term_i}]] else None".format(a=args[0], b=args[1], term_i=term_i)),

  # ONCE a: d[i-1][i] or d[i][a]"
  'ONCE': lambda term, term_i, args:
    ast.parse("d[i-1][{term_i}] or d[i][{a}] if None not in [d[i-1][{term_i}],d[i][{a}]] else None".format(term_i=term_i, a=args[0])),

  # HIST a: d[i-1][i] and d[i][a]
  'HIST': lambda term, term_i, args:
    ast.parse("d[i-1][{term_i}] and d[i][{a}] if None not in [d[i-1][{term_i}],d[i][{a}]] else None".format(term_i=term_i, a=args[0])),
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

  def template_modifier(self, op_dict, node):
    nodes = []
    for i, tt in enumerate(reversed(self.terms)):
      # tt[0] is the actual term while
      # tt[1] the offset of the second argument (if any)
      t = tt[0]
      newvalue = None
      term_idx = self.term_cnt-1-i
      if isinstance(t, str):
        vprint("d[i][%d] = state[%s]" % (term_idx, t))
        newvalue = op_dict['atom'](t, term_idx, t)
      elif isinstance(t, tuple):
        op = t[0]
        try:
          assign = op_dict[op]
        except KeyError as e:
          print("FIXME: Unknown operation '%s'" % (op))
          continue

        a = term_idx + 1
        b = term_idx + 1 + tt[1]
        vprint("d[i][%d] = %s(..., d[i][%d], d[i][%d])" % (term_idx, op, a, b))
        newvalue = assign(t, term_idx, [a, b])
      elif isinstance(t, bool):
        vprint("d[i][%d] = %s" % (term_idx, str(t)))
        newvalue = op_dict['bool'](t, term_idx, t)
      else:
        raise Exception("Unknown term type at %d: %s (%s)" % (i, type(t), t))

      lhs = ast.parse("d[i][{term_i}] = True".format(term_i=term_idx))

      newnode = ast.Assign(
        # The parsed ASTs contain a whole module that we need to unwrap
        targets=[lhs.body[0].targets[0]],
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
      vprint("Generating ptLTL initialization")
      node = self.template_modifier(init_dict, node)
    elif (isinstance(target, ast.Name) and target.id =='template_loop' and node.value.s == 'template_loop'):
      vprint("\nGenerating ptLTL loop assignments")
      node = self.template_modifier(loop_dict, node)

    return node
