#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import re
import glob
import datetime
import sys
import argparse
import csv

WARN = '\033[33m'
ENDC = '\033[0m'

# Based on https://realpython.com/python-csv/#reading-csv-files-into-a-dictionary-with-csv
def parse_csv(path):
  with open(path, mode='r', newline='') as csv_file:
    csv_reader = csv.DictReader(csv_file, skipinitialspace=True)
    # line_count = 0
    vprint('Variables names are %s' % ", ".join(csv_reader.fieldnames))
    for row in csv_reader:
      vvprint('%s' % ", ".join(filter(None, row.values())))
    vprint("Reading %d lines of %s completed" % (csv_reader.line_num, path))
    return csv_reader

def parse_ltl(path, variables, debug):
  with open(path, mode='r', newline='') as ltl_file:
    from ltl_parser import ltl_parser
    p = ltl_parser(debug)
    p.set_variables(variables)
    p.parser.parse(ltl_file.read())

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
  
  vprint = lambda *a, **k: None # do-nothing function
  vvprint = lambda *a, **k: None # do-nothing function
  if verbose > 0:
    def vprint(*args, **kwargs):
      print(*args, **kwargs)
    if verbose > 1:
      def vvprint(*args, **kwargs):
        print(*args, **kwargs)

  csv = parse_csv(args.csv_file)
  parse_ltl(args.ltl_file, csv.fieldnames, args.debug)
