"""
This file contains a set of tokens, that convert strings
to another type. While converting, this will also check 
if the type is actually correct
"""

from dataschema.base import Token
from dataschema.tokens.values import String
from dataschema.exceptions import ValidationError


__all__ = ['asDecimal']


class asDecimal(String):
	
	""" Convert a string to decimal """
	def __init__(self, *args, **kwargs):
		super(asDecimal, self).__init__(*args, **kwargs)

	def _validate(self, value, default=None, has_default=False):
		import decimal
		value = super(asDecimal, self).validate(value)

		try:
			return decimal.Decimal(value)
		except decimal.InvalidOperation:
			raise ValidationError(self.msg or u"{} is no decimal! (Path: {})".format(value, self.path))

