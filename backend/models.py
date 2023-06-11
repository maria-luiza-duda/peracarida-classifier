from django.db import models

class Record(models.Model):
    researcher_name = models.CharField(max_length=100)
    institution = models.CharField(max_length=100)
    collector_name = models.CharField(max_length=100)
    collection_location = models.CharField(max_length=100)
    latitude = models.IntegerField()
    longitude = models.IntegerField()
    depth = models.IntegerField()
    sediment_type = models.CharField(max_length=100)
    specimen_size = models.IntegerField()
    photo_material = models.CharField(max_length=100)
    