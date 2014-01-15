from .testcase import TestCase
import dataschema as ds

class DataSchemaBasicsTests(TestCase):
	"""
	Testing the basic functionality of the dataschema
	"""
	
	def test_validate_is_idempotent(self):
		cs = ds.Dict({
			'a': int,
			'b': ds.Int(default=4)
		})

		r1 = cs.validate({'a':1, 'b': 1})
		r2 = cs.validate({'a':1, 'b': 1})
		self.assertIsNot(r1, r2)


	def test_validate_does_not_change_input(self):
		cs = ds.Dict({
			"a": int,
			"b": bool,
			"c": ds.Int(default=2)
		})
		
		data = {"a": 1, "b": True}
		output = cs.validate(data)
		self.assertEquals(data, {"a": 1, "b": True})
		self.assertEquals(output, {"a": 1, "b": True, "c": 2})
			

	def test_as_json_is_correct(self):
		cs = ds.Dict({
			"a": {
				"aa": ds.Int()
			}
		})

		json = cs.as_json()

		self.assertIn('a', json)
		self.assertIn('aa', json['a'])
		self.assertEqual('Dict', json['class'])


	def test_path_info_is_correct(self):
		cs = ds.Dict({
			"a": {
				"aa": int
			}
		})
		json = cs.as_json()
		self.assertEqual(json['path'], "Dict")
		self.assertEqual(json['a']['path'], "Dict:a -> Dict")
		self.assertEqual(json['a']['aa']['path'], "Dict:a -> Dict:aa -> Int")


	def test_message_parameter(self):
		self.assertFails(ds.Int(msg="Test"), "no-int", "Test")
		self.assertFails(ds.Int(), "no-int", "Int expected <type 'int'> but got <type 'str'> (Value: no-int)")

	def test_nested_schema(self):
		
		cs_sub = ds.Int()
		cs_sub2 = ds.Dict({'b': bool})
		cs = ds.Dict({
			'a': cs_sub,
			'b': cs_sub2,
		})
		
		self.assertValidates(cs,
				{'a': 1, 'b':{'b':True}},
				{'a': 1, 'b':{'b': True}})