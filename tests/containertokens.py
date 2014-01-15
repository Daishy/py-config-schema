from .testcase import TestCase
import dataschema as ds


class AndTokenTests(TestCase):


	def test_validating(self):

		cs = ds.And(int, ds.Max(10), ds.Min(8))
		self.assertValidates(cs, 9)
		self.assertFails(cs, "1")
		self.assertFails(cs, "a")
		self.assertFails(cs, 7)
		self.assertFails(cs, 11)

	def test_combining_and_tokens(self):
		cs_1 = ds.And(int, ds.Max(10))
		cs_2 = ds.And(int, ds.Min(8))
		cs = cs_1 + cs_2

		self.assertValidates(cs_1, 7, 7)
		self.assertFails(cs, 7)

		self.assertValidates(cs_2, 11, 11)
		self.assertFails(cs, 11)

	def test_combining_impossible_combination(self):
		cs_1 = ds.And(float) # No int here, because isinstance(True, int)==True
		cs_2 = ds.And(bool)
		cs = cs_1+cs_2

		self.assertValidates(cs_1, 1.1, 1.1)
		self.assertFails(cs_1, True)

		self.assertValidates(cs_2, True, True)
		self.assertFails(cs_2, 1.1)

		self.assertFails(cs, 1.1)
		self.assertFails(cs, True)

	def test_and_passes_on_desc(self):
		cs = ds.And(int, desc="Some Desc")
		json = cs.as_json()
		self.assertEqual(json['desc'], "Some Desc")


class OrTokenTests(TestCase):

	def test_validating(self):
		cs_1 = ds.Int()
		cs_2 = ds.String()
		cs = ds.Or(cs_1, cs_2)

		self.assertFails(cs_1, "a")
		self.assertFails(cs_2, 1)
		self.assertValidates(cs, "a", "a")
		self.assertValidates(cs, 1, 1)

	def test_combining_or_tokens(self):
		cs_1 = ds.Or(ds.Int())
		cs_2 = ds.Or(ds.String())
		cs = cs_1 + cs_2

		self.assertFails(cs_1, "a")
		self.assertFails(cs_2, 1)
		self.assertValidates(cs, "a", "a")
		self.assertValidates(cs, 1, 1)

	def test_creating_empty_or(self):
		cs_1 = ds.Or()
		self.assertFails(cs_1, "a")
		self.assertFails(cs_1, 1)
		self.assertFails(cs_1, None)

	def test_or_failing(self):
		cs = ds.Or(int, ds.String())
		self.assertFails(cs, None)

	def test_or_error_msg(self):
		cs = ds.Or(int, ds.String(), msg="Failing test")
		self.assertFails(cs, None, "Failing test")



class ListTokenTests(TestCase):

	def test_list_with_ExplicitValue(self):
		# Creating List with None as definition produces a ds.List
		# with an ExplicitValue inside it.
		cs_1 = ds.List(None)
		self.assertValidates(cs_1, [None, None], [None, None])
		self.assertFails(cs_1, None)

	def test_creating_list_token(self):
		with self.assertRaises(ds.SchemaError):
			ds.List([int, bool])

		with self.assertRaises(ds.SchemaError):
			ds.List([])

		ds.List(int) # Explicit mode
		ds.List([int]) # Implicit mode


	def test_list_with_notempty_decorator(self):
		cs = ds.And(ds.List(int), ds.NotEmpty())
		self.assertValidates(cs, [1, 2], [1, 2])
		self.assertFails(cs, None)
		self.assertFails(cs, [])

	def test_list_with_defaults(self):
		cs = ds.List(ds.Int(default=10))
		self.assertValidates(cs, [1, None, None, 2], [1, 10, 10, 2])


class DictTokenTests(TestCase):
		
	def test_dicts(self):
		self.assertValidates({"a": int}, {"a": 1}, {"a": 1})
	
 		self.assertValidates({"a": ds.Int(required=False)}, {}, {"a": None})

 	def test_dicts_type_checked(self):
 		# Check we cant pass a non-dict to a dict and get the wrong result 
 		self.assertFails({'a': int}, 1)
		
		
 	def test_dicts_skip_unknown_keys(self):
 		self.assertFails(
 			{"a": int},
 			{"a":1, "b":2})
 		self.assertValidates(
 			{"a": int, ds.Dict.skip_unknown_keys: True},
 			{"a": 1, "b": 2},
 			{"a": 1})
		
		
 	def test_dicts_required(self):
 		self.assertValidates(
 			{"a": {"a1":int}, "b":{"b1":int, ds.Dict.required: False}},
 			{"a": {"a1": 1}},
 			{"a": {"a1": 1}, "b": None})
 		self.assertFails(
 			{"a": {"a1":int}, "b":{"b1":int, ds.Dict.required: True}},
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
 			{"a": int, ds.Dict.default: default},
 			None,
 			{"a": 1})
			
 		self.assertValidates(
			{ds.Dict.default: default},
 			None,
 			{'a': 1})
		
	
 	def test_dicts_optional_keys(self):
 		self.assertValidates(
 			{'a': ds.Bool(required=False)},
 			{},
 			{'a': None})
 		self.assertValidates(
 			{'a': ds.Bool(default=False)},
 			{},
 			{'a': False})
 		self.assertValidates(
 			{'a': ds.Bool(default=None, required=False)},
 			{},
 			{'a': None})


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
 			{int: int, object: ds.String()},
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
 			{1: int, int: ds.String()},
 			{1: 1, 2: u"a"},
 			{1: 1, 2: u"a"})

 		self.assertFails(
 			{1: int, int: ds.String()},
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

 	def test_dict_msg_on_validationerror(self):
 		cs = ds.Dict({"a": int, ds.Dict.msg: "Test"})
 		self.assertFails(cs, None, "Test")




	# --------------------------------------------------------------------------------
	# Test adding one dict to another. This gets a seperate section because it
	# may be a bit more complex than with the other tokens
		
	
 	def test_schema_addition(self):
 	 		
 	 	# Cant add dict and simple value
 	 	cs_a = ds.Dict({'a': int})
 	 	cs_b = ds.Int()
 	 	with self.assertRaises(ds.SchemaError):
 	 		cs = cs_a + cs_b
			
 	 	# Can add two dicts
 	 	cs_a = ds.Dict({'a': int})
 	 	cs_b = ds.Dict({'b': bool})
 	 	cs = cs_a + cs_b
 	 	self.assertEqual(cs.validate({"a": 1, "b": True}), {"a": 1, "b": True})
		
 	 	# Can only add with distinctiv keys
 	 	cs_a = ds.Dict({'a': int})
 	 	cs_b = ds.Dict({'a': bool})
 	 	with self.assertRaises(ds.SchemaError):
 	 		cs = cs_a + cs_b
			
		
# 	def test_schema_addition_required(self):
# 	 	# required is used of the stricter one
# 	 	cs_a = Schema({'a': int, Dict.required: True})
# 	 	cs_b = Schema({'b': int, Dict.required: False})
# 	 	cs = cs_a + cs_b
# 	 	self.assertFails(cs, None)
		
# 	 	cs_a = Schema({'a': int, Dict.required: False})
# 	 	cs_b = Schema({'b': int, Dict.required: True})
# 	 	cs = cs_a + cs_b
# 	 	self.assertFails(cs, None)
		
# 	 	cs_a = Schema({'a': int, Dict.required: False})
# 	 	cs_b = Schema({'b': int, Dict.required: False})
# 	 	cs = cs_a + cs_b
# 	 	self.assertValidates(cs, None)
	
	
# 	def test_schema_addition_skip_unknown_keys(self):
# 	 	# skip_unknown_keys is used from the stricter one
# 	 	cs_a = Schema({'a': int, Dict.skip_unknown_keys: True})
# 	 	cs_b = Schema({'b': int, Dict.skip_unknown_keys: False})
# 	 	cs = cs_a + cs_b
# 	 	self.assertEquals(cs.compiled.skip_unknown_keys, False)
# 	 	self.assertFails(cs, {'a':1, 'b': 2, 'c': 3})
		
# 	 	cs_a = Schema({'a': int, Dict.skip_unknown_keys: False})
# 	 	cs_b = Schema({'b': int, Dict.skip_unknown_keys: True})
# 	 	cs = cs_a + cs_b
#  	 	self.assertEquals(cs.compiled.skip_unknown_keys, False)
# 	 	self.assertFails(cs, {'a':1, 'b': 2, 'c': 3})
		
# 	 	cs_a = Schema({'a': int, Dict.skip_unknown_keys: True})
# 	 	cs_b = Schema({'b': int, Dict.skip_unknown_keys: True})
# 	 	cs = cs_a + cs_b
# 	 	self.assertEquals(cs.compiled.skip_unknown_keys, True)
# 	 	self.assertValidates(cs, {'a':1, 'b': 2, 'c': 3})
		
	
# 	def test_schema_addition_default(self):
# 	 	#cs_a = Schema({'a': int, Dict.default: {'a': 1}})
# 	 	#cs_b = Schema({'b': int, Dict.default: {'b': 2}})
# 	 	#cs = cs_a + cs_b
# 	 	#self.assertValidates(cs, None, {'a': 1, 'b': 2})
# 	 	pass # TODO

# 	def test_schema_addition_typekeys(self):
# 	 	cs_a = Schema({str: object})
# 	 	cs_b = Schema({int: bool})
# 	 	cs = cs_a + cs_b
# 	 	self.assertFails(cs_a, {"string": True, 1: False})
# 	 	self.assertFails(cs_b, {"string": True, 1: False})
# 	 	self.assertValidates(cs, {"string": True, 1: False})


# 	 	# Two of the same typekeys with conflicting infos will raise an schemaerror
# 	 	with self.assertRaises(SchemaError):
# 	 		cs_a = Schema({str: object})
# 	 		cs_b = Schema({str: bool})
# 	 		cs = cs_a + cs_b

# 	 	# But two with the same will go through
# 	 	cs_a = Schema({str: bool})
# 	 	cs_b = Schema({str: bool})
# 	 	cs = cs_a + cs_b
		
		
# 	def test_schema_addition_with_and_tokens(self):
# 		cs_a = Schema(And(int, Min(0)))
# 		cs_b = Schema(And(int, Max(10)))
# 		cs = cs_a + cs_b
# 		self.assertValidates(cs_a, 20, 20)
# 		self.assertValidates(cs_b, -20, -20)
# 		self.assertFails(cs, 20)
# 		self.assertFails(cs, -20)

# 	def test_schema_addition_override_with_direct_values(self):
# 		cs_a = Schema({'a': int})
# 		cs_b = Schema({'a': 1})