from .return_class import AbstractApiClass


class FeatureGroupRowProcessSummary(AbstractApiClass):
    """
        A summary of the feature group processes for a deployment.

        Args:
            client (ApiClient): An authenticated API Client instance
            totalProcesses (int): The total number of processes
            pendingProcesses (int): The number of pending processes
            completeProcesses (int): The number of complete processes
            failedProcesses (int): The number of failed processes
    """

    def __init__(self, client, totalProcesses=None, pendingProcesses=None, completeProcesses=None, failedProcesses=None):
        super().__init__(client, None)
        self.total_processes = totalProcesses
        self.pending_processes = pendingProcesses
        self.complete_processes = completeProcesses
        self.failed_processes = failedProcesses

    def __repr__(self):
        return f"FeatureGroupRowProcessSummary(total_processes={repr(self.total_processes)},\n  pending_processes={repr(self.pending_processes)},\n  complete_processes={repr(self.complete_processes)},\n  failed_processes={repr(self.failed_processes)})"

    def to_dict(self):
        """
        Get a dict representation of the parameters in this class

        Returns:
            dict: The dict value representation of the class parameters
        """
        return {'total_processes': self.total_processes, 'pending_processes': self.pending_processes, 'complete_processes': self.complete_processes, 'failed_processes': self.failed_processes}
