class ConfigValidatorError(Exception):
    """
    This is raised, if the schema is not valid and couldnt be compiled
    """
    pass

class ConfigValidationError(ConfigValidatorError):
    pass
    