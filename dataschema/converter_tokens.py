"""
This file contains a set of tokens, that convert strings
to another type. While converting, this will also check 
if the type is actually correct
"""

from .core import DecoratorToken
from .exceptions import ValidationError, SchemaError

from .value_tokens import String


__all__ = ['asDecimal']


class asDecimal(String):
	
	""" Convert a string to decimal """
	def __init__(self, *args, **kwargs):
		super(asDecimal, self).__init__(*args, **kwargs)

	def validate(self, value):
		import decimal
		value = super(asDecimal, self).validate(value)

		try:
			return decimal.Decimal(value)
		except decimal.InvalidOperation:
			raise ValidationError(self.msg or u"{} is no decimal! (Path: {})".format(value, self.path))

