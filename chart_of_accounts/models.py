from django.db import models

class ExcelDocument(models.Model):
    excel_file = models.FileField(upload_to='excel_documents/')
    json_data = models.JSONField(blank=True, null=True)

class ExcelData(models.Model):
    column_a = models.CharField(max_length=255, blank=True, null=True)
    column_b = models.CharField(max_length=255, blank=True, null=True)
    column_c = models.CharField(max_length=255, blank=True, null=True)