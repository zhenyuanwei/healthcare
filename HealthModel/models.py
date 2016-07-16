from __future__ import unicode_literals

from django.db import models

# Create your models here.
class AdminUser(models.Model):
    username = models.CharField(max_length = 10)
    password = models.CharField(max_length = 20)


class BookingInfo(models.Model):
    id = models.IntegerField(primary_key=True)
    phonenumber = models.CharField(max_length = 11)
    name = models.CharField(max_length = 20)
    membercard = models.CharField(max_length = 20)
    bookeddoctor = models.CharField(max_length = 20)
    bookeditem = models.CharField(max_length = 50)
    bookedtime = models.CharField(max_length = 20)
    webchatid = models.CharField(max_length = 50)
    status = models.CharField(max_length = 1)
    

class Membership(models.Model):
    discounttype = models.CharField(max_length = 20)
    discountrate = models.FloatField()
    
class DoctorInfo(models.Model):
    doctorname = models.CharField(max_length = 20)
    phonenumber = models.CharField(max_length = 11)
    webchatid = models.CharField(max_length = 50)
    
class ServiceType(models.Model):
    servicename = models.CharField(max_length = 50)
    servicerate = models.IntegerField()
    
class DoctorServiceType(models.Model):
    doctorid = models.IntegerField()
    servicetypeid = models.IntegerField()
    servicename = models.CharField(max_length = 50)
    
    