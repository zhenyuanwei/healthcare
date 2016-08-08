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
from datetime import date
from datetime import datetime

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
    outDic['hightlight'] = '5'
    outDic['doctorList'] = doctorList
    outDic['servicetypeList'] = servicetypeList
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

def doPrePayment(request):
    outDic = {}
    outDic['hightlight'] = '5'
    
    paymenttype = request.GET['paymenttype']
    vipno = request.GET['vipno']
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
            membership = Membership.objects.get(vipno=vipno)
            servicediscount = membership.discountrate
            outDic['membership'] = membership
            
        servicerate = service.servicerate
        amount = servicerate * float(servicediscount)
        #amount = int(amount)
    except :
        print '--------there is no membership : vipno = ' + vipno + '------------'
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
        outDic['vipno'] = vipno
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
    today = date.today()
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
    today = str(date.today())
    #today = '2016-08'
    paymentList = getPaymentList(querydate=today)
    outDic['paymentList'] = paymentList
    usedTemplate = get_template('admin/paymentlist.html')
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

def searchPaymentList(request):
    outDic = {}
    outDic['hightlight'] = '6'
    querydate = '2014-09-08'
    paymentList = getPaymentList(querydate=querydate)
    outDic['paymentList'] = paymentList
    usedTemplate = get_template('admin/paymentlist.html')
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

def getPaymentList(querydate, doctorId=''):
    #raw_sql = "select * from health.HealthModel_transaction where 1 = 1 "
    #transactionList = None
    if doctorId == '':
        transactionList = Transaction.objects.filter(transactionDate__startswith=querydate)
    else :
        transactionList = Transaction.objects.filter(transactionDate__startswith=querydate,doctorId=doctorId)
    
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
    paymentList.append(payment)
    return paymentList