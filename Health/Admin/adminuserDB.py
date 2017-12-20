'''
Created on May 22, 2016

@author: wzy
'''
# -*- coding: utf-8 -*-
from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from HealthModel.models import AdminUser
from Health.Admin.common import createResponseDic
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt
from Health.utils import checksession

def addAdminUser(request):
    admin = AdminUser(username='test1', password = '123456')
    admin.save()
    return HttpResponse('Insert the admin DB OK!')

def goChangePassword(request):
    res = checksession(request=request)
    if True != res:
        return res

    outDic = createResponseDic(request=request)
    outDic['hightlight'] = '11'
    usedTemplate = get_template('admin/changepassword.html')
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

@csrf_exempt
def doChangePassword(request):
    res = checksession(request=request)
    if True != res:
        return res

    outDic = createResponseDic(request=request)
    outDic['hightlight'] = '11'
    try :
        userId = request.POST['userId']
        newPassword = request.POST['password']
        adminUser = AdminUser.objects.get(id = userId)
        adminUser.password = newPassword
        adminUser.save()
        outDic['messages'] = 'SUCCESS'
    except :
        outDic['messages'] = 'FAILT' 
        
    usedTemplate = get_template('admin/changepasswordresult.html')
    html = usedTemplate.render(outDic)
    return HttpResponse(html)
