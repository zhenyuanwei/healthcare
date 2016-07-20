'''
Created on Jul 18, 2016

@author: weizhenyuan
'''
from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.template.loader import get_template
from HealthModel.models import AdminUser
from HealthModel.models import DoctorInfo
from HealthModel.models import ServiceType
from HealthModel.models import DoctorServiceType
from HealthModel.models import Membership
from django.template.context_processors import request


def addAdminUser(request):
    admin = AdminUser(username='test1', password = '123456')
    admin.save()
    return HttpResponse('Insert the admin DB OK!')

def goDoctorInfo(request):
    usedTemplate = get_template('admin/doctor.html')
    html = usedTemplate.render()
    return HttpResponse(html)

def addDoctorInfo(request):
    docotrName = request.GET['doctorname']
    phoneNumber = request.GET['phonenumber']
    webchatId = request.GET['webchatid']
    doctor = DoctorInfo()
    doctor.doctorname = docotrName
    doctor.phonenumber = phoneNumber
    doctor.webchatid = webchatId
    doctor.save()
    usedTemplate = get_template('admin/success.html')
    html = usedTemplate.render()
    return HttpResponse(html)

def goServiceType(request):
    usedTemplate = get_template('admin/servicetype.html')
    html = usedTemplate.render()
    return HttpResponse(html)

def doServiceType(request):
    servicename = request.GET['servicename']
    servicerate = request.GET['servicerate']
    serviceType = ServiceType()
    serviceType.servicename = servicename
    serviceType.servicerate = servicerate
    serviceType.save()
    usedTemplate = get_template('admin/success.html')
    html = usedTemplate.render()
    return HttpResponse(html)

def goMembership(request):
    usedTemplate = get_template('admin/membership.html')
    html = usedTemplate.render()
    return HttpResponse(html)

def doMembership(request):
    vipno = request.GET['vipno']
    vipname = request.GET['vipname']
    phonenumber = request.GET['phonenumber']
    password = '000000'
    amount = 0
    lastamount = 0
    discounttype = ''
    discountrate = request.GET['discountrate']
    webchatid = ''
    usedTemplate = get_template('admin/success.html')
    membership = Membership()
    membership.vipno = vipno
    membership.vipname = vipname
    membership.phonenumber = phonenumber
    membership.password = password
    membership.amount = amount
    membership.lastamount = lastamount
    membership.discountrate = discountrate
    membership.discounttype = discounttype
    membership.webchatid = webchatid
    membership.save()
    html = usedTemplate.render()
    return HttpResponse(html)
    