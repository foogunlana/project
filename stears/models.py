from django.db import models


class ArticleImageModel(models.Model):
    docfile = models.FileField(upload_to='articleImages/%Y/%m/%d')
    title = models.CharField(max_length=50, default='')
    description = models.CharField(max_length=100, default='')
    source = models.URLField(max_length=100, default='')


class ProfileImageModel(models.Model):
    docfile = models.FileField(upload_to='profileImages/%Y/%m/%d')


class ReportModel(models.Model):
    pdf = models.FileField(upload_to='reports/%Y/%m/%d')
    author = models.CharField(max_length=50)
    title = models.CharField(max_length=50, default='')
    industry = models.BooleanField(default=False)
    summary = models.CharField(default='', max_length=200)
    week_ending = models.DateField()
