from django.db import models

class Chart_of_accounts(models.Model):
    column1 = models.CharField(max_length=255)
    column2 = models.CharField(max_length=255)
    column3 = models.CharField(max_length=255)
    column4 = models.CharField(max_length=255)

    def __str__(self):
        return self.column1