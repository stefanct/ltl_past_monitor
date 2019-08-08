#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import re
import glob
import datetime
import sys
import argparse
import pathlib
import csv
import ltl_parser
import ltlpast
from debug import *

def verify_csv(path, ltl_file, debug=False):
  if isinstance(path, str):
    path = pathlib.Path(path)
  with path.open(mode='r', newline='') as csv_file:
    csv_reader = csv.DictReader(csv_file, skipinitialspace=True)
    atoms = csv_reader.fieldnames

    if (atoms == None):
      raise SyntaxError("Could not parse variable names in CSV file (%s)" % path.name)

    terms = parse_ltl(ltl_file, atoms, debug)
    solve = ltlpast.generate_solver(terms, atoms)
    vprint("\nRunning verifier...")
    return solve(csv_reader, len(terms))

def parse_ltl(path, variables, debug):
  p = ltl_parser.parser(debug)
  p.set_variables(variables)
  if isinstance(path, str):
    path = pathlib.Path(path)
  with path.open(mode='r', newline=None) as ltl_file:
    text = ltl_file.read()
  ltl_ast = p.parser.parse(text)
  vprint("\nLTL Tree:")
  ltl_parser.print_tree(ltl_ast, indent_guides=True)
  vprintn("\nLTL Line:")
  ltl_parser.print_tree_oneline(ltl_ast)
  vprint()
  return ltl_parser.get_terms(ltl_ast)

if __name__ == "__main__":
  import locale
  locale.setlocale(locale.LC_ALL, '') # do not ignore locale settings of the environment. yes, python needs to be told this m(

  # Argument parsing
  argparser = argparse.ArgumentParser(description='LTL+past offline verifier.')
  argparser.add_argument('ltl_file', action='store', help=('Path to the file containing the LTL+past specifications'))
  argparser.add_argument('csv_file', action='store', help=('Path to the file containing the trace'))
  argparser.add_argument('-v', action='count', dest='verbose', default=0, help='How much output is printed')
  argparser.add_argument('-d', action='store_true', dest='debug', help='Enable debug output of libraries')

  args = argparser.parse_args()

  set_verbosity(args.verbose)

  try:
    ret = verify_csv(args.csv_file, args.ltl_file, args.debug)
  except Exception as e:
    print("%s Exiting." % e)
    exit(2)

  if (ret != 0):
    print("Fail")
  else:
    print("Pass")
  exit(ret)
