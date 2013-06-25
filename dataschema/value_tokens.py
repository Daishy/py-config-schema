"""
This file contains all simple value tokens (like Int, String, Bool)
"""

from .core import ValueToken, ContainerToken

import sys



__all__ = ["Int", "String", "Bool", "Object", "Bytestring", "AnyString"]

@ContainerToken.register_for(int)
class Int(ValueToken):
    def __init__(self, **kwargs):
        super(Int, self).__init__(int, **kwargs)


if sys.version_info.major == 2:
        
    @ContainerToken.register_for(unicode)
    class String(ValueToken):
        def __init__(self, **kwargs):
            super(String, self).__init__(unicode, **kwargs)

    @ContainerToken.register_for(str)
    class Bytestring(ValueToken):
        def __init__(self, **kwargs):
            super(Bytestring, self).__init__(str, **kwargs)


else:
    @ContainerToken.register_for(str)
    class String(ValueToken):
        def __init(self, **kwargs):
            super(String, self).__init__(str, **kwargs)

    @ContainerToken.register_for(bytes)
    class Bytestring(ValueToken):
        def __init__(self, **kwargs):
            super(Bytestring, self).__init__(bytes, **kwargs)


class AnyString(ValueToken):
    """
    This token exists to cover simple strings, which can either be str or unicode
    (So basicly a string without having to worry if python 2 or 3)
    """
    def __init__(self, **kwargs):
        types = (unicode, str) if sys.version_info.major == 2 else (str)
        super(AnyString, self).__init__(types, **kwargs)

        

   
@ContainerToken.register_for(bool)
class Bool(ValueToken):
    def __init__(self, **kwargs):
        super(Bool, self).__init__(bool, **kwargs)

        
@ContainerToken.register_for(object)
class Object(ValueToken):
    def __init__(self, **kwargs):
        super(Object, self).__init__(object, **kwargs)