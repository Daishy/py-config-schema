"""
This file contains all simple value tokens (like Int, String, Bool)
"""

from dataschema.base import Token
from dataschema.exceptions import ValidationError

import sys # Needed to check for Python 2 or 3 while handling str/unicode/strings



__all__ = ["Int", "String", "Unicode", "Bytestring", "Bool", "Object", "Decimal", "Float", 'ExplicitValue']




class ValueToken(Token):
	"""
	The baseclass for all token that represent a single value. Suplies some of the basic-features for all 
	tokens.
	Possible flags are:
	:param value_type: The expected type of the valuetoken. The value will be checked with isinstance against this
	:param required: If true, the Token must be given in the config (May still be None) (default: True)
	:param desc: A string giving the Description of the Setting (Default: None)
	:param default: A defaultvalue for the Token (Default: None
	"""
	
	def __init__(self, value_type, required=True, desc=None, default=None, msg=None):
		"""
		Init a new ValueToken
		:param value_type: The type to validate against
		:param required: True if the token must be given and valid (default: True)
		:param desc: A Short description of the token
		:param default: The defaultvalue to be used for the token, if value is not found. (default: None)        
		:param msg: Errormessage to use if a ValidationError occurs. If none, a default one will be generated
		"""
		super(ValueToken, self).__init__(msg=msg, desc=desc)
		self.value_type = value_type
		self.required = required
		self.default = default

		self.set_path(None)

	def set_path(self, parent_path):
		super(ValueToken, self).set_path(parent_path)
		
		
	def _validate(self, value, default=None, has_default=False):
		"""
		Validate the value. The base-methods simply checks if the value is None and if so replace it with the default. Afterwards this will
		check if this value is required. If it is and the value is `None` a `ValidationError` is raised. Finally this will check the type of the value,
		which must match `self.value_type`
	
		:param value: The value to check
		
		:return: Returns value or default, if value is None
		"""
		if value == None:
			value = self.default
		if self.required and value == None:
			raise ValidationError(self.msg or u"{} is required, but validated value was None!".format(self.path))
		if value != None and not isinstance(value, self.value_type):
			raise ValidationError(self.msg or u"{} expected {} but got {} (Value: {})".format(self.path, self.value_type, type(value), value))
		return value

	def __add__(self, other):
		"""
		Adding to ValueTokens together is a bit complicated, because of the values. The addition is as follows:
		default: If both are None, keep None. If one None, the other given use given. If both not None, raise Error
		required: self.required || other.required
		value_type: Must be the same
		desc = Add first and Second
		"""
		import pdb;pdb.set_trace()

	
	
	def as_json(self, **kwargs):
		return super(ValueToken, self).as_json(
				value_type=repr(self.value_type),
				required=self.required,
				default=self.default,
				desc=self.desc, 
				**kwargs)

	def __repr__(self):
		return u"""<ValueToken path='{}' default='{}' type='{}'>\n""".format(self.path, self.default, self.value_type)



# ============================================================================================================
# ============================================================================================================
# == Now the actuall implementiations of the ValueTokens


class ExplicitValue(Token):
	"""
	This class expects a direct value and the validated value must be exactly the same
	"""

	def __init__(self, value, msg=None):
		super(ExplicitValue, self).__init__(msg=msg)
		self.expected_value = value

	def set_path(self, parent_path):
		self.path = u"{} -> <Value [{}]>".format(parent_path, self.expected_value)

	def as_json(self):
		return super(ExplicitValue, self).as_json(expected_value=self.expected_value)

	def _validate(self, value, default=None, has_default=False):
		if not value == self.expected_value:
			raise ValidationError(self.msg or u"{} expected {} but got {}".format(self.path, self.expected_value, value))
		return value



@Token.register_for(float)
class Float(ValueToken):
	""" For handling Floats """
	def __init__(self, **kwargs):
		super(Float, self).__init__(float, **kwargs)


class Decimal(ValueToken):
	""" For handling decimal-types (-> 8.20) """
	def __init__(self, **kwargs):
		import decimal
		super(Decimal, self).__init__(decimal.Decimal, **kwargs)


@Token.register_for(int)
class Int(ValueToken):
	def __init__(self, **kwargs):
		super(Int, self).__init__(int, **kwargs)


if sys.version_info.major == 2: # In Python 2
		
	@Token.register_for(unicode)
	class Unicode(ValueToken):
		def __init__(self, **kwargs):
			super(Unicode, self).__init__(unicode, **kwargs)

	@Token.register_for(str)
	class Bytestring(ValueToken):
		def __init__(self, **kwargs):
			super(Bytestring, self).__init__(str, **kwargs)


else: # In python 3
	@Token.register_for(str)
	class Unicode(ValueToken):
		def __init(self, **kwargs):
			super(Unicode, self).__init__(str, **kwargs)

	@Token.register_for(bytes)
	class Bytestring(ValueToken):
		def __init__(self, **kwargs):
			super(Bytestring, self).__init__(bytes, **kwargs)


class String(ValueToken):
	"""
	This token exists to cover simple strings, which can either be str or unicode (in Python 2) 
	or Unicode (Python 3)
	(So basicly a string without having to worry if python 2 or 3)
	"""
	def __init__(self, **kwargs):
		types = (unicode, str) if sys.version_info.major == 2 else (str) # IN python 3 str is unicode
		super(String, self).__init__(types, **kwargs)

   
@Token.register_for(bool)
class Bool(ValueToken):
	def __init__(self, **kwargs):
		super(Bool, self).__init__(bool, **kwargs)

		
@Token.register_for(object)
class Object(ValueToken):
	def __init__(self, **kwargs):
		super(Object, self).__init__(object, **kwargs)