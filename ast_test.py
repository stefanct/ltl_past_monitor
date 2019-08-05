import sys
import astpretty
import ast
import ltlpast

TRACE = [
  {"p": 1, "q": 1, "r": 1, "s": 1},
  {"p": 1, "q": 0, "r": 0, "s": 0},
  {"p": 1, "q": 0, "r": 1, "s": 0},
]

TERM_CNT = 9

def main(*args):
  namespace = {}
  with open("template.py") as f:
    tree = ast.parse(f.read())
    trans = ltlpast.transformer(TERM_CNT, ["p", "q", "r", "s",])
    trans.visit(tree)
    astpretty.pprint(tree, show_offsets=False)
    exec(compile(tree, f.name, "exec"), namespace)

  ret = namespace['solve'](TRACE, TERM_CNT)
  if (ret == 1):
    print("Fail")
  else:
    print("Pass")
  exit(ret)

if __name__ == '__main__':
  sys.exit(main(*sys.argv))
