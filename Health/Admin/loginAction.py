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
            tmpStr = ''
            try :
                tmpStr = DoctorInfo.objects.get(id=bookinginfo.bookeddoctor).doctorname
            except :
                print '-------there is no doctor' + bookinginfo.bookeddoctor + '----------'
            finally:
                bookinginfo.bookeddoctor = tmpStr
        else :
            bookinginfo.bookeddoctor = ''
        
        if bookinginfo.bookeditem.strip() != '0' :
            tmpStr = ''
            try :
                tmpStr = ServiceType.objects.get(id=bookinginfo.bookeditem).servicename
            except :
                print '-------there is no service type' + bookinginfo.bookeditem + '----------'
            finally:
                bookinginfo.bookeditem = tmpStr
        else :
            bookinginfo.bookeditem = ''
        
        bookingList.append(bookinginfo)
    outDic = {}
    outDic['bookingList'] = bookingList
    outDic['hightlight'] = '1'
    html = usedTemplate.render(outDic)
    return HttpResponse(html)
    
def doLogin(request):
    username = request.GET['username']
    password = request.GET['password']
    
    try :
        adminUser = AdminUser.objects.get(username = username, password = password)
        request.session['username'] = username
        request.session['role'] = adminUser.role
        return HttpResponseRedirect("../bookinglist/")
    except :
        usedTemplate = get_template('admin/login.html')
        messageDic = {'messages' : 'OK'}
        html = usedTemplate.render(messageDic)
        return HttpResponse(html)
        
        
    
