from __future__ import unicode_literals

from django.db import models

# Create your models here.
class AdminUser(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length = 10)
    password = models.CharField(max_length = 20)

class Membership(models.Model):
    id = models.AutoField(primary_key=True)
    vipno = models.CharField(max_length = 11)
    vipname = models.CharField(max_length = 10)
    vipnameid = models.CharField(max_length = 18)
    phonenumber = models.CharField(max_length = 11)
    password = models.CharField(max_length = 10)
    amount = models.FloatField()
    lastamount = models.FloatField()
    discounttype = models.CharField(max_length = 20)
    discountrate = models.FloatField()
    webchatid = models.CharField(max_length = 50)
    
    
class DoctorInfo(models.Model):
    id = models.AutoField(primary_key=True)
    doctorname = models.CharField(max_length = 20)
    phonenumber = models.CharField(max_length = 11)
    webchatid = models.CharField(max_length = 50)
    
class ServiceType(models.Model):
    id = models.AutoField(primary_key=True)
    servicename = models.CharField(max_length = 50)
    servicerate = models.IntegerField()
    
class DoctorServiceType(models.Model):
    id = models.AutoField(primary_key=True)
    doctorid = models.IntegerField()
    servicetypeid = models.IntegerField()
    servicename = models.CharField(max_length = 50)
    
class BookingInfo(models.Model):
    id = models.AutoField(primary_key=True)
    phonenumber = models.CharField(max_length = 11)
    name = models.CharField(max_length = 20)
    membercard = models.CharField(max_length = 20)
    bookeddoctor = models.CharField(max_length = 20)
    bookeditem = models.CharField(max_length = 50)
    bookedtime = models.CharField(max_length = 20)
    webchatid = models.CharField(max_length = 50)
    status = models.CharField(max_length = 1)
    
    
    