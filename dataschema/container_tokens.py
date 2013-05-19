

from collections import OrderedDict

from .core import ContainerToken
from .exceptions import SchemaError, ValidationError


__all__ = ['And', 'Or', 'Dict']



class And(ContainerToken):
	"""
	This token holds a range of other tokens which must all validate, if validation is called on
	this container
	"""

	def __init__(self, *args):
		super(And, self).__init__()
		self.compiled = []
		for arg in args:
			token = self.get_token(arg)
			token.name = "Child-token of And `{}`".format(self.name)
			self.compiled.append(token)


	def validate(self, values):
		for token in self.compiled:
			values = token.validate(values)
		return values




class Or(ContainerToken):
	"""
	This token holds a set of other tokens. If validate, the first token to successfully validate will be used.
	If no token can validate the input, a schema-error is raised
	"""

	def __init__(self, *args):
		super(Or, self).__init__()
		self.compiled = []
		for arg in args:
			token = self.get_token(arg)
			token.name = "Child-token of Or `{}`".format(self.name)
			self.compiled.append(token)

	def validate(self, values):
		for token in self.compiled:
			try:
				return token.validate(values)
			except SchemaError as e:
				pass

		return SchemaError(u"Or-Token {} found no child-token that validates the input `{}`".format(self.name, values))



class TypeKey(object):
	"""
	A typekey is used in the dict, if not a value (e.g. {"a": int}) is used, but a 
	type (e.g. {str: object})). TypeKeys have an ordering, where a more specific Key 
	is less then less specific one (bool < int < number), which gives more specific keys
	the chance to check their value first. 
	"""
	def __init__(self, key_type):
		self.key_type = key_type

	def matches(self, value_key):
		return isinstance(value_key, self.key_type)

	def __repr__(self):
		return u"<Dict.TypeKey type={}>".format(self.key_type)

	def __cmp__(self, other):
		""" return -1 (smaller) if self is a child of other, else we dont care """
		return -1 if issubclass(self.key_type, other.key_type) else 0



class Dict(ContainerToken):
	""" 
	Holds a python-dictionary with a list of tokens and some other configurations. This class
	cant be instanciated directly, its only used in the internal representation.
	
	If allow_extra_keys is False (Default is False), the dict will validate only known keys 
	are within the struct to validate.
	
	This class is somewhat different from the other tokens. First of, it can only be instantited indireclty
	within the hirarchy, furthermore this does not register for a basic type, because the object
	is created a bit different (It gets the Sub-defintion of the python-dict)
	"""
	
	# Static objects for storing infos on the dict. object is used, to get a unique object to store in the dict
	default, fixed, desc, required = object(), object(), object(), object()
	
	
	def __init__(self, definition):
		"""
		Init the Dict with the given python-dict. This will extract the settings for the dict
		and all tokens expected
		"""

		super(Dict, self).__init__()

		# First extract all settings for the dict
		self.fixed = definition.pop(Dict.fixed, True)
		self.required = definition.pop(Dict.required, True)
		self.default = definition.pop(Dict.default, None)
		self.desc = definition.pop(Dict.desc, None)
		
		# As a first step get all keys, distinguish them and get the token
		self.compiled_valuekeys = {}
		self.compiled_typekeys = {}
		try:
			for key, value in definition.items():
				token = self.get_token(value)
				token.name = "name=" + repr(key)

				if not isinstance(key, type):
					self.compiled_valuekeys[key] = token
				else:
					self.compiled_typekeys[TypeKey(key)] = token
		except SchemaError as e:
			raise SchemaError(u"Dict '{}': {}".format(self.name, e.message))
			

		# Now order the Typekey-dict with respect to their priority
		self.compiled_typekeys = OrderedDict(sorted(self.compiled_typekeys.items(), key=lambda t: t[0]))
		

		
	def validate(self, value):
		"""
		Validate the dictionary. This will first iterate through the `compiled_valuekeys` and process each 
		entry with the matching entry in `value` (Keys that are not found in value will be validate with None as value.
		If the token wont allow that, a ValidationError is raised!)
		Next up, each entry that was not yet validated in values will be passed to the first handler in `compiled_typekeys`, 
		if there is a matching one. `validate` will be called on the found handler, with the entry in `value`.
		At last, if there are still unprocessed entries in value, we will check if that is allowed or not
		"""
		# we dont have data, so check if there is a default and if so, return that
		if value == None:
			if self.default == None and self.required:
				raise ValidationError(u"Value passed to '{}'' should have values, but is None!".format(self.name))
			return self.default
			
		# check we have the right kind of data
		elif not isinstance(value, dict):
			raise ValidationError(u"Value passed to '{}'' is not a dict! (value: {})".format(self.name, type(value)))

		# we have both data and is the right type, so validate it
		else:
			result = {}
			tmp = {k: v for k, v in value.items()} # Create a copy of the input, so the input is not changed

			
			try:
				# First validate each token found in the value-dict
				for key, token in self.compiled_valuekeys.items():
					result[key] = token.validate(tmp.pop(key, None))
			
				# Now try to match the compiled_typekeys to the left-over values (If match, validate and remove value)
				for key, value in tmp.items():
					for dictkeytype, token in self.compiled_typekeys.items():
						if dictkeytype.matches(key):
							result[key] = token.validate(value)
							del tmp[key]
							break

			except ValidationError as e:
				raise ValidationError(u"Dict '{}': {}".format(self.name, e.message))
	

			# now just check if there are leftovers and if they are allowed. If so, add them 
			if self.fixed and len(tmp) > 0:
				raise ValidationError(u"Dict '{}'' is fixed but encountered additional values: {}".format(self.name, tmp))

			# return the final dict
			return result

	
	
	def __add__(self, other):
		""" Unless most other tokens, two dicts can be combined into a new one. This can be used to merge to Schemas
		When combining two dicts, the settings from the first dict are used. Each key in both the dicts has to be unique. It
		is not possible for example to add {'a': int} to {'a': bool}. 
		This doesnt produce a deep copy. Only a new Dict-token is created, all other tokens are the same!
		"""
		if not isinstance(other, Dict):
			raise SchemaError(u"Tried to add non-dict ({}) to dict!".format(other))
		
		# Add Tokens
		tokens = {key: token for key, token in self.compiled.items()}
		for key, token in other.compiled.items():
			if key in tokens:
				raise SchemaError(u"Can't merge {} with {}, because of multiple key `{}`.".format(self, other, key))
			tokens[key] = token
	
		# Add Settings from self and other (the resulting dict will have the stricter of each rules)
		tokens[Dict.fixed] = self.fixed or other.fixed
		tokens[Dict.required] = self.required or other.required
		tokens[Dict.desc] = self.desc
		if self.default or other.default:
			tokens[Dict.default] = {key: value for key, value in self.default.items()} if self.default else {}
			tokens[Dict.default].update({key: value for key, value in other.default.items()} if other.default else {})
		
		return Dict(tokens)
		
		
		
		
		
	def as_json(self, **kwargs):
		_tmp = {key: token.as_json() for key, token in self.compiled.items()}
		return super(Dict, self).as_json(name="dict", fixed=self.fixed, required=self.required, desc=self.desc, default=self.default, **_tmp)