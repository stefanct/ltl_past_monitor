import ast
import pathlib
from debug import *

init_dict = {
  # $atom: pre[i] = state['$atom']
  'atom': lambda target, i, atom:
    ast.Assign(targets=[ast.Subscript(value=ast.Name(id=target, ctx=ast.Load()), slice=ast.Index(value=ast.Num(n=i)), ctx=ast.Store())],
               value=ast.Subscript(value=ast.Name(id='state', ctx=ast.Load()), slice=ast.Index(value=ast.Str(s=atom)), ctx=ast.Load())
    ),
}


loop_dict = {
  # $atom: now[i] = state['$atom']
  'atom': init_dict['atom'],
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
      newnode = None
      term_idx = self.term_cnt-1-i
      if isinstance(t, str):
        vprint("%s[%d] = state[%s]" % (target, term_idx, t))
        newnode = op_dict['atom'](target, term_idx, t)
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
        newnode = assign(target, term_idx, [a, b])
      else:
        raise Exception("Unknown term type at %d: %s (%s)" % (i, type(t), t))

      newnode.lineno = node.lineno
      newnode.col_offset = node.col_offset
      ast.fix_missing_locations(newnode)
      nodes.append(newnode)
    return nodes

  def visit_Assign(self, node):
    target = node.targets[0]

    if (isinstance(target, ast.Name) and target.id =='template_init' and node.value.s == 'template_init'):
      vprint("\nGenerating initialization")
      return self.template_modifier(init_dict, 'pre', node)

    if (isinstance(target, ast.Name) and target.id =='template_loop' and node.value.s == 'template_loop'):
      vprint("\nGenerating loop assignments")
      return self.template_modifier(loop_dict, 'now', node)

    return node
