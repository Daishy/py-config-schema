"""
This file contains all simple value tokens (like Int, String, Bool)
"""

from .core import ValueToken, ContainerToken


__all__ = ["Int", "String", "Bool", "Object"]

@ContainerToken.register_for(int)
class Int(ValueToken):
    """  A token representing a simple string. """
    
    def __init__(self, **kwargs):
        super(Int, self).__init__(int, **kwargs)


@ContainerToken.register_for(str)
class String(ValueToken):
    """ A token representing a Unicode-String """
    
    def __init__(self, **kwargs):
        super(String, self).__init__(str, **kwargs)

   
@ContainerToken.register_for(bool)
class Bool(ValueToken):
    """ Token for boolean values """
    
    def __init__(self, **kwargs):
        super(Bool, self).__init__(bool, **kwargs)

        
@ContainerToken.register_for(object)
class Object(ValueToken):
    """ Token for variable objects """
    def __init__(self, **kwargs):
        super(Object, self).__init__(object, **kwargs)