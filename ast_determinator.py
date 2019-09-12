#!/usr/bin/python3

# This script outputs the AST of its first argument
import sys
import astpretty
import ast

if __name__ == '__main__':
  tree = ast.parse(sys.argv[1])
  astpretty.pprint(tree, show_offsets=False, indent='  ')
