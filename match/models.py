from django.db import models
from django import forms
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, AbstractUser
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

class Person(models.Model):
    name = models.CharField(max_length=32)
    bdate = models.CharField(max_length=10)
    btime = models.CharField(max_length=5)
    bplace = models.CharField(max_length=200)
    gender = models.CharField(max_length=6)
    user = models.CharField(max_length=100, default='')
    password = models.CharField(max_length=100)
    Su = models.CharField(max_length=15)
    Mo = models.CharField(max_length=15)
    Me = models.CharField(max_length=15)
    Ma = models.CharField(max_length=15)
    Ju = models.CharField(max_length=15)
    Ve = models.CharField(max_length=15)
    Sa = models.CharField(max_length=15)
    Ra = models.CharField(max_length=15)
    Ke = models.CharField(max_length=15)
    As = models.CharField(max_length=15)

class User(AbstractUser):
    pass

class MapSession(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=200)

class Label(models.Model):
    user = models.CharField(max_length=100)
    session = models.CharField(max_length=7)
    text = models.TextField()
    lat = models.CharField(max_length=20)
    lon = models.CharField(max_length=20)

    def __str__(self):
        return self.user

class UserVideoLink(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.CharField(max_length=100)
    url = models.CharField(max_length=50)
    name = models.CharField(max_length=80)
    description = models.TextField()
