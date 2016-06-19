#!/usr/bin/env python3.4
# coding: utf-8

"""
Defines the parsers for the REPL commands.

Contributors: myrma
"""

import re

from acid.repl.command import *
from acid.parser import *


def parse_repl_line(line):
    if re.match(r'^\s*$', line):
        return Newline()

    m = re.match(r':!(?P<cmd>.*)', line)

    if m is not None:
        cmd = m.group('cmd')
        return OSCommand(cmd)

    m = re.match(r':(?P<name>\w+)(?P<args>.*)', line)

    if m is not None:
        name = m.group('name')
        args = m.group('args').split()
        return Command(name, args)

    parser = Parser(line, '<stdin>')

    try:
        return EvalExpr(parser.parse(Expr))
    except ParseError:
        try:
            return EvalStmt(parser.parse(Stmt))
        except ParseError:
            msg = 'Failed to parse REPL command.'
            raise ParseError(line, SourcePos(0, 0), msg) from None
