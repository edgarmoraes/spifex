from django.db import models

class Project(models.Model):
    project_name = models.CharField(max_length = 100)
    project_code = models.CharField(max_length = 100)
    project_type = models.CharField(max_length = 100)
    project_description = models.CharField(max_length = 256)
