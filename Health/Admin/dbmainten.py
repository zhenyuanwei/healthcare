'''
Created on Jul 18, 2016

@author: weizhenyuan
'''
from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.template.loader import get_template
from HealthModel.models import AdminUser, PaymentType, Transaction, Vacation
from HealthModel.models import DoctorInfo
from HealthModel.models import ServiceType
from HealthModel.models import ServiceRate
from HealthModel.models import Membership
from HealthModel.models import MembershipAmountLog
from HealthModel.models import Product
from django.template.context_processors import request
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from datetime import timedelta
from Health.Admin.common import checkSession
from Health.Admin.common import createResponseDic
from Health.Webchat.booking import getDaysList
from Health.Admin.payment import createPayment

timeBJ = 8

def addAdminUser(request):
    admin = AdminUser(username='test1', password = '123456')
    admin.save()
    return HttpResponse('Insert the admin DB OK!')

def goDoctorInfo(request):
    usedTemplate = get_template('admin/doctor.html')
    outDic = createResponseDic(request=request)
    outDic['hightlight'] = '2'
    serviceList = ServiceType.objects.all()
    outDic['serviceList'] = serviceList
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

def goDoctorInfoList(request):
    usedTemplate = get_template('admin/doctorlist.html')
    doctorlist = DoctorInfo.objects.all()
    outDic = createResponseDic(request=request)
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
        outDic = createResponseDic(request=request)
        outDic['hightlight'] = '2'
        outDic['doctorinfo'] = doctor
        
        doctorserviceIds = doctor.service
        serviceList = []
        dbServiceList = ServiceType.objects.all()
        for service in dbServiceList :
            service.checkFlag = checkServiceCan(doctorserviceIds=doctorserviceIds, serviceId=service.id)
            serviceList.append(service)
        outDic['serviceList'] = serviceList
        
        usedTemplate = get_template('admin/doctor.html')
        html = usedTemplate.render(outDic)
        return HttpResponse(html)

def checkServiceCan(doctorserviceIds, serviceId):
    serviceCan = 'False'
    doctorserviceIdList = doctorserviceIds.split(',')
    for tmpId in doctorserviceIdList :
        if str(serviceId) == tmpId :
            serviceCan = 'True'
            break
    return serviceCan

def goServiceType(request):
    outDic = createResponseDic(request=request)
    outDic['hightlight'] = '3'
    usedTemplate = get_template('admin/servicetype.html')
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

def goServiceTypeUpdate(request):
    serviceid = request.GET['id']
    outDic = createResponseDic(request=request)
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
    outDic = createResponseDic(request=request)
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
    
    outDic = createResponseDic(request=request)
    serviceRateList = ServiceRate.objects.all()
    outDic['serviceRateList'] = serviceRateList
    outDic['hightlight'] = '4'
    outDic['flag'] = 'A'
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

def goMembershipList(request):
    outDic = createResponseDic(request=request)
    
    membershiplist = Membership.objects.all()
    outDic['membershipList'] = membershiplist
    
    for membership in membershiplist :
        discoutType = ServiceRate.objects.get(id = membership.discounttype)
        membership.discounttype = discoutType.ratename
    
    outDic['hightlight'] = '4'
    usedTemplate = get_template('admin/membershiplist.html')
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

@csrf_exempt
def membershipListQuery(request):
    outDic = createResponseDic(request=request)
    
    phonenumber = request.POST['phonenumber']
    membershiplist = Membership.objects.all()
    if phonenumber != '' :
        membershiplist = membershiplist.filter(phonenumber = phonenumber)
    outDic['membershipList'] = membershiplist
    
    for membership in membershiplist :
        discoutType = ServiceRate.objects.get(id = membership.discounttype)
        membership.discounttype = discoutType.ratename
    
    outDic['hightlight'] = '4'
    usedTemplate = get_template('admin/membershiplist.html')
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
    discounttype = int(membership.discounttype)
    usedTemplate = get_template('admin/membership.html')
    outDic = createResponseDic(request=request)
    serviceRateList = ServiceRate.objects.all()
    outDic['serviceRateList'] = serviceRateList
    outDic['membership'] = membership
    outDic['discounttype'] = discounttype
    outDic['flag'] = 'U'
    outDic['hightlight'] = '4'
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

def goMembershipDetail(request):
    outDic = createResponseDic(request=request)
    outDic['hightlight'] = '4'
    
    temId = request.GET['id']
    membership = Membership.objects.get(id = temId)
    serviceRate = ServiceRate.objects.get(id = membership.discounttype)
    membership.ratename = serviceRate.ratename
    
    outDic['membership'] = membership
    
    membershipAmountLogList = MembershipAmountLog.objects.all()
    membershipAmountLogList = membershipAmountLogList.filter(membershipId = temId)
    outDic['membershipAmountLogList'] = membershipAmountLogList
    
    transactionList = Transaction.objects.all()
    transactionList = transactionList.filter(membershipId = temId, successFlag = '1')
    paymentList = []
    for transaction in transactionList :
        payment = createPayment(transaction = transaction)
        paymentList.append(payment)
    
    outDic['paymentList'] = paymentList
    
    usedTemplate = get_template('admin/membershipinfo.html')
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

def goMembershipAmountUpdate(request):

    temId = request.GET['id']
    membership = Membership.objects.get(id = temId)
    paymentTypeList = PaymentType.objects.exclude(paymenttype = '02')
    usedTemplate = get_template('admin/membership.html')
    outDic = createResponseDic(request=request)
    outDic['membership'] = membership
    outDic['paymentTypeList'] = paymentTypeList
    outDic['flag'] = 'M'
    outDic['hightlight'] = '4'
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

@csrf_exempt
def doMembership(request):
    try :
        flag = request.POST['operation']
        if flag == 'A' :
            if addMembership(request=request) :
                outDic = createResponseDic(request=request)
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
    except :
        print
    finally :
        return HttpResponseRedirect("../membershiplist/")
    

def addMembership(request):
    #vipno = request.GET['vipno']
    vipname = request.POST['vipname']
    #vipnameid = request.GET['vipnameid']
    vipnameid = ''
    phonenumber = request.POST['phonenumber']
    password = '000000'
    amount = 0
    '''if request.GET['amount'].strip() :
        amount = float(request.GET['amount'])'''
    lastamount = 0
    vipno = ''
    
    discountrateId = request.POST['discountrate']
    discounttype = discountrateId
    discountrate = 0
    discountrate2 = 0
    try :
        discount = ServiceRate.objects.get(id = discountrateId)
        discountrate = discount.rate
        discountrate2 = discount.morningdiscount
        vipno = discount.nextCardNo
    except :
        discountrate = 1
        discountrate2 = 1
        vipno = phonenumber
        
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
        
        #update the next membership id
        discount.nextCardNo = int(vipno) + 1
        discount.save()
    return isMember
    
def updateMembership(request):
    vipid = request.POST['vipid']
    vipname = request.POST['vipname']
    phonenumber = request.POST['phonenumber']
    #vipno = request.POST['vipno']
    vipno = phonenumber
    discountrateId = request.POST['discountrate']
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
    membership.discounttype = discountrateId
    membership.phonenumber = phonenumber
    membership.discountrate = discountrate
    membership.discountrate2 = discountrate2
    membership.save()

def updateMembershipAmount(request):
    vipid = request.POST['vipid']
    amount = 0
    if request.POST['amount'].strip() :
        amount = float(request.POST['amount'])
    
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
    transaction = Transaction()
    transaction.membershipId = membership.id
    transaction.doctorId = ''
    transaction.bookingId = ''
    transaction.servicetypeId = ''
    transaction.productIds = ''
    transaction.paymentType = request.POST['paymenttype']
    transaction.serviceamount = 0
    transaction.productamount = amount
    transaction.amount = amount
    transaction.discount = 1
    transaction.successFlag = '9'
    transaction.transactionDate = today
    transaction.save()
    
def goDiscountRateList(request):
    usedTemplate = get_template('admin/discountlist.html')
    outDic = createResponseDic(request=request)
    serviceRateList = ServiceRate.objects.all()
    outDic['serviceRateList'] = serviceRateList
    outDic['hightlight'] = '7'
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

def goDiscountRate(request):
    usedTemplate = get_template('admin/discount.html')
    outDic = createResponseDic(request=request)
    outDic['hightlight'] = '7'
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

@csrf_exempt
def doDiscountRate(request):
    usedTemplate = get_template('admin/discountlist.html')
    try : 
        discountname = request.POST['discountname']
        discountrate = request.POST['discountrate']
        morningdiscout = request.POST['morningdiscout']
        comments = request.POST['comments']
        nextCardNo = request.POST['nextCardNo']
        actionType = request.POST['actionType']
        if actionType == 'A' :
            discount = ServiceRate()
            discount.ratename = discountname
            discount.rate = discountrate
            discount.morningdiscount = morningdiscout
            discount.commnets = comments
            discount.nextCardNo = nextCardNo
            discount.save()
        elif actionType == 'U' :
            serviceRateId = request.POST['serviceRateId']
            discount = ServiceRate.objects.get(id=serviceRateId)
            discount.ratename = discountname
            discount.rate = discountrate
            discount.morningdiscount = morningdiscout
            discount.commnets = comments
            #discount.nextCardNo = nextCardNo
            discount.save()
    except :
        print '-----------worry--------------'
    outDic = createResponseDic(request=request)
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
    outDic = createResponseDic(request=request)
    serviceRateList = ServiceRate.objects.all()
    outDic['serviceRateList'] = serviceRateList
    outDic['hightlight'] = '7'
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

def goUpdateDiscountRate(request):
    usedTemplate = get_template('admin/discount.html')
    discountId = request.GET['id']
    discout = ServiceRate.objects.get(id=discountId)
    outDic = createResponseDic(request=request)
    outDic['serviceRate'] = discout
    outDic['hightlight'] = '7'
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

def goProductList(request):
    usedTemplate = get_template('admin/productlist.html')
    productList = Product.objects.all()
    outDic = createResponseDic(request=request)
    outDic['hightlight'] = '8'
    outDic['productList'] = productList
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

def goProduct(request):
    usedTemplate = get_template('admin/product.html')
    outDic = createResponseDic(request=request)
    outDic['hightlight'] = '8'
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

@csrf_exempt
def doProduct(request):
    usedTemplate = get_template('admin/productlist.html')
    try :
        productName = request.POST['productname']
        productPrice = request.POST['productprice']
        product = Product()
        product.productname = productName
        product.productprice = productPrice
        product.save()
    except :
        print '-----------worry--------------'
    
    outDic = createResponseDic(request=request)
    outDic['hightlight'] = '8'
    productList = Product.objects.all()
    outDic['productList'] = productList
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

def deleteProduct(request):
    usedTemplate = get_template('admin/productlist.html')
    productId = request.GET['id']
    try :
        product = Product.objects.get(id=productId)
        product.delete()
    except :
        print '------------There is no product to delete'
    
    outDic = createResponseDic(request=request)
    outDic['hightlight'] = '8'
    productList = Product.objects.all()
    outDic['productList'] = productList
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

def goPaymentTypeList(request):
    usedTemplate = get_template('admin/paymenttypelist.html')
    outDic = createResponseDic(request=request)
    paymentTypeList = PaymentType.objects.all()
    outDic['paymentTypeList'] = paymentTypeList
    outDic['hightlight'] = '9'
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

def goPaymentType(request):
    usedTemplate = get_template('admin/paymenttype.html')
    outDic = createResponseDic(request=request)
    outDic['hightlight'] = '9'
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

@csrf_exempt
def doPaymentType(request):
    paymentType = PaymentType()
    paymentType.paymenttype = request.POST['paymenttype']
    paymentType.paymenttypename = request.POST['paymenttypename']
    paymentType.save()
    usedTemplate = get_template('admin/paymenttypelist.html')
    outDic = createResponseDic(request=request)
    outDic['hightlight'] = '9'
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

def goVacatinList(request):
    outDic = createResponseDic(request=request)
    outDic['hightlight'] = '10'
    
    today = (datetime.now() + timedelta(hours=timeBJ)).strftime('%Y/%m/%d')
    vacationList = Vacation.objects.filter(flag='1')
    vacationList = vacationList.filter(vacationDate__gte = today)
    outDic['vacationList'] = vacationList
    
    usedTemplate = get_template('admin/vacationlist.html')
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

def doCancelVacation(request):
    outDic = createResponseDic(request=request)
    outDic['hightlight'] = '10'
    
    id = request.GET['id']
    try :
        vacation = Vacation.objects.get(id = id)
        vacation.flag = '0'
        vacation.save()
        
    except :
        outDic['messages'] = 'ERROR'
        print '------------------------cancel the vacation is fail : id = ' + id
        
    finally:
        return HttpResponseRedirect('../govacationlist/')
    
def goAdminVacatinApplication(request):
    outDic = createResponseDic(request=request)
    outDic['hightlight'] = '10'
    
    dayList = getDaysList(14)
    outDic['dayList'] = dayList
    
    doctorInfoList = DoctorInfo.objects.all()
    outDic['doctorInfoList'] = doctorInfoList
    
    usedTemplate = get_template('admin/vacationapplication.html')
    html = usedTemplate.render(outDic)
    return HttpResponse(html) 

@csrf_exempt
def doAdminVacatinApplication(request):
    outDic = createResponseDic(request=request)
    outDic['hightlight'] = '10'
    
    doctorId = request.POST['doctorId']
    vacationDate  = request.POST['vacationDate']
    starttime = request.POST['starttime']
    endtime = request.POST['endtime']
    doctor = DoctorInfo.objects.get(id = doctorId)
    doctorName = doctor.doctorname
    flag = '1'
    comments = ''
    
    vacation = Vacation()
    vacation.doctorId = doctorId
    vacation.doctorName = doctorName
    vacation.vacationDate = vacationDate
    vacation.starttime = starttime
    vacation.endtime = endtime
    vacation.flag = flag
    vacation.comments = comments
    vacation.save()
    
    return HttpResponseRedirect('../govacationlist/')   
    
