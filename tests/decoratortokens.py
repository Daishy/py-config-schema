from .testcase import TestCase
import dataschema as ds

class DataSchemaDecoratorTokenTests(TestCase):
	"""
	Testing the decorator tokens
	"""

	def test_range_decorator(self):
		cs = ds.Range(min=1, max=3)
		self.assertValidates(cs, 1, 1)
		self.assertValidates(cs, 3, 3)
		self.assertFails(cs, 0)
		self.assertFails(cs, 4)
	
	def test_max_decorator(self):
		cs = ds.And(int, ds.Max(10))
		self.assertValidates(cs, 1, 1)
		self.assertValidates(cs, 10, 10)
		self.assertFails(cs, 11)

	def test_min_decorator(self):
		cs = ds.And(int, ds.Min(10))
		self.assertValidates(cs, 11, 11)
		self.assertValidates(cs, 10, 10)
		self.assertFails(cs, 9)



	def test_is_path(self):
		cs = ds.IsPath()
		self.assertValidates(cs, "/tmp", "/tmp")
		self.assertFails(cs, "/thechanceishighthisdoesnotexist")
		self.assertFails(cs, None)
		self.assertFails(cs, 1)

	def test_not_empty(self):
		cs = ds.NotEmpty()
		self.assertValidates(cs, [1], [1])
		self.assertValidates(cs, "abc", "abc")
		
		self.assertFails(cs, [])
		self.assertFails(cs, "")
		self.assertFails(cs, {})

		# This should raise an exception, because NotEmpty should
		# not have to check, if the len-operator is supported on the input
		with self.assertRaises(TypeError):
			self.assertFails(cs, None)