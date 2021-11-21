from django.db import models

class SyncStatus(models.TextChoices):
    STARTED = 'started'
    FINISHED = 'finished'
    FAILED = 'failed'
    ABORTED = 'aborted'
