#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import re
import glob
import datetime
import sys
import argparse
import csv
import ltl_parser
from debug import *

WARN = '\033[33m'
ENDC = '\033[0m'

def parse_ltl(path, variables, debug):
  p = ltl_parser.parser(debug)
  p.set_variables(variables)
  try:
    with open(path, mode='r', newline=None) as ltl_file:
      text = ltl_file.read()
    ltl_ast = p.parser.parse(text)
  except Exception as e:
    print("%s Exiting." % e.args[0])
    exit(1)

  vprint("Tree:")
  ltl_parser.print_tree(ltl_ast, indent_guides=True)
  vprintn("Line: ")
  ltl_parser.print_tree_oneline(ltl_ast)
  print()

if __name__ == "__main__":
  import locale
  locale.setlocale(locale.LC_ALL, '') # do not ignore locale settings of the environment. yes, python needs to be told this m(

  global verbose

  # Argument parsing
  argparser = argparse.ArgumentParser(description='LTL+past offline verifier.')
  argparser.add_argument('ltl_file', action='store', help=('Path to the file containing the LTL+past specifications'))
  argparser.add_argument('csv_file', action='store', help=('Path to the file containing the trace'))
  argparser.add_argument('-v', action='count', dest='verbose', default=0, help='How much output is printed')
  argparser.add_argument('-d', action='store_true', dest='debug', help='Enable debug output of libraries')

  args = argparser.parse_args()

  verbose = args.verbose
  
  set_verbosity(verbose)

  with open(args.csv_file, mode='r', newline='') as csv_file:
    csv_reader = csv.DictReader(csv_file, skipinitialspace=True)
    parse_ltl(args.ltl_file, csv_reader.fieldnames, args.debug)
