import ast
from collections import Iterable
def get_terms(ltl_ast, terms):
  if isinstance(ltl_ast, Iterable):
    terms.append(ltl_ast)
    for c in ltl_ast[1:]:
      get_terms(c, terms)
  elif ltl_ast != None:
    terms.append(ltl_ast)


class transformer(ast.NodeTransformer):
  def __init__(
                self,
                ltl_ast,
                variables,
              ):
    self.ltl_ast = ltl_ast
    self.variables = variables

    self.terms = []
    get_terms(self.ltl_ast, self.terms)
    self.term_cnt = len(self.terms)

    super().__init__()

  def visit_Assign(self, node):
    target = node.targets[0]
    if (isinstance(target, ast.Name) and target.id =='template_init' and node.value.s == 'template_init'):
      print(node.value.s)
      node.value = ast.Str('haha')
      ast.fix_missing_locations(node)
      return [node, node]
    return node
