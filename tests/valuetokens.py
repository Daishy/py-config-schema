from .testcase import TestCase
import dataschema as ds



class DataSchemaValueTokensTests(TestCase):
	"""
	Testing the value-tokens
	"""

	def test_required_and_default(self):
		self.assertValidates(int, 1, 1)
		self.assertFails(int, None)
		self.assertValidates(ds.Int(required=False), None, None)
		self.assertValidates(ds.Int(required=False, default=1), None, 1)
		self.assertValidates(ds.Int(required=True, default=1), None, 1)
		self.assertValidates(ds.Int(required=False, default=None), None, None)
		self.assertFails(ds.Int(required=True, default=None), None)
		
		self.assertValidates(ds.Int(default=None, required=False), None, None)

	def test_int(self):
		# Check basic values
		self.assertValidates(int, 1, 1)
		self.assertValidates(int, 0, 0)
		self.assertValidates(ds.Int(), 1, 1)
		
		# check it fails without anything else
		self.assertFails(int, None)
		
		# check with required=false this is ok
		self.assertValidates(ds.Int(required=False), None, None)
		
		# Check default is used
		self.assertValidates(ds.Int(default=0), None, 0)
		
		# Check type-check is correct
		self.assertFails(int, "1")


	def test_boolean_also_qualifies_as_int(self):
		# True and False (bool) is a subset of int, so passing
		# a bool to an int-validator also checks out
		self.assertValidates(int, True, True)
		self.assertValidates(int, False, False)
		
		
	def test_unicode(self):


		if self.is_python_2():
			self.assertValidates(ds.Unicode(), u"test", u"test")	 	
			self.assertValidates(unicode, u"test", u"test")

			self.assertFails(ds.Unicode(), "nonunicode")
		else:
			self.assertValidates(ds.Unicode(), "test", "test")
			self.assertValidates(unicode, u"test", u"test")
			self.assertFails(ds.Bytestring(), b"test")
		
		# type-check
		self.assertFails(ds.Unicode(), 1)



	def test_bytestring(self):
		if self.is_python_2():
			self.assertValidates(ds.Bytestring(), "test", "test")
			self.assertFails(ds.Bytestring(), u"test")
		else:
			self.assertValidates(ds.Bytestring(), b"test", b"test")
			self.assertFails(ds.Bytestring(), "test")


	def test_string(self):
		if self.is_python_2():
			self.assertValidates(ds.String(), "a", "a")
			self.assertValidates(ds.String(), u"a", u"a")
		else:
			self.assertValidates(ds.String(), "a", "a")
			self.assertValidates(ds.String(), u"a", u"a")
			self.assertFails(ds.String(), b"a")
		
		
	def test_bool(self):
		self.assertValidates(bool, True)
		self.assertValidates(bool, False)
		self.assertValidates(ds.Bool(), True)
		
		#type checks
		self.assertFails(bool, "true")
		self.assertFails(bool, 1)
		
		
	def test_object(self):
		self.assertValidates(object, True, True)
		self.assertValidates(object, 1, 1)
		self.assertValidates(object, "t", "t")
		self.assertValidates(ds.Object(default=None, required=False), None, None)
		
		
		self.assertFails(object, None)


	def test_explicitvalue(self):
		self.assertValidates({'a': 1}, {'a': 1})

		self.assertValidates({'a': "test"}, {"a": "test"})
		self.assertValidates(True, True)

