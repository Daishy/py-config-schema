

import unittest
import sys
from dataschema import Token



class TestCase(unittest.TestCase):
	""" Basis testcase for py-data-schema defining some common
	assert- and helper-methods
	"""

	def is_python_2(self):
		return sys.version_info.major == 2


	def wrap_basic_type(self, definition):
		""" Wrap the basic type in a token to make testing easier.
		e.g. instead of self.assertValidates(ds.Int(), 1, 1)
		we can write self.assertValidates(int, 1, 1)
		"""
		token = Token.get_token(definition)
		token.set_path("testbase")
		return token
		

	def assertValidates(self, schema, data, expected_result=None):
		try:
			# Make sure we operate on a schema
			if not isinstance(schema, Token):
				schema = self.wrap_basic_type(schema)
				
			# Validate
			validated_data = schema.validate(data)

			# if that validated, check if thats what we need
			if expected_result:
				self.assertEqual(validated_data, expected_result)
			return validated_data

		except Token.ValidationError as e:
			self.fail(e.message)

	
	def assertFails(self, schema, data, expected_msg = None):
		"""
		This validates `schema` with `data` given and asserts that the
		validation raises an `ValidationError`. If `expected_msg` is given, 
		the exception-message must match it
		"""
		# Make sure we operate on a schema
		if not isinstance(schema, Token):
			schema = self.wrap_basic_type(schema)
	
		with self.assertRaises(schema.ValidationError) as e:
			schema.validate(data)

		if expected_msg:
			self.assertEqual(expected_msg, e.exception.message)
		