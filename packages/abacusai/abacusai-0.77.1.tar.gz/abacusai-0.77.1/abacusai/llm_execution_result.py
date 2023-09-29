from .return_class import AbstractApiClass


class LlmExecutionResult(AbstractApiClass):
    """
        Results of executing queries using LLM.

        Args:
            client (ApiClient): An authenticated API Client instance
            status (str): The status of the execution.
            error (str): The error message if the execution failed.
    """

    def __init__(self, client, status=None, error=None):
        super().__init__(client, None)
        self.status = status
        self.error = error

    def __repr__(self):
        return f"LlmExecutionResult(status={repr(self.status)},\n  error={repr(self.error)})"

    def to_dict(self):
        """
        Get a dict representation of the parameters in this class

        Returns:
            dict: The dict value representation of the class parameters
        """
        return {'status': self.status, 'error': self.error}
