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
    discountrate2 = models.FloatField()
    webchatid = models.CharField(max_length = 50)
    
class MembershipAmountLog(models.Model):
    id = models.AutoField(primary_key=True)
    membershipId = models.CharField(max_length = 10)
    addAmount = models.FloatField()
    transactionDate = models.DateTimeField()
    
    
class DoctorInfo(models.Model):
    id = models.AutoField(primary_key=True)
    doctorname = models.CharField(max_length = 20)
    phonenumber = models.CharField(max_length = 11)
    comments = models.CharField(max_length = 400)
    service = models.CharField(max_length = 200)
    webchatid = models.CharField(max_length = 50)
    
class ServiceType(models.Model):
    id = models.AutoField(primary_key=True)
    servicename = models.CharField(max_length = 50)
    servicerate = models.IntegerField()
    
class ServiceRate(models.Model):
    id = models.AutoField(primary_key=True)
    ratename = models.CharField(max_length = 50)
    rate = models.FloatField()
    
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
    
class Transaction(models.Model):
    id = models.AutoField(primary_key=True)
    membershipId = models.CharField(max_length = 10)
    doctorId = models.CharField(max_length = 10)
    bookingId = models.CharField(max_length = 10)
    servicetypeId = models.CharField(max_length = 10)
    paymentType = models.CharField(max_length = 2) #01 cash, 02 membership card, 03 weixin 00, not decied
    amount = models.FloatField()
    successFlag = models.CharField(max_length = 1) #0 unpayed, 1 payed
    transactionDate = models.DateField()
    
    
    