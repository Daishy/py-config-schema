"""
TODO
"""


from .exceptions import SchemaError, ValidationError
import json


class Token(object):
    """ Base-class for all Tokens """
    
    def __init__(self):
        pass
    
    def as_json(self, **kwargs):
        """ Return the token as a python-json-structure """
        return {key: value for key, value in kwargs.items()}
    
    def validate(self, struct):
        raise NotImplemented(u"Validate must be overriden in subclasses!")




class ContainerToken(Token):
    """
    base-class for tokens, that contain other tokens
    """
    
    def __init__(self):
        super(ContainerToken, self).__init__()
        
    
    @staticmethod
    def register_for(datatype):
        """ Decorator to use for ValueTokens, to register basic Datatypes """
        def tmp(cls):
            ContainerToken.tokens[datatype] = cls
            return cls
        
        return tmp
        
    
    # Association of Python-types to Token-types. This will be filled by
    # the ValueTokens itself (Because they are not yet defined here)
    tokens = {}
    
    def _get_token(self, definition, name=None):
        """
        Return the token appropriate for the type of definition
        `definition`
            A python datastructure (int,str, bool, dict, list, ....)
        `name`
            If name is given, it will be printed along in the exception, if any is thrown
        `return`
            The appropriate token-instance for the definition
        """
        from tokens import Dict
        
        # Now return the token (either the existing one or the created one)
        if isinstance(definition, Token):
            return definition;
        elif isinstance(definition, dict):
            return Dict(definition)
        elif definition in ContainerToken.tokens:
            return ContainerToken.tokens[definition]()
        else:
            raise SchemaError("Unexpected type '{}' for definition `{}` with value `{}`".format(type(definition), name or '?', definition))
        



class ValueToken(Token):
    """
    The baseclass for all token that represent a single value. Suplies some of the basic-features for all 
    tokens.
    Possible flags are:
    `required`
        If true, the Token must be given in the config (May still be None) (Default: True)
    `desc`
        A string giving the Description of the Setting (Default: None)
    `default`
        A defaultvalue for the Token (Default: None
    """
    
    def __init__(self, required=True, desc=None, default=None):
        super(ValueToken, self).__init__()
        self.required = required
        self.desc = desc
        self.default = default
        
    def validate(self, value):
        """
        Validate the value. The base-methods simply checks if the value 
        is None and, if a default is given, replace it with default.
        if required and not value is true, a SchemaValidationError is raised
        `value`
            The value to check
        `return`
            Returns value or default, if value is None
        """
        if value == None and self.default != None:
            value = self.default
        if self.required and value == None:
            raise ValidationError(u"Token is required, but None")
        return value
        
        
    def as_json(self, **kwargs):
        return super(ValueToken, self).as_json(required=self.required,
                default=self.default,
                desc=self.desc, 
                **kwargs)
    
    
class DecoratorToken(ContainerToken):
    """ Baseclass for all Tokens, that wrap another token to enhance validation or
    add other features """
    
    
    def __init__(self, wrapped_token):
        self.wrapped_token = self._get_token(wrapped_token)
    
    def validate(self, struct):
        return self.wrapped_token.validate(struct)
    
    def as_json(self, **kwargs):
        return super(DecoratorToken, self).as_json(wrapped=self.wrapped_token.as_json(), **kwargs)
    

class ConfigSchema(ContainerToken):
    """
    The main-class for validating the config. Compiles the definition and checks it is valid.
    After this, the validate-method will validate a given struct against the definition.
    """
    
    # Store the exceptions in this class, to make easier to obtain references
    ValidationError = ValidationError
    SchemaError = SchemaError
    
    def __init__(self, definition):
        """
        Init a new validator 
        `definition`
            The definition to parse and validate again later on
        """
        self.compiled = self._get_token(definition, name="ConfigSchema")
        
        
    def validate(self, struct):
        """ 
        Validate the struct against the definition. If the struct does not validate
        a ConfigValidationError is raised, otherwise the valid config is returned
        `struct`
            The struct to validate
        `return`
            A python data-structure that resembles the struct, but enhanced with default-values and validated
        """
        return self.compiled.validate(struct)
        
        
    def as_json(self):
        return {
            u"name": u"ConfigSchema",
            "definition": self.compiled.as_json()
        }
        
        
    def __repr__(self):
        """ This uses the as_json()-Method to obtain a representation of the schema
        which contains all information """
        return json.dumps(self.as_json(), indent=4)
        
        