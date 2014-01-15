from .testcase import TestCase
import dataschema as ds

class DataSchemaConvertTokenTests(TestCase):
	

	def test_as_decimal_converter(self):
		from decimal import Decimal 

		cs = ds.asDecimal()
		self.assertValidates(cs, "1.5", Decimal('1.5'))
		self.assertValidates(cs, "1", Decimal('1'))
		self.assertValidates(cs, "-1", Decimal('-1'))
		self.assertValidates(cs, "-1.1", Decimal('-1.1'))
		self.assertFails(cs, "a")
		self.assertFails(cs, "a1")
		self.assertFails(cs, "1a")