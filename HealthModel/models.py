from __future__ import unicode_literals

from django.db import models

# Create your models here.
class AdminUser(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length = 10)
    password = models.CharField(max_length = 20)
    role = models.CharField(max_length = 1) # 1 super user, 2 admin
    
class PaymentType(models.Model):
    id = models.AutoField(primary_key=True)
    paymenttype = models.CharField(max_length = 2)
    paymenttypename = models.CharField(max_length = 20)

class Membership(models.Model):
    id = models.AutoField(primary_key=True)
    vipno = models.CharField(max_length = 11)
    vipname = models.CharField(max_length = 10)
    vipnameid = models.CharField(max_length = 18) #Person ID
    phonenumber = models.CharField(max_length = 11)
    password = models.CharField(max_length = 10)
    amount = models.FloatField()
    lastamount = models.FloatField()
    discounttype = models.CharField(max_length = 20)
    discountrate = models.FloatField()
    discountrate2 = models.FloatField()
    webchatid = models.CharField(max_length = 128)
    webchatid2 = models.CharField(max_length = 128, default = '')
    startDate = models.CharField(max_length=10, default = '0000/01/01')
    endDate = models.CharField(max_length=10, default = '9999/12/31')
    deleteFlag = models.CharField(max_length=10, default = '0') # 0 effective, 1 un-effective
    
    
class MembershipAmountLog(models.Model):
    id = models.AutoField(primary_key=True)
    membershipId = models.CharField(max_length = 10)
    addAmount = models.FloatField()
    username = models.CharField(max_length = 10, default = 'admin')
    transactionDate = models.DateTimeField()
    
class DoctorInfo(models.Model):
    id = models.AutoField(primary_key=True)
    sn = models.CharField(max_length = 6, default = '001')
    doctorname = models.CharField(max_length = 20)
    phonenumber = models.CharField(max_length = 11)
    comments = models.CharField(max_length = 400)
    service = models.CharField(max_length = 200)
    webchatid = models.CharField(max_length = 128)
    rank = models.IntegerField(default=0)
    
class ServiceType(models.Model):
    id = models.AutoField(primary_key=True)
    servicename = models.CharField(max_length = 50)
    servicerate = models.IntegerField()
    serviceperiod = models.IntegerField()

class Product(models.Model):
    id = models.AutoField(primary_key=True)
    productname = models.CharField(max_length = 50)
    productprice = models.FloatField()
    
class ServiceRate(models.Model):
    id = models.AutoField(primary_key=True)
    ratename = models.CharField(max_length = 50)
    rate = models.FloatField()  #discount
    morningdiscount = models.FloatField()
    commnets = models.CharField(max_length = 50)
    nextCardNo = models.IntegerField(default = 100000)
    
class BookingInfo(models.Model):
    id = models.AutoField(primary_key=True)
    phonenumber = models.CharField(max_length = 11)
    name = models.CharField(max_length = 20)
    membercard = models.CharField(max_length = 20)
    bookeddoctor = models.CharField(max_length = 20)
    bookeditem = models.CharField(max_length = 50)
    bookedtime = models.CharField(max_length = 20)
    webchatid = models.CharField(max_length = 128)
    status = models.CharField(max_length = 1) # 0 cancel, 1 new booking, 9 completed
    
class Transaction(models.Model):
    id = models.AutoField(primary_key=True)
    membershipId = models.CharField(max_length = 10)
    doctorId = models.CharField(max_length = 10)
    bookingId = models.CharField(max_length = 10)
    servicetypeId = models.CharField(max_length = 10)
    productIds = models.CharField(default = '', max_length = 50)
    account = models.IntegerField(default = 1)
    paymentType = models.CharField(max_length = 2) #01 cash, 02 membership card, 03 weixin,04 pos, 05 alipay, 00 not decied
    serviceamount = models.FloatField(default = 0)
    productamount = models.FloatField(default = 0)
    amount = models.FloatField(default = 0)
    preamount = models.FloatField(default = 0)
    discount = models.FloatField(default = 1)
    successFlag = models.CharField(max_length = 1) #0 unpayed, 1 payed, 9 membership add amount, 8 deleted
    transactionDate = models.DateField()
    username = models.CharField(max_length = 10, default = 'admin')
    ordertype = models.CharField(default='', max_length=1) # A define somebody, B assigned by shop
    
class Vacation(models.Model):
    id = models.AutoField(primary_key=True) 
    doctorId = models.CharField(max_length = 10)
    doctorName = models.CharField(max_length = 20, default = '')
    vacationDate = models.CharField(max_length = 10)
    starttime = models.CharField(max_length = 8)
    endtime = models.CharField(max_length = 8)
    flag = models.CharField(max_length = 1) #flag=1 vacation, flag=0 cancelled
    comments = models.CharField(max_length = 50)
    
class Messages(models.Model):
    id = models.AutoField(primary_key=True) 
    messageId = models.CharField(max_length = 10)
    message = models.CharField(max_length = 256)
    