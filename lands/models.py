from django.db import models
from django_extensions.db.models import TimeStampedModel

# Create your models here.


class Info(TimeStampedModel):
    group_name = models.CharField(max_length=30)
    name = models.CharField(max_length=100)


class Land(TimeStampedModel):
    latitude = models.FloatField()
    longitude = models.FloatField()
    name = models.CharField(max_length=100)


class LandInfoMapping(TimeStampedModel):
    info = models.ForeignKey("lands.Info", on_delete=models.CASCADE)
    land = models.ForeignKey("lands.Land", on_delete=models.CASCADE)
    like_count = models.IntegerField(default=0)
    unlike_count = models.IntegerField(default=0)


class LandInfoUserMapping(TimeStampedModel):
    land_info_mapping = models.ForeignKey("lands.LandInfoMapping", on_delete=models.CASCADE)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    is_like_event = models.BooleanField(default=False)


class LandImageMapping(TimeStampedModel):
    land = models.ForeignKey("lands.Land", on_delete=models.CASCADE)
    image = models.TextField()


class LandCommentMapping(TimeStampedModel):
    land = models.ForeignKey("lands.Land", on_delete=models.CASCADE)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    comment = models.TextField()
