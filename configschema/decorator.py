
from core import DecoratorToken
from exceptions import ConfigValidationError


class Range(DecoratorToken):
    """ 
    A token representing a Range of values
    """
    
    def __init__(self, wrapped_token, min=None, max=None):
        super(Range, self).__init__(wrapped_token)
        self.min = min
        self.max = max
        
    def as_json(self):
        return super(Range, self).as_json(min=self.min, max=self.max, decorator="Range")
    
    def validate(self, struct):
        struct = super(Range, self).validate(struct)
        if struct != None and self.min != None and struct < self.min:
            raise ConfigValidationError(u"Range: Value {} is not <= than {}".format(struct, self.min))
        if struct != None and self.max != None and struct > self.max:
            raise ConfigValidationError(u"Range: Value {} is not >= than {}".format(struct, self.min))
        return struct

class Length(DecoratorToken):
    """ Token to check for a specific length (min, max, exakt) """
    def __init__(self, wrapped_token, min=None, max=None, length=None):
        super(Length, self).__init__(wrapped_token)
        self.min = min
        self.max = max
        self.length = length
        
    def as_json(self):
        return super(Length, self).as_json(min=self.min, max=self.max, length=self.length, decorator="Length")
    
    def validate(self, struct):
        struct = super(Length, self).validate(struct)
        
        # check if length matches
        if struct != None:
            _length = len("{}".format(struct))
            if self.min != None and _length < self.min:
                raise ConfigValidationError(u"Length of {} is < than {}".format(struct, self.min))
            if self.max != None and _length > self.max:
                raise ConfigValidationError(u"Length of {} is > than {}".format(struct, self.max))
            if self.length != None and _length != self.length:
                raise ConfigValidationError(u"Length of {} is != than {}".format(struct, self.length))
        
        return struct


class NotEmpty(Length):
    """
    A TOken that checks if a String is not Empty)
    """
    def __init__(self, wrapped_token):
        super(NotEmpty, self).__init__(wrapped_token, min=1)
    
    def as_json(self):
        return super(NotEmpty, self).as_json(decorator="NotEmpty")
        