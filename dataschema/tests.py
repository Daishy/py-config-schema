"""
Tests for the Schema.

Has to be run from a toplevel-skript, because of the python3.3 relative imports

"""


import unittest
import sys

from .exceptions import SchemaError, ValidationError
from .core import Schema
from .value_tokens import Int, String, Bytestring, Unicode, Bool, Object
from .container_tokens import Dict, And, Or
from .decorator_tokens import *



class DataSchemaTests(unittest.TestCase):

	def is_python_2(self):
		return sys.version_info.major == 2


	def assertValidates(self, definition, config, expected_result=None):
		
		try:
			schema = definition if isinstance(definition, Schema) else Schema(definition)

			config = schema.validate(config)
			if expected_result:
				self.assertEqual(config, expected_result)
			return config
		except ValidationError as e:
			self.fail(e.message)
		except SchemaError as e:
			self.fail(e.message)
	
	def assertFails(self, definition, config):
		schema = definition if isinstance(definition, Schema) else Schema(definition)
		with self.assertRaises(ValidationError):
			schema.validate(config)


	# --------------------------------------------------------------------------------
	#  Test basic functionality

	
	def test_validate_is_idempotent(self):
		cs = Schema({'a': int, 'b': Int(default=4)})

		c1 = cs.validate({'a':1, 'b': 1})
		c2 = cs.validate({'a':1, 'b': 1})
		self.assertIsNot(c1, c2)

	def test_validate_does_not_change_input(self):
		cs = Schema({"a": int, "b": bool, "c": Int(default=2)})
		input = {"a": 1, "b": True}
		output = cs.validate(input)
		self.assertEquals(input, {"a": 1, "b": True})
		self.assertEquals(output, {"a": 1, "b": True, "c": 2})
			
	def test_required_and_default(self):
		self.assertValidates(int, 1)
		self.assertFails(int, None)
		self.assertValidates(Int(required=False), None, None)
		self.assertValidates(Int(required=False, default=1), None, 1)
		self.assertValidates(Int(required=True, default=1), None, 1)
		self.assertValidates(Int(required=False, default=None), None, None)
		self.assertFails(Int(required=True, default=None), None)
		
		self.assertValidates(Int(default=None, required=False), None, None)
			




	# --------------------------------------------------------------------------------
	# Test value-Tokens


	def test_int(self):
		# Check basic values
		self.assertValidates(int, 1, 1)
		self.assertValidates(int, 0, 0)
		self.assertValidates(Int(), 1, 1)
		
		# check it fails without anything else
		self.assertFails(int, None)
		
		# check with required=false this is ok
		self.assertValidates(Int(required=False), None, None)
		
		# Check default is used
		self.assertValidates(Int(default=0), None, 0)
		
		# Check type-check is correct
		self.assertFails(int, "1")
		
		
	def test_unicode(self):
		if self.is_python_2():
			self.assertValidates(Unicode(), u"test", u"test")	 	
			self.assertValidates(unicode, u"test", u"test")

			self.assertFails(Unicode(), "nonunicode")
		else:
			self.assertValidates(Unicode(), "test", "test")
			self.assertValidates(unicode, u"test", u"test")
			self.assertFails(Bytestring(), b"test")
		
		# type-check
		self.assertFails(Unicode(), 1)



	def test_bytestring(self):
		if self.is_python_2():
			self.assertValidates(Bytestring(), "test", "test")
			self.assertFails(Bytestring(), u"test")
		else:
			self.assertValidates(Bytestring(), b"test", b"test")
			self.assertFails(Bytestring(), "test")


	def test_string(self):
		if self.is_python_2():
			self.assertValidates(String(), "a", "a")
			self.assertValidates(String(), u"a", u"a")
		else:
			self.assertValidates(String(), "a", "a")
			self.assertValidates(String(), u"a", u"a")
			self.assertFails(String(), b"a")
		
		
	def test_bool(self):
		self.assertValidates(bool, True)
		self.assertValidates(bool, False)
		self.assertValidates(Bool(), True)
		
		#type checks
		self.assertFails(bool, "true")
		self.assertFails(bool, 1)
		
		
	def test_object(self):
		self.assertValidates(object, True, True)
		self.assertValidates(object, 1, 1)
		self.assertValidates(object, "t", "t")
		self.assertValidates(Object(default=None, required=False), None, None)
		
		
		self.assertFails(object, None)


	# --------------------------------------------------------------------------------
	#   Test direct values
	def test_direct_values(self):
		self.assertValidates({'a': 1}, {'a': 1})

		self.assertValidates({'a': "test"}, {"a": "test"})
		self.assertValidates(True, True)
	


	# --------------------------------------------------------------------------------
	#  Test Container-Tokens

		
	def test_dicts(self):
		self.assertValidates({"a": int}, {"a": 1})
		
		self.assertValidates({"a": Int(required=False)}, {}, {"a": None})

	def test_dicts_type_checked(self):
		# Check we cant pass a non-dict to a dict and get the wrong result 
		self.assertFails({'a': int}, 1)
		
		
	def test_dicts_skip_unknown_keys(self):
		self.assertFails(
			{"a": int},
			{"a":1, "b":2})
		self.assertValidates(
			{"a": int, Dict.skip_unknown_keys: True},
			{"a": 1, "b": 2},
			{"a": 1})
			
			
	def test_dicts_required(self):
		self.assertValidates(
			{"a": {"a1":int}, "b":{"b1":int, Dict.required: False}},
			{"a": {"a1": 1}},
			{"a": {"a1": 1}, "b": None})
		self.assertFails(
			{"a": {"a1":int}, "b":{"b1":int, Dict.required: True}},
			{"a": {"a1": 1}})            
		self.assertFails(
			{"a": {"a1":int}, "b":{"b1":int}},
			{"a": {"a1": 1}, "b":{}})
			
			
	def test_dicts_default(self):
		self.assertValidates(
			{"a": int},
			{"a": 1},
			{"a": 1})
		
		default = {"a": 1}
		self.assertValidates(
			{"a": int, Dict.default: default},
			None,
			{"a": 1})
			
		self.assertValidates(
			{Dict.default: default},
			None,
			{'a': 1})
		
	
	def test_dicts_optional_keys(self):
		self.assertValidates(
			{'a': Bool(required=False)},
			{},
			{'a': None})
		self.assertValidates(
			{'a': Bool(default=False)},
			{},
			{'a': False})
		self.assertValidates(
			{'a': Bool(default=None, required=False)},
			{},
			{'a': None})

	def test_basic_And(self):
		self.assertValidates(
			And(int, object),
			1,
			1)

		self.assertValidates(
			And(Int(required=False), Bool(required=False)),
			None,
			None)

		self.assertFails(And(int, bool), 1)
		self.assertFails(And(int, String()), "test")
		self.assertFails(And(Int(required=False), bool), None)
		self.assertValidates(
			And(Int(required=False), bool),
			True,
			True)
		self.assertFails(And(Int(required=False), bool), 1)


	def test_basic_or(self):
		pass
		#TODO



	# --------------------------------------------------------------------------------
	# Test Dict with type-keys

	def test_dict_typekeys(self):
		self.assertValidates(
			{str: int},
			{"a": 1, "b": 2},
			{"a": 1, "b": 2})


	def test_dict_typekeys_hirarchie(self):
		self.assertValidates(
			{int: bool, bool: int},
			{True: 1},
			{True: 1})

		self.assertFails(
			{int: bool, bool: str},
			{True: True})

		self.assertValidates(
			{int: bool, object: object},
			{1: True, 2: False, "str": 1},
			{1: True, 2: False, "str": 1})

		self.assertFails(
			{int: int, object: String()},
			{1: "test"})

	def test_dict_typekeys_and_valuekeys_coexist(self):
		self.assertValidates(
			{"a": int, int: bool},
			{"a": 1, 1: True, 2: False},
			{"a": 1, 1: True, 2: False})

		self.assertFails(
			{"a": int, str: str},
			{"a": "a"})

	def test_class_keys(self):
		class A(object): pass
		a = A()
		self.assertValidates(
			{A: int},
			{a: 1},
			{a: 1})

	def test_value_over_type(self):
		self.assertValidates(
			{1: int, int: String()},
			{1: 1, 2: u"a"},
			{1: 1, 2: u"a"})

		self.assertFails(
			{1: int, int: String()},
			{1: "a", 2: u"a"})

	def test_typekeys_with_dict_value(self):
		self.assertValidates(
			{str: {"a": int}},
			{"1": {"a": 1}, "2": {"a": 2}},
			{"1": {"a": 1}, "2": {"a": 2}})

		self.assertFails(
			{str: {"a": int}},
			{"1": {}}
		)
		self.assertFails(
			{str: {"a": int}},
			{"1": None}
		)


	# --------------------------------------------------------------------------------
	# Test Msg-Parameter

	def test_message_parameter(self):
		try:
			Schema(Int(msg="Test")).validate("no-int")
			self.fail(u"This should have raised a ValidationError")
		except ValidationError as e:
			self.assertEqual(e.message, "Test")

		try:
			Schema(Int(msg=None)).validate("no-int")
			self.fail(u"This should have raised a ValidationError")
		except ValidationError as e:
			self.assertEqual(e.message, "Schema->Int expected <type 'int'> but got <type 'str'> (Value: no-int)")


	# --------------------------------------------------------------------------------
	# naming-tests

	def test_simple_naming(self):
		s = Schema(int)
		self.assertEqual(s.compiled.path, "Schema->Int")

		s = Schema(And(int, bool))
		self.assertEqual(s.compiled.path, "Schema->And->")
		self.assertEqual(s.compiled.compiled[0].path, "Schema->And->Int")
		self.assertEqual(s.compiled.compiled[1].path, "Schema->And->Bool")

		s = Schema({"a": int, "b": bool})
		self.assertEqual(s.compiled.path, "Schema->Dict")
		self.assertEqual(s.compiled.compiled_valuekeys['a'].path, "Schema->Dict:a->Int")
 
 	def test_repr(self):
 		s = Schema({"a": int, "b": bool})
 		as_string = repr(s)
 		self.assertNotEqual(s, None)



	# --------------------------------------------------------------------------------
	# 
 
	def test_complex_configs(self):
		""" Test some more complex Configs """
		config = {
			"name": String(),
			"version": int,
			"debug": Bool(default=False),
			"sub": {
				"sub1": String(required=False)
			}
		}
		
		self.assertValidates(config, {"name": u"a", "version": 1, "debug": True, "sub":{"sub1": u"test"}})
		self.assertValidates(config, {"name": u"a", "version": 1, "sub": {"sub1": u"Test"}})
		self.assertValidates(config, {"name": u"a", "version": 2, "sub": {}})
		
		
	def test_nested_schema(self):
		
		cs_sub = Schema(int)
		cs_sub2 = Schema({'b': bool})
		cs = Schema({
			'a': cs_sub,
			'b': cs_sub2,
		})
		
		self.assertValidates(cs,
				{'a': 1, 'b':{'b':True}},
				{'a': 1, 'b':{'b': True}})


	# --------------------------------------------------------------------------------
	#  Test decorators


	def test_max_decorator(self):
		cs = Schema(And(int, Max(10)))
		self.assertValidates(cs, 1, 1)
		self.assertFails(cs, 11)

		

	# --------------------------------------------------------------------------------
	# Test adding one schema to another and combine them
 		
		
	def test_schema_addition(self):
	 	# Cant add to simple values
	 	cs_a = Schema(int)
	 	cs_b = Schema(int)
	 	with self.assertRaises(SchemaError):
	 		cs = cs_a + cs_b
			
	 	# Cant add dict and simple value
	 	cs_a = Schema({'a': int})
	 	cs_b = Schema(int)
	 	with self.assertRaises(SchemaError):
	 		cs = cs_a + cs_b
			
	 	# Can add two dicts
	 	cs_a = Schema({'a': int})
	 	cs_b = Schema({'b': bool})
	 	cs = cs_a + cs_b
	 	self.assertEqual(cs.validate({"a": 1, "b": True}), {"a": 1, "b": True})
		
	 	# Can only add with distinctiv keys
	 	cs_a = Schema({'a': int})
	 	cs_b = Schema({'a': bool})
	 	with self.assertRaises(SchemaError):
	 		cs = cs_a + cs_b
			
		
	def test_schema_addition_required(self):
	 	# required is used of the stricter one
	 	cs_a = Schema({'a': int, Dict.required: True})
	 	cs_b = Schema({'b': int, Dict.required: False})
	 	cs = cs_a + cs_b
	 	self.assertFails(cs, None)
		
	 	cs_a = Schema({'a': int, Dict.required: False})
	 	cs_b = Schema({'b': int, Dict.required: True})
	 	cs = cs_a + cs_b
	 	self.assertFails(cs, None)
		
	 	cs_a = Schema({'a': int, Dict.required: False})
	 	cs_b = Schema({'b': int, Dict.required: False})
	 	cs = cs_a + cs_b
	 	self.assertValidates(cs, None)
	
	
	def test_schema_addition_skip_unknown_keys(self):
	 	# skip_unknown_keys is used from the stricter one
	 	cs_a = Schema({'a': int, Dict.skip_unknown_keys: True})
	 	cs_b = Schema({'b': int, Dict.skip_unknown_keys: False})
	 	cs = cs_a + cs_b
	 	self.assertEquals(cs.compiled.skip_unknown_keys, False)
	 	self.assertFails(cs, {'a':1, 'b': 2, 'c': 3})
		
	 	cs_a = Schema({'a': int, Dict.skip_unknown_keys: False})
	 	cs_b = Schema({'b': int, Dict.skip_unknown_keys: True})
	 	cs = cs_a + cs_b
 	 	self.assertEquals(cs.compiled.skip_unknown_keys, False)
	 	self.assertFails(cs, {'a':1, 'b': 2, 'c': 3})
		
	 	cs_a = Schema({'a': int, Dict.skip_unknown_keys: True})
	 	cs_b = Schema({'b': int, Dict.skip_unknown_keys: True})
	 	cs = cs_a + cs_b
	 	self.assertEquals(cs.compiled.skip_unknown_keys, True)
	 	self.assertValidates(cs, {'a':1, 'b': 2, 'c': 3})
		
	
	def test_schema_addition_default(self):
	 	#cs_a = Schema({'a': int, Dict.default: {'a': 1}})
	 	#cs_b = Schema({'b': int, Dict.default: {'b': 2}})
	 	#cs = cs_a + cs_b
	 	#self.assertValidates(cs, None, {'a': 1, 'b': 2})
	 	pass # TODO

	def test_schema_addition_typekeys(self):
	 	cs_a = Schema({str: object})
	 	cs_b = Schema({int: bool})
	 	cs = cs_a + cs_b
	 	self.assertFails(cs_a, {"string": True, 1: False})
	 	self.assertFails(cs_b, {"string": True, 1: False})
	 	self.assertValidates(cs, {"string": True, 1: False})


	 	# Two of the same typekeys with conflicting infos will raise an schemaerror
	 	with self.assertRaises(SchemaError):
	 		cs_a = Schema({str: object})
	 		cs_b = Schema({str: bool})
	 		cs = cs_a + cs_b

	 	# But two with the same will go through
	 	cs_a = Schema({str: bool})
	 	cs_b = Schema({str: bool})
	 	cs = cs_a + cs_b
		
		
	def test_schema_addition_with_and_tokens(self):
		cs_a = Schema(And(int, Min(0)))
		cs_b = Schema(And(int, Max(10)))
		cs = cs_a + cs_b
		self.assertValidates(cs_a, 20, 20)
		self.assertValidates(cs_b, -20, -20)
		self.assertFails(cs, 20)
		self.assertFails(cs, -20)

	def test_schema_addition_override_with_direct_values(self):
		cs_a = Schema({'a': int})
		cs_b = Schema({'a': 1})
		
		
def run_tests():
	""" Method to run the tests from a toplevel skript, so relative imports work """
	suite = unittest.TestLoader().loadTestsFromTestCase(DataSchemaTests)
	runner=unittest.TextTestRunner()
	runner.run(suite)
	