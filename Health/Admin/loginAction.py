'''
Created on Jul 5, 2016

@author: wzy
'''
# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render, render_to_response
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponseRedirect
from HealthModel.models import AdminUser
from HealthModel.models import BookingInfo
from HealthModel.models import DoctorInfo
from HealthModel.models import ServiceType
from Health.Webchat.booking import getBookingList
from Health.Admin.common import createResponseDic

"@csrf_exempt"
def login(request):
    usedTemplate = get_template('admin/login.html')
    html = usedTemplate.render()
    return HttpResponse(html)

def bookingList(request):
    usedTemplate = get_template('admin/bookinglist.html')
    bookingList = getBookingList()
    outDic = createResponseDic(request=request)
    outDic['bookingList'] = bookingList
    outDic['hightlight'] = '1'
    html = usedTemplate.render(outDic)
    return HttpResponse(html)
    
def doLogin(request):
    username = request.GET['username']
    password = request.GET['password']
    explorer = request.GET['explorer']
    
    try :
        adminUser = AdminUser.objects.get(username = username, password = password)
        request.session['userId'] = adminUser.id
        request.session['username'] = username
        request.session['role'] = adminUser.role
        request.session['explorer'] = explorer
        return HttpResponseRedirect("../bookinglist/")
    except :
        usedTemplate = get_template('admin/login.html')
        outDic = {}
        outDic['messages'] = 'OK'
        html = usedTemplate.render(outDic)
        return HttpResponse(html)
        
        
    
