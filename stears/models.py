from django.db import models
from imagekit.processors import SmartResize, ResizeToFill
from imagekit.models import ImageSpecField


class ArticleImageModel(models.Model):
    docfile = models.FileField(upload_to='articleImages/%Y/%m/%d')
    title = models.CharField(max_length=50, default='')
    description = models.CharField(max_length=100, default='')
    source = models.URLField(max_length=100, default='')
    picker = ImageSpecField(
        source='docfile', processors=[SmartResize(200, 117)], format='JPEG')
    feature = ImageSpecField(
        source='docfile', processors=[ResizeToFill(414, 242)], format='JPEG')
    main_feature = ImageSpecField(
        source='docfile', processors=[ResizeToFill(800, 468)], format='JPEG')
    main_feature_mobile = ImageSpecField(
        source='docfile', processors=[SmartResize(736, 380)], format='JPEG')


class ProfileImageModel(models.Model):
    title = models.CharField(max_length=50, default='')
    docfile = models.FileField(upload_to='profileImages/%Y/%m/%d')
    small = ImageSpecField(
        source='docfile', processors=[SmartResize(200, 200)], format='JPEG')
    large = ImageSpecField(
        source='docfile', processors=[ResizeToFill(500, 500)], format='JPEG')


class ReportModel(models.Model):
    pdf = models.FileField(upload_to='reports/%Y/%m/%d')
    author = models.CharField(max_length=50)
    title = models.CharField(max_length=50, default='')
    industry = models.BooleanField(default=False)
    ftype = models.CharField(max_length=50, default='weekly')
    summary = models.CharField(default='', max_length=200)
    week_ending = models.DateField()
