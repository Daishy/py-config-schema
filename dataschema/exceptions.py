


class SchemaError(Exception):
    """
    This is raised, if the schema is not valid and couldnt be compiled
    """
    def __init__(self, msg):
        super(SchemaError, self).__init__()
        self.message = msg


class ValidationError(Exception):
    """ 
    This is raised, if there was an error during the validation 
    """
    def __init__(self, msg):
        super(ValidationError, self).__init__()
        self.message = msg
    