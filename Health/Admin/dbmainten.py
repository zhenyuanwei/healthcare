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
from HealthModel.models import ServiceRate
from HealthModel.models import Membership
from HealthModel.models import MembershipAmountLog
from django.template.context_processors import request
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from datetime import timedelta

timeBJ = 8

def addAdminUser(request):
    admin = AdminUser(username='test1', password = '123456')
    admin.save()
    return HttpResponse('Insert the admin DB OK!')

def goDoctorInfo(request):
    usedTemplate = get_template('admin/doctor.html')
    outDic = {}
    outDic['hightlight'] = '2'
    serviceList = ServiceType.objects.all()
    outDic['serviceList'] = serviceList
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

def goDoctorInfoList(request):
    usedTemplate = get_template('admin/doctorlist.html')
    doctorlist = DoctorInfo.objects.all()
    outDic = {}
    outDic['hightlight'] = '2'
    outDic['doctorList'] = doctorlist
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

def addDoctorInfo(request):
    doctorid = request.GET['doctorid'] 
    docotrName = request.GET['doctorname']
    phoneNumber = request.GET['phonenumber']
    comments = request.GET['comments']
    webchatId = ''
    service = ''
    for key in request.GET.keys() :
        if key[0:7] == 'service' :
            service = service + request.GET[key] + ','
            
    #print service
    
    try :
        if doctorid.strip() == '' :
            doctor = DoctorInfo() # for add doctor
        else :
            # for update doctor
            doctor = DoctorInfo.objects.get(id=doctorid)
            webchatId = doctor.webchatid
            
        doctor.doctorname = docotrName
        doctor.phonenumber = phoneNumber
        doctor.comments = comments
        doctor.webchatid = webchatId
        doctor.service = service
        doctor.save()
    except :
        print '-------there is no doctor id = ' + doctorid + '--------'
        
    finally:
        return goDoctorInfoList(request=request)

def deleteDoctorInfo(request):
    doctorid = request.GET['id']
    try :
        doctor = DoctorInfo.objects.get(id=doctorid)
        doctor.delete()
    except :
        print '------there is no doctor id = ' + doctorid + '----------'
    finally:
        return goDoctorInfoList(request=request)
    
def goUpdateDoctorInfo(request):
    doctorid = request.GET['id']
    try :
        doctor = DoctorInfo.objects.get(id=doctorid)
    except :
        print '------there is no doctor id = ' + doctorid + '----------'
    finally:
        usedTemplate = get_template('admin/doctor.html')
        outDic = {}
        outDic['hightlight'] = '2'
        outDic['doctorinfo'] = doctor
        serviceList = ServiceType.objects.all()
        outDic['serviceList'] = serviceList
        html = usedTemplate.render(outDic)
        return HttpResponse(html)

def goServiceType(request):
    outDic = {}
    outDic['hightlight'] = '3'
    usedTemplate = get_template('admin/servicetype.html')
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

def goServiceTypeUpdate(request):
    serviceid = request.GET['id']
    outDic = {}
    outDic['hightlight'] = '3'
    try :
        service = ServiceType.objects.get(id=serviceid)
        outDic['service'] = service
    except :
        print '------------there is no service type id = ' + serviceid + ' ----------'
    finally:
        usedTemplate = get_template('admin/servicetype.html')
        html = usedTemplate.render(outDic)
        return HttpResponse(html)

def deleteServiceType(request):
    serviceId = request.GET['id']
    try :
        service = ServiceType.objects.get(id=serviceId)
        service.delete()
    except :
        print '------there is no service type id = '  + serviceId + '----------'
    finally:
        return goServiceTypeList(request=request)

def goServiceTypeList(request):
    usedTemplate = get_template('admin/servicetypelist.html')
    serviceList = ServiceType.objects.all()
    outDic = {}
    outDic['hightlight'] = '3'
    outDic['serviceList'] = serviceList
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

def doServiceType(request):
    serviceid = request.GET['serviceid']
    servicename = request.GET['servicename']
    servicerate = request.GET['servicerate']
    serviceperiod = request.GET['serviceperiod']
    try :
        if serviceid.strip() == '' :
            serviceType = ServiceType()
        else :
            serviceType = ServiceType.objects.get(id=serviceid)
        serviceType.servicename = servicename
        serviceType.servicerate = servicerate
        serviceType.serviceperiod = serviceperiod
        serviceType.save()
    except :
        print '------there is no service type id=' + serviceid + '--------'
    finally:
        return goServiceTypeList(request=request)

def goMembership(request):
    usedTemplate = get_template('admin/membership.html')
    
    outDic = {}
    serviceRateList = ServiceRate.objects.all()
    outDic['serviceRateList'] = serviceRateList
    outDic['hightlight'] = '4'
    outDic['flag'] = 'A'
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

def goMembershipList(request):
    membershiplist = Membership.objects.all()
    usedTemplate = get_template('admin/membershiplist.html')
    outDic = {}
    outDic['membershipList'] = membershiplist
    outDic['hightlight'] = '4'
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

def goMembershipDelete(request):
    temId = request.GET['id']
    try :
        membership = Membership.objects.get(id = temId)
        membership.delete()
    except :
        print '---------there is no membership id = '  + temId + '----------'
    finally:   
        return HttpResponseRedirect("../membershiplist/")

def goMembershipUpdate(request):
    temId = request.GET['id']
    membership = Membership.objects.get(id = temId)
    usedTemplate = get_template('admin/membership.html')
    outDic = {}
    serviceRateList = ServiceRate.objects.all()
    outDic['serviceRateList'] = serviceRateList
    outDic['membership'] = membership
    outDic['flag'] = 'U'
    outDic['hightlight'] = '4'
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

def goMembershipAmountUpdate(request):
    temId = request.GET['id']
    membership = Membership.objects.get(id = temId)
    usedTemplate = get_template('admin/membership.html')
    outDic = {}
    outDic['membership'] = membership
    outDic['flag'] = 'M'
    outDic['hightlight'] = '4'
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

def doMembership(request):
    flag = request.GET['operation']
    if flag == 'A' :
        if addMembership(request=request) :
            outDic = {}
            outDic['hightlight'] = '4'
            outDic['isMessages'] = 'OK'
            usedTemplate = get_template('admin/membership.html')
            html = usedTemplate.render(outDic)
            return HttpResponse(html)
    elif flag == 'U' :
        updateMembership(request=request)
    elif flag == 'M' :
        updateMembershipAmount(request=request)
    else :
        addMembership(request=request)
    '''outDic = {}
    outDic['hightlight'] = '4'
    usedTemplate = get_template('admin/success.html')
    html = usedTemplate.render(outDic)
    return HttpResponse(html)'''
    return HttpResponseRedirect("../membershiplist/")
    

def addMembership(request):
    vipno = request.GET['vipno']
    vipname = request.GET['vipname']
    #vipnameid = request.GET['vipnameid']
    vipnameid = ''
    phonenumber = request.GET['phonenumber']
    password = '000000'
    amount = 0
    if request.GET['amount'].strip() :
        amount = float(request.GET['amount'])
    lastamount = 0
    discounttype = ''
    
    discountrateId = request.GET['discountrate']
    discountrate = 0
    discountrate2 = 0
    try :
        discount = ServiceRate.objects.get(id = discountrateId)
        discountrate = discount.rate
        discountrate2 = discount.morningdiscount
    except :
        discountrate = 1
        discountrate2 = 1
        
    webchatid = ''
    
    isMember = False
    tmpMembership = Membership.objects.filter(vipno = vipno)
    if tmpMembership :
        isMember = True
    else :
        membership = Membership()
        membership.vipno = vipno
        membership.vipname = vipname
        membership.vipnameid = vipnameid
        membership.phonenumber = phonenumber
        membership.password = password
        membership.amount = amount
        membership.lastamount = lastamount
        membership.discountrate = discountrate
        membership.discountrate2 = discountrate2
        membership.discounttype = discounttype
        membership.webchatid = webchatid
        membership.save()
    return isMember
    
def updateMembership(request):
    vipid = request.GET['vipid']
    vipname = request.GET['vipname']
    phonenumber = request.GET['phonenumber']
    vipno = request.GET['vipno']
    discountrateId = request.GET['discountrate']
    discountrate = 0
    discountrate2 = 0
    try :
        discount = ServiceRate.objects.get(id = discountrateId)
        discountrate = discount.rate
        discountrate2 = discount.morningdiscount
    except :
        discountrate = 1
        discountrate2 = 1
    
    membership = Membership.objects.get(id = vipid)
    membership.vipname = vipname
    membership.vipno = vipno
    membership.phonenumber = phonenumber
    membership.discountrate = discountrate
    membership.discountrate2 = discountrate2
    membership.save()

def updateMembershipAmount(request):
    vipid = request.GET['vipid']
    amount = 0
    if request.GET['amount'].strip() :
        amount = float(request.GET['amount'])
    
    membership = Membership.objects.get(id = vipid)
    lastamount = membership.amount
    membership.lastamount = lastamount
    membership.amount = lastamount + amount
    membership.save()
    
    today = datetime.now() + timedelta(hours = timeBJ)
    membershipAmountLog = MembershipAmountLog()
    membershipAmountLog.membershipId = vipid
    membershipAmountLog.addAmount = amount
    membershipAmountLog.transactionDate = today
    membershipAmountLog.save()
    
def goDiscountRateList(request):
    usedTemplate = get_template('admin/discountlist.html')
    outDic = {}
    serviceRateList = ServiceRate.objects.all()
    outDic['serviceRateList'] = serviceRateList
    outDic['hightlight'] = '7'
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

def goDiscountRate(request):
    usedTemplate = get_template('admin/discount.html')
    outDic = {}
    outDic['hightlight'] = '7'
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

@csrf_exempt
def doDiscountRate(request):
    usedTemplate = get_template('admin/discountlist.html')
    discountname = request.POST['discountname']
    discountrate = request.POST['discountrate']
    morningdiscout = request.POST['morningdiscout']
    comments = request.POST['comments']
    discount = ServiceRate()
    discount.ratename = discountname
    discount.rate = discountrate
    discount.morningdiscount = morningdiscout
    discount.commnets = comments
    discount.save()
    outDic = {}
    serviceRateList = ServiceRate.objects.all()
    outDic['serviceRateList'] = serviceRateList
    outDic['hightlight'] = '7'
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

def deleteDiscountRate(request):
    usedTemplate = get_template('admin/discountlist.html')
    discountId = request.GET['id']
    discout = ServiceRate.objects.get(id=discountId)
    discout.delete()
    outDic = {}
    serviceRateList = ServiceRate.objects.all()
    outDic['serviceRateList'] = serviceRateList
    outDic['hightlight'] = '7'
    html = usedTemplate.render(outDic)
    return HttpResponse(html)
    
