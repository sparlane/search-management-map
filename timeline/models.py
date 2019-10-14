"""
Models for timeline
"""

from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

from mission.models import Mission


class TimeLineEntry(models.Model):
    """
    An entry in the timeline
    """
    mission = models.ForeignKey(Mission, on_delete=models.PROTECT)
    user = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, related_name='creator%(app_label)s_%(class)s_related')
    timestamp = models.DateTimeField(default=timezone.now)

    EVENT_TYPE = (
        ('add', "Added/Created an Object"),
        ('del', "Removed an Object"),
        ('upd', "Updated/Edited an Object"),
        ('sbg', "Asset Started Search"),
        ('snd', "Asset Finished Search"),
        ('usr', "User defined Event"),
    )
    event_type = models.CharField(max_length=3, choices=EVENT_TYPE)

    message = models.TextField()

    url = models.TextField()