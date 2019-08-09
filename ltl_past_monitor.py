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
import distutils.util
import ltl_parser
import ltlpast
from debug import *

# Verifies that all formulas in ltl_file are satisfied by the states contained in the CSV file.
# Returns the number of formulas that are *not* satisfied.
def verify_csv(path, ltl_file, debug=False):
  if isinstance(path, str):
    path = pathlib.Path(path)

  states = None
  with path.open(mode='r', newline='') as csv_file:
    csv_reader = csv.DictReader(csv_file, skipinitialspace=True)
    atoms = csv_reader.fieldnames
    if (atoms == None):
      raise SyntaxError("Could not parse variable names in CSV file (%s)" % path.name)

    states = list(csv_reader) # Slurp the CSV file

  # Convert state tuples from strings to boolean values
  for s in states:
    for k in s.keys():
      s[k] = distutils.util.strtobool(s[k])

  list_of_terms = parse_ltl(ltl_file, atoms, debug)
  ret = 0
  for i, t in enumerate(list_of_terms):
    vprint("Generating solver for formula %d..." % i)
    solve = ltlpast.generate_solver(t, atoms)
    vprint("\nRunning verifier for formula %d..." % i)
    cur = solve(iter(states), len(t))
    vprintn("Formula %d " % i)
    vprint("failed" if cur != 0 else "passed")
    vprint()
    ret += cur
  return ret

def parse_ltl(path, variables, debug):
  p = ltl_parser.parser(debug)
  p.set_variables(variables)
  if isinstance(path, str):
    path = pathlib.Path(path)
  with path.open(mode='r', newline=None) as ltl_file:
    text = ltl_file.read()
  ltl_asts = p.parser.parse(text)
  vprint("\nLTL Tree/Forest:")
  ltl_parser.print_forest(ltl_asts, indent_guides=True)
  vprint("\nLTL Line(s):")
  ltl_parser.print_forest_oneline(ltl_asts)
  vprint()
  return ltl_parser.get_terms(ltl_asts)

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
