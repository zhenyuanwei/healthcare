'''
Created on Aug 6, 2016

@author: weizhenyuan
'''
from django.http import HttpResponse
from django.template.loader import get_template
from django.http import HttpResponseRedirect
from HealthModel.models import DoctorInfo
from HealthModel.models import ServiceType
from HealthModel.models import Membership
from HealthModel.models import Transaction
from HealthModel.models import ServiceRate
from datetime import date
from datetime import datetime
from datetime import timedelta

timeBJ = 8

class Payment :
    id = 0
    paymenttype = ''
    vipname = ''
    vipno = ''
    doctorname = ''
    amount = 0
    servicename = ''
    paymentdate = date.today()

def goPrePayment(request):
    doctorList = DoctorInfo.objects.all()
    servicetypeList = ServiceType.objects.all()
    usedTemplate = get_template('admin/prepayment.html')
    outDic = {}
    serviceRateList = ServiceRate.objects.all()
    outDic['serviceRateList'] = serviceRateList
    outDic['hightlight'] = '5'
    outDic['doctorList'] = doctorList
    outDic['servicetypeList'] = servicetypeList
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

def doPrePayment(request):
    outDic = {}
    outDic['hightlight'] = '5'
    
    paymenttype = request.GET['paymenttype']
    phonenumber = request.GET['phonenumber']
    doctor = request.GET['doctor']
    servicetype = request.GET['servicetype']
    servicerate = request.GET['servicerate']
    servicediscount = request.GET['servicediscount']
    amount = 0
    #calculate the amount start
    try :
        doctorInfo = DoctorInfo.objects.get(id=doctor)
        outDic['doctorInfo'] = doctorInfo
        service = ServiceType.objects.get(id=servicetype)
        outDic['service'] = service
        if paymenttype == '02' :
            membership = Membership.objects.get(phonenumber=phonenumber)
            servicediscount = membership.discountrate
            
            now = datetime.now().strftime('%H')
            if now < 13 :
                servicediscount = membership.discountrate2
                
            outDic['membership'] = membership
            
        servicerate = service.servicerate
        amount = servicerate * float(servicediscount)
        
    except :
        print '--------there is no membership : phonenumber = ' + phonenumber + '------------'
        outDic['isMessage'] = 'OK'
        doctorList = DoctorInfo.objects.all()
        servicetypeList = ServiceType.objects.all()
        outDic['doctorList'] = doctorList
        outDic['servicetypeList'] = servicetypeList
        usedTemplate = get_template('admin/prepayment.html')
        html = usedTemplate.render(outDic)
        return HttpResponse(html)
    finally:
        outDic['amount'] = amount
        outDic['paymenttype'] = paymenttype
        outDic['vipno'] = phonenumber
        outDic['doctor'] = doctor
        outDic['servicetype'] = servicetype
        outDic['servicerate'] = servicerate
        outDic['servicediscount'] = servicediscount
    #calculate the amount end
    
    usedTemplate = get_template('admin/prepaymentresult.html')
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

def doPayment(request):
    outDic = {}
    outDic['hightlight'] = '5'
    
    #save to payment start
    paymenttype = request.GET['paymenttype']
    membershipid = request.GET['membershipid']
    doctor = request.GET['doctor']
    servicetype = request.GET['servicetype']
    servicediscount = request.GET['servicediscount']
    amount = request.GET['amount']
    today = datetime.now() + timedelta(hours=timeBJ)
    isSave = True
    
    try :
        if paymenttype == '02' :
            membership = Membership.objects.get(id=membershipid)
            outDic['membership'] = membership
            membershipAmount = membership.amount
            newamount = membership.amount - float(amount)
            servicediscount = membership.discountrate
            if newamount > 0 :
                membership.lastamount = membershipAmount
                membership.amount = newamount
                membership.save()
            else :
                isSave = False
                print '---------there is no enough money in vip card----------'
        
        if isSave :
            transaction = Transaction()
            transaction.membershipId = membershipid
            transaction.doctorId = doctor
            transaction.servicetypeId = servicetype
            transaction.amount = amount
            transaction.paymentType = paymenttype
            transaction.transactionDate = today
            transaction.save()
            
            doctorinfo = DoctorInfo.objects.get(id=doctor)
            service = ServiceType.objects.get(id=servicetype)
            outDic['doctorInfo'] = doctorinfo
            outDic['service'] = service
        
        else :
            outDic['isMessage'] = 'OK'
        
    finally:
        outDic['paymenttype'] = paymenttype
        outDic['amount'] = amount
        outDic['servicediscount'] = servicediscount
    
    #save to payment end
    
    usedTemplate = get_template('admin/paymentresult.html')
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

def goPaymentList(request):
    outDic = {}
    outDic['hightlight'] = '6'
    
    #query form show
    dayList = []
    tempday = datetime.now()
    for i in range(1, 8) :
        dayList.append((tempday + timedelta(days=-i)).strftime('%Y-%m-%d'))
    outDic['dayList'] = dayList
    doctrList = DoctorInfo.objects.all()
    outDic['doctrList'] = doctrList
    #query form show
        
    today = str(date.today())
    paymentList = getPaymentList(querydate=today)
    outDic['paymentList'] = paymentList
    usedTemplate = get_template('admin/paymentlist.html')
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

def searchPaymentList(request):
    outDic = {}
    outDic['hightlight'] = '6'
    
    #query form show
    dayList = []
    tempday = datetime.now()
    for i in range(1, 8) :
        dayList.append((tempday + timedelta(days=-i)).strftime('%Y-%m-%d'))
    outDic['dayList'] = dayList
    doctrList = DoctorInfo.objects.all()
    outDic['doctrList'] = doctrList
    #query form show
    
    querydate = request.GET['querydate']
    doctorId = request.GET['doctorid']
    paymentList = getPaymentList(querydate=querydate, doctorId=doctorId)
    outDic['paymentList'] = paymentList
    usedTemplate = get_template('admin/paymentlist.html')
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

def getPaymentList(querydate='', doctorId='', queryyear='', querymonth=''):
    transactionList = Transaction.objects.all()
    
    if querydate != '' :
        transactionList = Transaction.objects.filter(transactionDate=querydate)
    
    if queryyear != '' :
        transactionList = Transaction.objects.filter(transactionDate__year=queryyear)
    
    if querymonth != '' :
        transactionList = Transaction.objects.filter(transactionDate__month=querymonth)
    
    if doctorId != '' :
        transactionList = transactionList.filter(doctorId=doctorId)
    
    
    paymentList = []
    totalamount = 0
    for transaction in transactionList :
        payment = Payment()
        payment.id = transaction.id
        payment.paymenttype = transaction.paymentType
        payment.amount = transaction.amount
        totalamount = totalamount + transaction.amount
        payment.paymentdate = transaction.transactionDate
        doctor = DoctorInfo.objects.get(id=transaction.doctorId)
        payment.doctorname = doctor.doctorname
        service = ServiceType.objects.get(id=transaction.servicetypeId)
        payment.servicename = service.servicename
        try :
            membership = Membership.objects.get(id=transaction.membershipId)
            payment.vipname = membership.vipname
            payment.vipno = membership.vipno
        except :
            payment.vipname = ''
            payment.vipno = ''
        paymentList.append(payment)
    
    payment = Payment()
    payment.servicename = 'Total'
    payment.amount = totalamount
    
    summarydate = ''
    if querydate != '' :
        summarydate = datetime.strptime(querydate, '%Y-%m-%d').date
    if queryyear != '' :
        summarydate = queryyear
    if querymonth != '' :
        summarydate = summarydate + '-' +querymonth
        
    payment.paymentdate = summarydate
    paymentList.append(payment)
    return paymentList

def goPaymentSummaryList(request):
    outDic = {}
    outDic['hightlight'] = '6'
    
    #query form show
    yearList = []
    year = datetime.strftime(date.today(), '%Y')
    for i in range(0, 5) :
        yearList.append(int(year) - i)
    outDic['yearList'] = yearList
    doctrList = DoctorInfo.objects.all()
    outDic['doctrList'] = doctrList
    #query form show
        
    #today = str(date.today())
    paymentList = getPaymentList(queryyear=year)
    outDic['paymentList'] = paymentList
    usedTemplate = get_template('admin/paymentsummarylist.html')
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

def searchPaymentSummaryList(request):
    outDic = {}
    outDic['hightlight'] = '6'
    
    #query form show
    yearList = []
    year = datetime.strftime(date.today(), '%Y')
    for i in range(0, 5) :
        yearList.append(int(year) - i)
    outDic['yearList'] = yearList
    doctrList = DoctorInfo.objects.all()
    outDic['doctrList'] = doctrList
    #query form show
        
    queryyear = request.GET['queryyear']
    querymonth = request.GET['querymonth']
    doctorId = request.GET['doctorid']
    paymentList = getPaymentList(queryyear=queryyear, querymonth=querymonth, doctorId=doctorId)
    outDic['paymentList'] = paymentList
    usedTemplate = get_template('admin/paymentsummarylist.html')
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

