class Error(Exception):
    def __init__(self, message: str):
        """Exception raised for different kinds of errors.
        Attributes:
                message: explanation of the error
        """
        self.message = message


# Exception raised when an internal error occured within the Aqueduct system.
class InternalServerError(Error):
    def __init__(self, message: str):
        self.message = (
            "An internal server error occured when processing the "
            "request. This is likely not your fault. Please contact "
            "us at support@runllm.com with your RunLLM account "
            "email and a brief description of what you were trying to "
            "do when the error occurred, so that we can further "
            "assist you. Apologies for the inconvenience!"
        )


# Exception raised when the requested resource is not found.
class ResourceNotFoundError(Error):
    pass


class ClientValidationError(Error):
    pass


# A catch-all exception raised for all other errors.
class RunLLMError(Error):
    pass


# Exception raised for errors occured when certain inputs are missing or contain
# invalid values. Also thrown on any errors in the user's queries or function code.
class InvalidRequestError(Error):
    pass
