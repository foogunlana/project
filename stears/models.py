from django.db import models


class ArticleImageModel(models.Model):
    docfile = models.FileField(upload_to='articleImages/%Y/%m/%d')


class ProfileImageModel(models.Model):
    docfile = models.FileField(upload_to='profileImages/%Y/%m/%d')
