"""
This file contains a list of tokens, that can be used to check 
a value for more specific things or convert them 
"""

from .core import DecoratorToken
from .exceptions import ValidationError, SchemaError


__all__ = ["Call", "Check"]


class Call(DecoratorToken):
	""" Call takes a callable and calls it with the 
	value specified in validate. The return-value of the 
	call is instead returned
	"""

	def __init__(self, func):
		self.func = func

	def validate(self, values):
		func = self.func
		return func(values)



class Check(Call):
	""" Takes a function and calls the function on validate.
	If the function returns true, the validation goes through,if false
	a validationerror is raised
	"""

	def validate(self, values):
		values = super(Check, self).validate(values)
		if not values:
			raise validationError(u"Check {} returned False!".format(self.name))
		return values


