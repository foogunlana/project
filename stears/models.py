from django.db import models


class ArticleImageModel(models.Model):
    docfile = models.FileField(upload_to='articleImages/%Y/%m/%d')


class ProfileImageModel(models.Model):
    docfile = models.FileField(upload_to='profileImages/%Y/%m/%d')


class ReportModel(models.Model):
    pdf = models.FileField(upload_to='reports/%Y/%m/%d')
    author = models.CharField(max_length=50)
    industry = models.BooleanField(default=False)
    summary = models.CharField(default='', max_length="200")
    week_ending = models.DateField()
