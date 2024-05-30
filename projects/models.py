from django.db import models

class Projects(models.Model):
    project_name = models.CharField(max_length = 100)
    project_code = models.CharField(max_length = 100)
    project_type = models.CharField(max_length = 100)
    project_description = models.CharField(max_length = 256)
    uuid_project = models.UUIDField(null=True, blank=True)