"""
Tests for the Schema.

Has to be run from a toplevel-skript, because of the python3.3 relative imports

"""


import unittest
from .exceptions import SchemaError, ValidationError
from .core import Schema
from .value_tokens import Int, String, Bool,  Object
from .container_tokens import Dict, And, Or



class DataSchemaTests(unittest.TestCase):

	def assertValidates(self, definition, config, expected_result=None):
		
		try:
			cv = Schema(definition)
			config = cv.validate(config)
			if expected_result:
				self.assertEqual(config, expected_result)
			return config
		except ValidationError as e:
			self.fail(e.message)
		except SchemaError as e:
			self.fail(e.message)
	
	def assertFails(self, definition, config):
		cv = Schema(definition)
		with self.assertRaises(ValidationError):
			cv.validate(config)


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
		
		
	def test_string(self):
		# Check Basic values
		self.assertValidates(str, "test", "test")
		self.assertValidates(str, "unicode", "unicode")
		self.assertValidates(String(), "test", "test")
		
		# Check unicode does not work if it is available
		try:
			unicode
			basestring
			
			with self.assertRaises(SchemaError):
				Schema(unicode)
			with self.assertRaises(SchemaError):
				Schema(basestring)
		except NameError:
			pass
		
		# Empty values should validate
		self.assertValidates(str, "", "")
		self.assertValidates(String(required=False), None, "")
		
		# default
		self.assertValidates(String(default="test"), None, "test")
		self.assertValidates(String(required=False), None, None)
		
		# type-check
		self.assertFails(str, 1)
		
		
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
	#  Test Container-Tokens

		
	def test_dicts(self):
		self.assertValidates({"a": int}, {"a": 1})
		
		self.assertValidates({"a": Int(required=False)}, {}, {"a": None})

	def test_dicts_type_checked(self):
		# Check we cant pass a non-dict to a dict and get the wrong result 
		self.assertFails({'a': int}, 1)
		
		
	def test_dicts_fixed(self):
		self.assertFails(
			{"a": int},
			{"a":1, "b":2})
		self.assertValidates(
			{"a": int, Dict.fixed: False},
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
		self.assertFails(And(int, str), "test")
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




	# --------------------------------------------------------------------------------
	# 
 
	def test_complex_configs(self):
		""" Test some more complex Configs """
		config = {
			"name": str,
			"version": int,
			"debug": Bool(default=False),
			"sub": {
				"sub1": String(required=False)
			}
		}
		
		self.assertValidates(config, {"name": "a", "version": 1, "debug": True, "sub":{"sub1": "test"}})
		self.assertValidates(config, {"name": "a", "version": 1, "sub": {"sub1": "Test"}})
		self.assertValidates(config, {"name": "a", "version": 2, "sub": {}})
		
		
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
		
		
		
	# def test_schema_addition(self):
	# 	# Cant add to simple values
	# 	cs_a = Schema(int)
	# 	cs_b = Schema(int)
	# 	with self.assertRaises(SchemaError):
	# 		cs = cs_a + cs_b
			
	# 	# Cant add dict and simple value
	# 	cs_a = Schema({'a': int})
	# 	cs_b = Schema(int)
	# 	with self.assertRaises(SchemaError):
	# 		cs = cs_a + cs_b
			
	# 	# Can add two dicts
	# 	cs_a = Schema({'a': int})
	# 	cs_b = Schema({'b': bool})
	# 	cs = cs_a + cs_b
	# 	self.assertEqual(cs.validate({"a": 1, "b": True}), {"a": 1, "b": True})
		
	# 	# Can only add with distinctiv keys
	# 	cs_a = Schema({'a': int})
	# 	cs_b = Schema({'a': bool})
	# 	with self.assertRaises(SchemaError):
	# 		cs = cs_a + cs_b
			
		
	# def test_schema_addition_required(self):
	# 	# required is used of the stricter one
	# 	cs_a = Schema({'a': int, Dict.required: True})
	# 	cs_b = Schema({'b': int, Dict.required: False})
	# 	cs = cs_a + cs_b
	# 	self.assertFails(cs, None)
		
	# 	cs_a = Schema({'a': int, Dict.required: False})
	# 	cs_b = Schema({'b': int, Dict.required: True})
	# 	cs = cs_a + cs_b
	# 	self.assertFails(cs, None)
		
	# 	cs_a = Schema({'a': int, Dict.required: False})
	# 	cs_b = Schema({'b': int, Dict.required: False})
	# 	cs = cs_a + cs_b
	# 	self.assertValidates(cs, None)
		
	# def test_schema_addition_fixed(self):
	# 	# fixed is used from the stricter one
	# 	cs_a = Schema({'a': int, Dict.fixed: True})
	# 	cs_b = Schema({'b': int, Dict.fixed: False})
	# 	cs = cs_a + cs_b
	# 	self.assertFails(cs, {'a':1, 'b': 2, 'c': 3})
		
	# 	cs_a = Schema({'a': int, Dict.fixed: False})
	# 	cs_b = Schema({'b': int, Dict.fixed: True})
	# 	cs = cs_a + cs_b
	# 	self.assertFails(cs, {'a':1, 'b': 2, 'c': 3})
		
	# 	cs_a = Schema({'a': int, Dict.fixed: False})
	# 	cs_b = Schema({'b': int, Dict.fixed: False})
	# 	cs = cs_a + cs_b
	# 	self.assertValidates(cs, {'a':1, 'b': 2, 'c': 3})
		
	
	# def test_schema_addition_default(self):
	# 	cs_a = Schema({'a': int, Dict.default: {'a': 1}})
	# 	cs_b = Schema({'b': int, Dict.default: {'b': 2}})
	# 	cs = cs_a + cs_b
	# 	self.assertValidates(cs, None, {'a': 1, 'b': 2})
		
		
		
		
def run_tests():
	""" Method to run the tests from a toplevel skript, so relative imports work """
	suite = unittest.TestLoader().loadTestsFromTestCase(DataSchemaTests)
	runner=unittest.TextTestRunner()
	runner.run(suite)
	