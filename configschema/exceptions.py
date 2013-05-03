class SchemaError(Exception):
    """
    This is raised, if the schema is not valid and couldnt be compiled
    """
    pass



class ValidationError(Exception):
    """ 
    This is raised, if there was an error during the validation 
    """
    pass
    