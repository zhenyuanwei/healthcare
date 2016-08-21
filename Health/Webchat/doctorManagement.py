'''
Created on Aug 14, 2016

@author: weizhenyuan
'''
from django.http import HttpResponse
from django.template.loader import get_template
from Health.Webchat.myweixin import getOpenID
from HealthModel.models import DoctorInfo
from Health.Admin.payment import getPaymentList
from datetime import date
def gobindDoctor(request):
    #get webchat user
    openId = '000'
    try :
        code = request.GET['code']
        openId = getOpenID(code=code)
    except :
        openId = '000'
        print '------------this is not from weixin-----------'
    #get webchat user
    
    outDic = {}
    outDic['openId'] = openId
    
    try :
        doctor = DoctorInfo.objects.get(webchatid=openId)
        outDic['doctor'] = doctor
        usedTemplate = get_template('webchat/doctorinfo.html')
        html = usedTemplate.render(outDic)
    except :
        usedTemplate = get_template('webchat/doctorbind.html')
        html = usedTemplate.render(outDic)
    return HttpResponse(html) 

def dobindDoctor(request):
    outDic = {}
    openId = request.GET['openId']
    bindno = request.GET['bindno']
    outDic['openId'] = openId
    outDic['bindno'] = bindno
    
    try :
        print '----------- bindno = ' + bindno
        doctor = DoctorInfo.objects.get(phonenumber=bindno)
        webchatId = doctor.webchatid
        if webchatId == '' :
            doctor.webchatid = openId
            doctor.save()
        else :
            outDic['messages'] = 'BINDED'
            
        outDic['doctor'] = doctor
        usedTemplate = get_template('webchat/doctorinfo.html')
        html = usedTemplate.render(outDic)
        return HttpResponse(html) 
    except :
        outDic['messages'] = 'OK'
        usedTemplate = get_template('webchat/doctorbind.html')
        html = usedTemplate.render(outDic)
        return HttpResponse(html) 

def goDoctorQuery(request):
    #get webchat user
    openId = '000'
    try :
        code = request.GET['code']
        openId = getOpenID(code=code)
    except :
        openId = '000'
        print '------------this is not from weixin-----------'
    #get webchat user
    outDic = {}
    outDic['openId'] = openId
    try :
        doctor = DoctorInfo.objects.get(webchatid=openId)
        doctorId = doctor.id
        today = date.today().strftime('%Y-%m-%d')
        paymentList = getPaymentList(doctorId=doctorId, querydate=today)
        outDic['paymentList'] = paymentList
        usedTemplate = get_template('webchat/doctorpaymentlist.html')
        html = usedTemplate.render(outDic)
    except :
        outDic['messages'] = 'BIND'
        usedTemplate = get_template('webchat/doctorbind.html')
        html = usedTemplate.render(outDic)
    finally:
        return HttpResponse(html) 

    
def goDoctorMonthQuery(request):
    #get webchat user
    openId = '000'
    try :
        code = request.GET['code']
        openId = getOpenID(code=code)
    except :
        openId = '000'
        print '------------this is not from weixin-----------'
    #get webchat user
    outDic = {}
    outDic['openId'] = openId
    try :
        doctor = DoctorInfo.objects.get(webchatid=openId)
        doctorId = doctor.id
        today = date.today()
        year = today.strftime('%Y')
        month = today.strftime('%m')
        paymentList = getPaymentList(doctorId=doctorId, queryyear=year, querymonth=month)
        outDic['paymentList'] = paymentList
        usedTemplate = get_template('webchat/doctorpaymentlist.html')
        html = usedTemplate.render(outDic)
    except :
        outDic['messages'] = 'BIND'
        usedTemplate = get_template('webchat/doctorbind.html')
        html = usedTemplate.render(outDic)
    finally:
        return HttpResponse(html) 
        
