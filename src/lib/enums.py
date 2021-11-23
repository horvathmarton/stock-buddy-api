from django.db import models


class SyncStatus(models.TextChoices):
    """
    Enum indicating the status of a sync operation.
    """

    STARTED = "started"
    FINISHED = "finished"
    FAILED = "failed"
    ABORTED = "aborted"
