import ast

class transformer(ast.NodeTransformer):
  def visit_Assign(self, node):
    target = node.targets[0]
    if (isinstance(target, ast.Name) and target.id =='template_init' and node.value.s == 'template_init'):
      print(node.value.s)
      node.value = ast.Str('haha')
      ast.fix_missing_locations(node)
      return [node, node]
    return node
