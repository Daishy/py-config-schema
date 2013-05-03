from .core import ValueToken, ContainerToken
from .exceptions import ValidationError

@ContainerToken.register_for(int)
class Int(ValueToken):
    """ 
    A token representing a simple string.
    Extra options are: 
    `min`
        if given, the value must be >= this value
    `max`  
        if given, the value must be <= this value
    """
    def __init__(self, **kwargs):
        super(Int, self).__init__(**kwargs)
        
    def validate(self, value):
        """ Validates the integer. """
        value = super(Int, self).validate(value)
        if value != None and not isinstance(value, int):
            raise ValidationError(u"int-value expected, but got {}".format(type(value)))
        return value
    
    def as_json(self, **kwargs):
        return super(Int, self).as_json(name="Int", **kwargs)


@ContainerToken.register_for(str)
class String(ValueToken):
    """ 
    A token representing a Unicode-String
    """
    def __init__(self, **kwargs):
        super(String, self).__init__(**kwargs)
        
    def as_json(self, **kwargs):
        return super(String, self).as_json(name="String", **kwargs)
    
    def validate(self, value):
        value = super(String, self).validate(value)
        
        if value != None and not (isinstance(value, str) or isinstance(value, unicode)):
            raise ValidationError(u"String expected, but got {}".format(type(value)))
        return value


class Path(String):
    """
    Token for validating a file or path
    """
    # TODO
   
@ContainerToken.register_for(bool)
class Bool(ValueToken):
    """
    Token for boolean values
    """
    def __init__(self, **kwargs):
        super(Bool, self).__init__(**kwargs)
        
    def as_json(self, **kwargs):
        return super(Bool, self).as_json(name="Bool")
    
    def validate(self, struct):
        struct = super(Bool, self).validate(struct)
        if struct != None and not isinstance(struct, bool):
            raise ValidationError(u"value should be boolean, but is {}".format(struct))
        return struct


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
    
    def __init__(self, definition):
        """
        Init the Dict with the given python-dict. This will extract the settings for the dict
        and all tokens expected
        """
        # First extract all settings for the dict
        self.allow_extra_keys = definition.pop("__allow_extra_keys__", False)
        self.required = definition.pop("__required__", True)
        
        # Now extract the rest of the entries
        self.compiled = {}
        for key, value in definition.items():
            self.compiled[key] = self._get_token(value, name=key)
        
    def validate(self, struct):
        """
        Validate the dictionary. This will iterate through the compiled_definition 
        stored in this instance and check each key with the value given.
        If the key is in `value`, the associated token will validate it. If not, TODO
        """
        result = {}
        
        # Check if we have data and need Data
        if struct == None:
            if self.required:
                raise ValidationError(u"`struct` passed to Dict should have values, but is None!")
            
            return None
        # We have data, so check it
        else:
        
            # Now pass validation on to the child-tokens
            for key, token in self.compiled.items():
                if key in struct:
                    result[key] = token.validate(struct.pop(key))
                else:
                    result[key] = token.validate(None)
            
            # Finally check, if we still have keys in the struct left
            if not self.allow_extra_keys and len(struct):
                raise ValidationError(u"Found keys ({}) not defined in Schema. This is not allowed!".format(u",".join(struct.keys())))
        
            return result
    
        
    def as_json(self, **kwargs):
        _tmp = {key: token.as_json() for key, token in self.compiled.items()}
        return super(Dict, self).as_json(name="dict", allow_extra_keys=self.allow_extra_keys, **_tmp)
    

    
