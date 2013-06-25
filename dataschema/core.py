"""
Contains the basic classes for all tokens
it also contains the ConfigSchema-Class
"""

from .exceptions import SchemaError, ValidationError





class Token(object):
	""" Base-class for all Tokens """

	
	# Store the exceptions on the schema, so they are easy accessable
	SchemaError = SchemaError
	ValidationError = ValidationError
	
	def __init__(self, msg=None):
		"""
		:param msg: A custom error message for ValidationError. If none, a default-msg is generated
		"""
		self.path = ""
		self.msg = msg

	def set_path(self, path):
		""" This method is used to set the path for the token. The path is later on used in
		error messages or debugging """
		self.path = path_info + self.path


	def as_json(self, **kwargs):
		""" Return the token as a python/json-structure. Can be used to extract auto-docu-infos """
		return {key: value for key, value in kwargs.items()}
	

	def validate(self, values):
		raise NotImplemented(u"validate-method must be overriden in subclasses!")
	
	
	def __add__(self, other):
		""" This is used to merge to Schemas. Each Token (or base-class) must override
		this method, if it is merge-able. 
		"""
		raise SchemaError(u"Tried to merge token {} and {}, which is not possible!".format(self.path, other))

	# TODO: +=-operator, radd, subtract?



class ContainerToken(Token):
	"""
	This class manages the conversion from a basic python type like
	dict, int, str, bool, ... to the appropriate token (Int, Dict, ...)
	"""

	tokens = {}

	def __init__(self):
		super(ContainerToken, self).__init__(msg=None)

	@staticmethod
	def register_for(datatype):
		""" Decorator to use for ValueTokens, to register basic Datatypes """
		def inner(cls):
			ContainerToken.tokens[datatype] = cls
			return cls        
		return inner


	def get_token(self, definition):
		"""
		Return the token appropriate for the type of definition
		
		:param definition: A python datastructure (int,str, bool, dict, list, ....)
		:return: The appropriate token-instance for the definition
		"""                
		from .container_tokens import Dict
		
		if isinstance(definition, Schema): # if definition is schema, just return the inner token
			return definition.compiled
		if isinstance(definition, Token): # If already a token, use that one
			return definition;
		elif isinstance(definition, dict): # If a dict, than use the dict-class
			return Dict(definition)
		elif definition in ContainerToken.tokens: # If type is one of the associations in tokens
			return ContainerToken.tokens[definition]()
		else: # The type is not known
			raise SchemaError(u"Schema can't resolve basic type `{}` to a schema-type".format(definition))



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
		super(ValueToken, self).__init__(msg=msg)
		self.value_type = value_type
		self.required = required
		self.desc = desc
		self.default = default

	def set_path(self, path):
		self.path = path + self.__class__.__name__
		
		
	def validate(self, value):
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
	
	
	def as_json(self, **kwargs):
		return super(ValueToken, self).as_json(
				value_type=repr(self.value_type),
				required=self.required,
				default=self.default,
				desc=self.desc, 
				**kwargs)

	def __repr__(self):
		return u"<ValueToken {} ({})>".format(self.path, self.value_type)
	

class DecoratorToken(Token):
	"""
	The basetoken used to validate additional stuff, like Range or Regex
	"""

	def __init__(self, msg=None):
		"""
		:param msg: A userdefined error message if a ValidationError occurs within the Decorator
		"""
		super(DecoratorToken, self).__init__(msg=msg)
	
	def set_path(self, path):
		self.path = path + self.__class__.__name__

	def __repr__(self):
		return u"<DecoratorToken {}>".format(self.path)


	
class Schema(ContainerToken):
	"""
	The main-class for validating the config. Compiles the definition and checks it is valid.
	After this, the validate-method will validate a given struct against the definition.
	"""
	
	def __init__(self, definition):
		"""
		Init a new validator 
		:param definition: The definition to parse and validate again later on
		"""
		self.compiled = self.get_token(definition)
		self.compiled.set_path(u"Schema->")
		
		
	def validate(self, values):
		""" 
		Validate the values against the definition. If the values does not validate
		a ConfigValidationError is raised, otherwise the valid config is returned
		:param values: The values to validate
		:param return: A python data-structure that resembles the values, but enhanced with default-values and validated
		"""
		return self.compiled.validate(values)
		
		
	def __add__(self, other):
		""" Merge to config-Schemas and return the result as new config-schema. """
		return Schema(self.compiled + other.compiled)
		
		
	def as_json(self):
		return {
			"name": u"Schema",
			"definition": self.compiled.as_json()
		}
		
		
	def __repr__(self):
		""" This uses the as_json()-Method to obtain a representation of the schema
		which contains all information """
		import simplejson as json		
		return json.dumps(self.as_json(), indent=4)
		
		