from __future__ import unicode_literals

from django.db import models

# Create your models here.


class Downloaded(models.Model):
    url = models.CharField(max_length=500)
    date = models.DateTimeField('date downloaded')
    agent_name = models.CharField(max_length=30)
    jsondata = models.TextField()
        
        