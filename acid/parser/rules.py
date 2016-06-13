#!/usr/bin/env python3.4
# coding: utf-8

"""
This module defines the parser rules. To define a custom parser rule, use this
snippet as a template:

	@Parser.register([NodeType], priority=[n])
	def [rule_name](self):
		# To consume a token of a given type:
		expected_token = self.expect([token type])

		node = self.consume([NodeType to consume])

		...  # Processing tokens

		return [AST node]

Contributors: myrma
"""

from acid.parser.parser import Parser
from acid.parser.lexer import *
from acid.parser.ast import *
from acid.exception import *


@Parser.register(Program, priority=1)
def consume_program(self):
	# the program instructions
	instrs = []

	while self.token_queue:
		try:
			# tries to parse an expression from the token queue
			instr = self.consume(Stmt)
		except ParseError:
			raise  # when no expression could be parsed
		else:
			# append the instruction to the program
			instrs.append(instr)

	# returns the resulting Program object.
	return Program(instrs, self.path)


@Parser.register(Declaration, priority=1)
def consume_declaration(self):
	self.expect(TokenType.LPAREN)
	self.expect(TokenType.DEFINE)

	atom = self.expect(TokenType.ATOM)
	name = atom.value

	value = self.consume(Expr)
	self.expect(TokenType.RPAREN)
	return Declaration(name, value)


@Parser.register(TypeDeclaration, priority=1)
def consume_type_declaration(self):
	self.expect(TokenType.LPAREN)
	self.expect(TokenType.HASTYPE)

	atom = self.expect(TokenType.ATOM)
	name = atom.value

	value = self.consume(Expr)
	self.expect(TokenType.RPAREN)
	return Declaration(name, value)


@Parser.register(TopLevelExpr, priority=2)
def consume_toplevel_expr(self):
	expr = self.consume(Expr)
	return TopLevelExpr(expr)


@Parser.register(Call, priority=2)
def consume_call(self):
	self.expect(TokenType.LPAREN)
	func = self.consume(Expr)

	args = []
	# consumes expressions as long as it parses.
	while True:
		try:
			arg = self.consume(Expr)
		except ParseError:
			break
		else:
			args.append(arg)

	self.expect(TokenType.RPAREN)

	return Call(func, args)


@Parser.register(Lambda, priority=1)
def consume_lambda(self):
	self.expect(TokenType.LPAREN)
	self.expect(TokenType.LAMBDA)
	self.expect(TokenType.LPAREN)

	params = []
	while self.token_queue[0].type == TokenType.ATOM:
		token = self.token_queue.pop(0)
		params.append(token.value)

	self.expect(TokenType.RPAREN)
	body = self.consume(Expr)
	self.expect(TokenType.RPAREN)
	return Lambda(params, body)


@Parser.register(Variable, priority=1)
def consume_variable(self):
	atom = self.expect(TokenType.ATOM)
	return Variable(atom.value)


@Parser.register(IntLiteral, priority=1)
def consume_int_literal(self):
	token = self.expect(TokenType.INT_LITERAL)
	return IntLiteral(int(token.value))


@Parser.register(FloatLiteral, priority=1)
def consume_float_literal(self):
	token = self.expect(TokenType.FLOAT_LITERAL)
	return FloatLiteral(float(token.value))


@Parser.register(CharLiteral, priority=1)
def consume_char_literal(self):
	token = self.expect(TokenType.CHAR_LITERAL)
	char = token.value.strip("'")
	return CharLiteral(char)


@Parser.register(StringLiteral, priority=1)
def consume_string_literal(self):
	token = self.expect(TokenType.STRING_LITERAL)

	# todo: find another way to unescape strings
	string = token.value.strip('"').encode('latin-1').decode('unicode_escape')
	return StringLiteral(string)
