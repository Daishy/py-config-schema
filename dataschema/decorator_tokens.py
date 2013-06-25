"""
This file contains a list of tokens, that can be used to check 
a value for more specific things or convert them 
"""

from .core import DecoratorToken
from .exceptions import ValidationError, SchemaError


__all__ = ["Call", "Check", "Range", "Min", "Max", "NotEmpty", "Regex", "IsPath"]


class Call(DecoratorToken):
	""" Call takes a callable and calls it with the 
	value specified in validate. The return-value of the 
	call is instead returned
	"""

	def __init__(self, func, msg=None):
		super(Call, self).__init__(msg=msg)
		self.func = func

	def validate(self, values):
		try:
			func = self.func
			return func(values)
		except Exception as e:
			raise ValidationError(self.msg or u"Call {} raised an exception while calling {}: {}".format(self.path, self.func, e.message))



class Check(Call):
	""" Takes a function and calls the function on validate.
	If the function returns true, the validation goes through,if false
	a validationerror is raised
	"""

	def validate(self, values):
		check = super(Check, self).validate(values)
		if not check:
			raise validationError(self.msg or u"Check {} returned False!".format(self.path))
		return values


class IsPath(Check):
	""" Check if the string given to the validate-function is an actuall system-path """
	def __init__(self, msg=None):
		import os
		super(IsPath, self).__init__(os.path.exists, msg)


class Range(DecoratorToken):
	"""
	Range checks a value is not less than min and not greater than max.
	"""
	def __init__(self, min=None, max=None, msg=None):
		super(Range, self).__init__(msg=msg)
		self.min = min
		self.max = max

	def validate(self, value):
		if value != None:
			if self.min != None and value < self.min:
				raise ValidationError(self.msg or u"Range {}: Value {} < Min {}".format(self.path, value, self.min))
			if self.max != None and value > self.max:
				raise ValidationError(self.msg or u"Range {}: Value {} > Max {}".format(self.path, value, self.max))
		return value


class Min(Range):
	""" Check a value is more than min """
	def __init__(self, min):
		super(Min, self).__init__(min=min)

class Max(Range):
	""" Check a value is less than max"""
	def __init__(self, max):
		super(Max, self).__init__(max=max)



class Regex(DecoratorToken):
	def __init__(self, regex, flags=None):
		import re
		super(Regex, self).__init__()
		self.regex = re.compile(regex, flags)

	def validate(self, value):
		if not self.regex.match(value):
			raise ValidationError(self.msg or u"Regex {}: Value {} did not match Regex {}".format(self.path, value, self.regex))
		return value


class NotEmpty(DecoratorToken):
	def validate(self, value):
		if len(value) == 0:
			raise ValidationError(self.msg or u"{} is empty!")
		return value