'''
Created on Jul 5, 2016

@author: wzy
'''
# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render, render_to_response
from django.template.loader import get_template
from django.template import Context
from HealthModel.models import AdminUser
from HealthModel.models import BookingInfo

"@csrf_exempt"
def login(request):
    usedTemplate = get_template('admin/login.html')
    html = usedTemplate.render()
    return HttpResponse(html)

def doLogin(request):
    
    username1 = request.GET['username']
    password1 = request.GET['password']
    adminUser = AdminUser.objects.filter(username = username1, password = password1)
    if adminUser :
        usedTemplate = get_template('admin/bookinglist.html')
        bookingList = BookingInfo.objects.all().extra(where=["status in ('1')"])
        """bookingList = BookingInfo.objects.all()"""
        bookingListDic = {'bookingList' : bookingList}
        html = usedTemplate.render(bookingListDic)
        return HttpResponse(html)
    else :
        usedTemplate = get_template('admin/login.html')
        messageDic = {'messages' : 'OK'}
        html = usedTemplate.render(messageDic)
        return HttpResponse(html)
        
    
