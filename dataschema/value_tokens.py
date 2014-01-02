"""
This file contains all simple value tokens (like Int, String, Bool)
"""

from .core import ValueToken, Token, ContainerToken
from .exceptions import ValidationError

import sys



__all__ = ["Int", "String", "Unicode", "Bytestring", "Bool", "Object", "Decimal", "Float"]


class Value(Token):
    """
    A direct value to check for
    """

    def __init__(self, value, msg=None):
        super(Value, self).__init__(msg=msg)
        self.expected_value = value

    def set_path(self, path):
        self.path = path + "<Value {}>".format(self.expected_value)

    def validate(self, value):
        if not value == self.expected_value:
            raise ValidationError(self.msg or u"{} expected {} but got {}".format(self.path, self.expected_value, value))
        return value

@ContainerToken.register_for(float)
class Float(ValueToken):
    """ For handling Floats """
    def __init__(self, **kwargs):
        super(Float, self).__init__(float, **kwargs)


class Decimal(ValueToken):
    """ For handling decimal-types (-> 8.20) """
    def __init__(self, **kwargs):
        import decimal
        super(Decimal, self).__init__(decimal.Decimal, **kwargs)


@ContainerToken.register_for(int)
class Int(ValueToken):
    def __init__(self, **kwargs):
        super(Int, self).__init__(int, **kwargs)


if sys.version_info.major == 2: # In Python 2
        
    @ContainerToken.register_for(unicode)
    class Unicode(ValueToken):
        def __init__(self, **kwargs):
            super(Unicode, self).__init__(unicode, **kwargs)

    @ContainerToken.register_for(str)
    class Bytestring(ValueToken):
        def __init__(self, **kwargs):
            super(Bytestring, self).__init__(str, **kwargs)


else: # In python 3
    @ContainerToken.register_for(str)
    class Unicode(ValueToken):
        def __init(self, **kwargs):
            super(Unicode, self).__init__(str, **kwargs)

    @ContainerToken.register_for(bytes)
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

        

   
@ContainerToken.register_for(bool)
class Bool(ValueToken):
    def __init__(self, **kwargs):
        super(Bool, self).__init__(bool, **kwargs)

        
@ContainerToken.register_for(object)
class Object(ValueToken):
    def __init__(self, **kwargs):
        super(Object, self).__init__(object, **kwargs)