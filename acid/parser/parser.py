#!/usr/bin/env python3.4
# coding: utf-8

"""
Declares the Parser class, which can transform a code string into an AST.

Contributors: myrma
"""

import functools
from collections import defaultdict

from acid.parser.ast import *
from acid.parser.lexer import TokenType, tokenize
from acid.exception import ParseError


# todo: refactor consume_stmt and consume_expr, register_stmt and register_expr

class Parser:
	"""
	Registers some consumers to parse the AST.
	"""

	consumers = defaultdict(list)

	def __init__(self, code, path=None):
		self.path = path
		self.code = code
		self.token_queue = list(tokenize(self.code))  # the tokenized string
		self.error = None

	@classmethod
	def from_file(cls, path):
		with open(path) as file:
			code = file.read()
			return cls(code, path)

	@classmethod
	def from_string(cls, code, path=None):
		"""
		Parses the given code, without needing to instantiate a Parser object.
		"""

		parser = cls(code, path)
		ast = parser.run()
		return ast

	@classmethod
	def register(cls, node_type, priority=1):
		"""
		Registers a given consumer function with a priority. `priority` is an
		integer defining the order in which expression types try to parse from
		the token queue. The closest this number if from 1, the highest will be
		its priority.

		`priority` must be greater than one (not strictly).
		"""

		def _decorator_wrapper(consumer):
			@functools.wraps(consumer)
			def _consumer_wrapper(self):
				# copies the token list
				tmp_queue = self.token_queue[:]

				try:
					node = consumer(self)
				except ParseError:
					# assign tmp_queue to reference token_queue
					self.token_queue[:] = tmp_queue

					raise
				except IndexError:
					# assign tmp_queue to reference token_queue
					self.token_queue[:] = tmp_queue

					# when the user tries to call token_queue.pop(0)
					raise ParseError(self.token_queue[0].pos, 'Unexpected EOF')
				else:
					return node

			# decrement because highest priority is 1, not 0
			_consumer_wrapper.priority = priority - 1
			cls.consumers[node_type].append(_consumer_wrapper)

		return _decorator_wrapper


	def consume(self, node_type):
		"""
		Tries to parse a node of type `node_type` from the token list.
		This does not affect the list if the function failed to parse.
		"""

		consumers = list(self.consumers[node_type])

		for sub_node_type in node_type.sub_types():
			consumers.extend(self.consumers[sub_node_type])

		consumers.sort(key=lambda cons: cons.priority)

		# tries every concrete nodes of type node_type
		for consumer in consumers:
			try:
				node = consumer(self)
			except ParseError as e:
				error = e
				continue
			else:
				return node
		else:
			# when every node has been tried, but none succeeded to parse
			raise error

	def expect(self, token_type):
		"""
		Tries to consume a single token from the token queue.
		Returns the token if the next token is of the given type, raises a
		ParseError otherwise.
		"""

		token = self.token_queue.pop(0)

		# if the next token is not of the expected type
		if token.type != token_type:
			msg = 'Expected {}, got {}'.format(token_type.name, token.type.name)
			raise ParseError(token.pos, msg)

		return token

	def run(self):
		"""
		Parses a given string into a Program object.
		"""

		program = self.consume(Program)
		return program
