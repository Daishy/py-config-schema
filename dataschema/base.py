"""
Contains the basic classes for all tokens.
"""

from dataschema.exceptions import SchemaError, ValidationError


class Token(object):
	""" Base-class for all Tokens """

	# this part handles the association of basic types to tokens
	type_register = {}

	@classmethod
	def register_for(cls, datatype):
		""" Decorator to use for ValueTokens, to register basic Datatypes """
		def inner(cls):
			Token.type_register[datatype] = cls
			return cls        
		return inner

	@classmethod
	def get_token(cls, definition):
		"""
		Return the token appropriate for the type of definition
		
		:param definition:
			The value to parse. This may be almost anything. Some types are handled
			seperatly (like dict, list or basic types like int or bool, for which a ValueToken is defined).
			Elements that are already a descendent of the Token-Class will be kept as is. Other values
			are handled as an ExplizitValue, that should be validated against

		:return: The appropriate token-instance for the definition
		"""
		
		if isinstance(definition, Token): # If already a token just return
			return definition;
		elif isinstance(definition, dict): # If a dict, than use the dict-class
			from dataschema.tokens.container import Dict
			return Dict(definition)	
		elif isinstance(definition, list): # if a list, use the List-Class
			from dataschema.tokens.container import List
			return List(definition)	
		elif isinstance(definition, type):
			if definition in Token.type_register: # If type is one of the associations in tokens
				return Token.type_register[definition]()
			else: # The type is not known
				raise SchemaError(u"Schema can't resolve basic type `{}` to a schema-type".format(definition))
		else: # Otherwise assume the definition should be taken "as is" and the value must match exactly
			from dataschema.tokens.values import ExplicitValue
			return ExplicitValue(definition)


	
	# Store the exceptions on the schema, so they are easy to access
	SchemaError = SchemaError
	ValidationError = ValidationError
	
	def __init__(self, msg=None, desc=None):
		"""
		:param msg: A custom error message for ValidationError. If None, a default-msg is generated
		:param desc: The description of the Token
		"""
		self.path = ""
		self.msg = msg
		self.desc = desc
		
	def set_path(self, parent_path):
		""" This method is used to set the path for the token. The path is later on used in
		error messages or debugging
		"""
		self.path = "{}{}{}".format(
			parent_path if parent_path else "",
			" -> " if parent_path else "",
			self.__class__.__name__)
	
	def as_json(self, **kwargs):
		""" Return the token-compound as a python-dict. Can be used to extract auto-docu-infos """
		if not 'token' in kwargs:
			kwargs['class'] = self.__class__.__name__
		if not 'path' in kwargs:
			kwargs['path'] = self.path
		if not 'desc' in kwargs:
			kwargs['desc'] = self.desc

		return {key: value for key,value in kwargs.items()}

	def validate(self, values, **kwargs):
		"""
		This is the main validate-function. This parses the arguments given, to see if
		a real default was given. This is neccessary, because a default=None in the definition
		would be not sufficient to check if a default was given or not. So this function
		checks if a default is in kwargs and calls _validate with that results
		"""
		if 'default' in kwargs:
			return self._validate(values, default=kwargs.get('default'), has_default=True)
		else:
			return self._validate(values, default=None, has_default=False)

	
	def _validate(self, values, default=None, has_default=False):
		"""
		"""
		raise NotImplemented(u"validate-method must be overriden in subclasses!")
	
	def __add__(self, other):
		""" This is used to merge to Schemas. Each Token (or base-class) must override
		this method, if it is merge-able. 
		"""
		raise SchemaError(u"Tried to merge token {} and {}, which is not possible or not implemented!".format(self.path, other))