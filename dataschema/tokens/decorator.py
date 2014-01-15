"""
This file contains a list of tokens, that can be used to check 
a value for more specific things or convert them 
"""

from dataschema.base import Token
from dataschema.exceptions import ValidationError, SchemaError


__all__ = ["Call", "Check", "Range", "Min", "Max", "NotEmpty", "Regex", "IsPath"]



class DecoratorToken(Token):
	"""
	The basetoken used to validate additional stuff, like Range or Regex


	DecoratorTokens dont have a required or default-keyword, as those should be provided
	to the actual ValueTokens determining the type. But Decorator-Tokens can have a description
	and an error-message, which will be passed on.
	"""

	def __init__(self, msg=None, desc=None):
		"""
		:param msg: A userdefined error message if a ValidationError occurs within the Decorator
		:param desc: The description of the DecoratorToken. Defaults to None
		"""
		super(DecoratorToken, self).__init__(msg=msg, desc=desc)
		self.set_path(None)
	
	def set_path(self, parent_path):
		super(DecoratorToken, self).set_path(parent_path)

	def as_json(self, **kwargs):
		super(DecoratorToken, self).as_json(**kwargs)

	def __repr__(self):
		return u"<DecoratorToken {}>".format(self.path)

	



# ============================================================================================================
# ============================================================================================================
# == Now the actuall implementiations of the DecoratorTokens


class Call(DecoratorToken):
	""" Call takes a callable and calls it with the 
	value specified in validate. The return-value of the 
	call is instead returned
	"""

	def __init__(self, func, msg=None, desc=None):
		super(Call, self).__init__(msg=msg, desc=desc)
		self.func = func

	def _validate(self, values, default=None, has_default=False):
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

	def _validate(self, values, default=None, has_default=False):
		check = super(Check, self)._validate(values)
		if not check:
			raise ValidationError(self.msg or u"Check {} returned False!".format(self.path))
		return values


class IsPath(Check):
	""" Check if the string given to the validate-function is an actuall system-path """
	def __init__(self, msg=None, desc=None):
		import os
		super(IsPath, self).__init__(os.path.exists, msg=msg, desc=desc)

	def _validate(self, values, default=None, has_default=False):
		try:
			return super(IsPath, self)._validate(values)
		except ValidationError:
			raise ValidationError(self.msg or u"IsPath returned false for path `{}`".format(values))


class Range(DecoratorToken):
	"""
	Range checks a value is not less than min and not greater than max.
	"""
	def __init__(self, min=None, max=None, msg=None, desc=None):
		super(Range, self).__init__(msg=msg, desc=desc)
		self.min = min
		self.max = max

	def _validate(self, value):
		if value != None:
			if self.min != None and value < self.min:
				raise ValidationError(self.msg or u"Range {}: Value {} < Min {}".format(self.path, value, self.min))
			if self.max != None and value > self.max:
				raise ValidationError(self.msg or u"Range {}: Value {} > Max {}".format(self.path, value, self.max))
		return value


class Min(Range):
	""" Check a value is more than min """
	def __init__(self, min, **kwargs):
		super(Min, self).__init__(min=min, **kwargs)

class Max(Range):
	""" Check a value is less than max"""
	def __init__(self, max, **kwargs):
		super(Max, self).__init__(max=max, **kwargs)



class Regex(DecoratorToken):
	def __init__(self, regex, flags=None, **kwargs):
		import re
		super(Regex, self).__init__(**kwargs)
		self.regex = re.compile(regex, flags)

	def _validate(self, value):
		if not self.regex.match(value):
			raise ValidationError(self.msg or u"Regex {}: Value {} did not match Regex {}".format(self.path, value, self.regex))
		return value


class NotEmpty(DecoratorToken):
	def _validate(self, value):
		if len(value) == 0:
			raise ValidationError(self.msg or u"{} is empty!")
		return value