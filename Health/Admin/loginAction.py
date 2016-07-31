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

"@csrf_exempt"
def login(request):
    usedTemplate = get_template('admin/login.html')
    html = usedTemplate.render()
    return HttpResponse(html)
def bookingList(request):
    usedTemplate = get_template('admin/bookinglist.html')
    tmpList = BookingInfo.objects.all().extra(where=["status in ('1')"])
    bookingList = []
    for bookinginfo in tmpList:
        if bookinginfo.bookeddoctor.strip() != '0' :
            bookinginfo.bookeddoctor = DoctorInfo.objects.get(id=bookinginfo.bookeddoctor).doctorname
        else :
            bookinginfo.bookeddoctor = ''
        
        if bookinginfo.bookeditem.strip() != '0' :
            bookinginfo.bookeditem = ServiceType.objects.get(id=bookinginfo.bookeditem).servicename
        else :
            bookinginfo.bookeditem = ''
        
        bookingList.append(bookinginfo)
    outDic = {}
    outDic['bookingList'] = bookingList
    outDic['hightlight'] = '1'
    html = usedTemplate.render(outDic)
    return HttpResponse(html)
    
def doLogin(request):
    
    username1 = request.GET['username']
    password1 = request.GET['password']
    adminUser = AdminUser.objects.filter(username = username1, password = password1)
    if adminUser :
        return HttpResponseRedirect("../bookinglist/")
    else :
        usedTemplate = get_template('admin/login.html')
        messageDic = {'messages' : 'OK'}
        html = usedTemplate.render(messageDic)
        return HttpResponse(html)
        
    
