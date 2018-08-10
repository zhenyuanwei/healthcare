'''
Created on Aug 6, 2016

@author: weizhenyuan
'''
from django.http import HttpResponse
from django.template.loader import get_template
from django.http import HttpResponseRedirect
from django.db import transaction as dbTransaction
from HealthModel.models import DoctorInfo, Product, PaymentType, BookingInfo,\
    AdminUser
from HealthModel.models import ServiceType
from HealthModel.models import Membership
from HealthModel.models import Transaction
from HealthModel.models import ServiceRate
from HealthModel.models import Messages
from datetime import date
from datetime import datetime
from datetime import timedelta
from django.views.decorators.csrf import csrf_exempt
from Health.Admin.common import createResponseDic, getDiscount
from Health.Admin.common import getToday
from Health.Webchat.myweixin import sendMessage
from Health.Admin.common import getMessage
from Health.utils import checksession

timeBJ = 8

class Payment :
    id = 0
    paymenttype = ''
    paymenttypename = ''
    vipname = ''
    vipno = ''
    doctorname = ''
    amount = 0
    servicename = ''
    productname = ''
    paymentdate = date.today()
    bookingId = ''

def goPrePayment(request):
    res = checksession(request=request)
    if True != res:
        return res

    outDic = createResponseDic(request=request)
    outDic['hightlight'] = '5'
    doctorList = DoctorInfo.objects.all()
    outDic['doctorList'] = doctorList
    servicetypeList = ServiceType.objects.all()
    outDic['servicetypeList'] = servicetypeList
    productList = Product.objects.all()
    outDic['productList'] = productList
    #serviceRateList = ServiceRate.objects.all()
    #outDic['serviceRateList'] = serviceRateList
    
    try :
        bookingId = request.GET['id']
        bookingInfo = BookingInfo.objects.get(id = bookingId)
        outDic['bookingInfo'] = bookingInfo
        doctor = DoctorInfo.objects.get(id = bookingInfo.bookeddoctor)
        outDic['doctorname'] = doctor.doctorname
        service = ServiceType.objects.get(id = bookingInfo.bookeditem)
        outDic['servicename'] = service.servicename
    except :
        print '--------there is no booking pay '
    
    usedTemplate = get_template('admin/prepayment.html')
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

@csrf_exempt
def doPrePayment(request):
    res = checksession(request=request)
    if True != res:
        return res

    outDic = createResponseDic(request=request)
    outDic['hightlight'] = '5'
    
    try :
        paymenttype = '00'
        phonenumber = request.POST['phonenumber']
        doctor = request.POST['doctor']
        servicetype = request.POST['servicetype']
        # added by 20180721
        ordertype = request.POST['ordertype']
        # added by 20180721
        #servicerate = request.POST['servicerate']
        #servicediscount = request.POST['servicediscount']
        servicediscount = 1
        membershipId = ''
        amount = 0
        serviceamount = 0
        productamount = 0
        
        #product amount 
        productIds = ''
        productList = []
        for key in request.POST.keys() :
            if key[0:7] == 'product' :
                productId = request.POST[key]
                product = Product.objects.get(id = productId)
                productamount = productamount + product.productprice
                productList.append(product)
                productIds = productIds + request.POST[key] + ','
        outDic['productList'] = productList
        outDic['productamount'] = productamount
        
        if doctor != '0' :
            doctorInfo = DoctorInfo.objects.get(id=doctor)
            outDic['doctorInfo'] = doctorInfo
        
        serviceamount = 0
        if servicetype != '0' :
            service = ServiceType.objects.get(id=servicetype)
            serviceamount = service.servicerate
            outDic['service'] = service
            
        #Membership check
        if phonenumber != '' :
            try :
                membership = Membership.objects.get(phonenumber=phonenumber, deleteFlag = '0')
            except :
                try :
                    membership = Membership.objects.get(vipno=phonenumber, deleteFlag = '0')
                except :
                    membership = None
            if membership != None :
                membershipId = membership.id
                phonenumber = membership.phonenumber
                '''servicediscount = membership.discountrate
                #now = (timedelta(hours=timeBJ) + datetime.now()).strftime('%H')
                now = getToday().strftime('%H')
                if now < '12' :
                    servicediscount = membership.discountrate2'''
                servicediscount = getDiscount(phonenumber = phonenumber)    
                outDic['membership'] = membership
            
        
        amount = serviceamount * float(servicediscount) + productamount
        
        outDic['amount'] = amount
        outDic['paymenttype'] = paymenttype
        outDic['phonenumber'] = phonenumber
        outDic['doctor'] = doctor
        outDic['servicetype'] = servicetype
        outDic['serviceamount'] = serviceamount
        outDic['amount'] = amount
        outDic['servicediscount'] = servicediscount
        today = getToday()
        
        #save to transaction
        bookingId = ''
        try : 
            bookingId = request.POST['bookingId']
            if bookingId == '' :
                raise Exception('for no booking, than can mutil-payment')
            transaction = Transaction.objects.get(bookingId = bookingId, successFlag = '0')
            outDic['transactionId'] = transaction.id
        except :
            transaction = Transaction()
            transaction.membershipId = membershipId
            transaction.bookingId = bookingId
            transaction.doctorId = doctor
            transaction.servicetypeId = servicetype
            transaction.amount = amount
            transaction.productamount = productamount
            transaction.serviceamount = serviceamount
            transaction.productIds = productIds
            transaction.discount = float(servicediscount)
            transaction.paymentType = paymenttype
            transaction.successFlag = '0'
            transaction.transactionDate = today
            transaction.ordertype = ordertype # added by 20180721
            transaction.save()
            outDic['transactionId'] = transaction.id
        
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
        usedTemplate = get_template('admin/prepaymentresult.html')
        html = usedTemplate.render(outDic)
        return HttpResponse(html)

def goPaymentTypeSelect(request):
    res = checksession(request=request)
    if True != res:
        return res

    outDic = createResponseDic(request=request)
    outDic['hightlight'] = '5'
    isMembership = True
    try :
        transactionIds = ''
        for key in request.GET.keys() :
            if key[0:13] == 'transactionId' :
                transactionId = request.GET[key]
                transactionIds = transactionIds + transactionId + ','
                transaction = Transaction.objects.get(id = transactionId)
                if transaction.membershipId == '' :
                    isMembership = False
        outDic['transactionIds'] = transactionIds
    except :
        outDic['messages'] = 'ERROR'
    
    paymentTypeList = PaymentType.objects.all()
    if not isMembership :
        paymentTypeList = paymentTypeList.exclude(paymenttype = '02')
    outDic['paymentTypeList'] = paymentTypeList
    
    usedTemplate = get_template('admin/paymenttypeselect.html')
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

@csrf_exempt
def doPaymentTypeSelect(request):
    res = checksession(request=request)
    if True != res:
        return res

    outDic = createResponseDic(request=request)
    outDic['hightlight'] = '5'
    
    try :
        transactionIds = request.POST['transactionIds'].split(',')
        paymentList = []
        serviceAmount = 0
        prodctAmount = 0
        amount = 0
        paymenttypename = ''
        for transactionId in transactionIds :
            if transactionId != '' :
                transaction = Transaction.objects.get(id = transactionId)
                serviceAmount = serviceAmount + transaction.serviceamount * transaction.discount
                prodctAmount = prodctAmount + transaction.productamount
                amount = amount + transaction.amount
                payment = createPayment(transaction = transaction)
                paymentList.append(payment)
        outDic['paymentList'] = paymentList
        outDic['serviceAmount'] = serviceAmount
        outDic['prodctAmount'] = prodctAmount
        outDic['amount'] = amount
        outDic['transactionIds'] = request.POST['transactionIds']
        try :
            paymenttype = request.POST['paymenttype']
            outDic['paymenttype'] = paymenttype
            paymenttypename = PaymentType.objects.get(paymenttype = paymenttype).paymenttypename
            outDic['paymenttypename'] = paymenttypename
            usedTemplate = get_template('admin/prepaymentlist.html')
            
        except :
            outDic['messages'] = 'NOPAYMENTTYPE'
            paymentTypeList = PaymentType.objects.all()
            outDic['paymentTypeList'] = paymentTypeList
            usedTemplate = get_template('admin/paymenttypeselect.html')
        
    except :
        outDic['messages'] = 'ERROR'
        
    
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

@csrf_exempt
def doPayment(request):
    res = checksession(request=request)
    if True != res:
        return res

    outDic = createResponseDic(request=request)
    outDic['hightlight'] = '5'
    
    try :
        transactionIds = request.POST['transactionIds'].split(',')
        paymentType = request.POST['paymenttype']
        paymentList = []
        serviceAmount = 0
        prodctAmount = 0
        amount = 0
        membershipId = ''
        isSave = True
        #Calculate the total amount
        for transactionId in transactionIds :
            if transactionId != '' :
                transaction = Transaction.objects.get(id = transactionId)
                membershipId = transaction.membershipId
 
                successFlag = transaction.successFlag
                if successFlag != 1 :
                    serviceAmount = serviceAmount + transaction.serviceamount * transaction.discount
                    prodctAmount = prodctAmount + transaction.productamount
                    amount = amount + transaction.amount
        
        #check the member card amount  
        membership = None  
        lastamount = 0
        membershipAmount = 0    
        if paymentType == '02' :
            membership = Membership.objects.get(id = membershipId, deleteFlag = '0')
            lastamount = membership.amount
            membership.lastamount = lastamount
            membershipAmount = lastamount - amount
            '''if membershipAmount >= 0 :
                membership.amount = membershipAmount    
                membership.save()

                if membership.webchatid != '' :
                    sendPaymentLogToWebchat(membership = membership, amount = amount)
                
            else :
                isSave = False
                outDic['messages'] = 'ERROR' '''
            if membershipAmount < 0 :
                isSave = False
                outDic['messages'] = 'ERROR'
        
        #do payment        
        if isSave :
            with dbTransaction.atomic() :
                if paymentType == '02' :
                    membership.amount = membershipAmount    
                    membership.save()
                    if membership.webchatid != '' :
                        sendPaymentLogToWebchat(membership = membership, amount = amount)
                    
                for transactionId in transactionIds :
                    if transactionId != '' :
                        transaction = Transaction.objects.get(id = transactionId)
                        successFlag = transaction.successFlag
                        if successFlag != 1 :
                            username = outDic['username']
                            transaction.paymentType = paymentType
                            transaction.successFlag = '1'
                            transaction.username = username
                            # add for preamount by 2018/02/05
                            transaction.preamount = membershipAmount
                            # add for preamount by 2018/02/05
                            transaction.save()  
                        
                        payment = createPayment(transaction = transaction)
                        paymentList.append(payment)
                        
                        #complete the booking
                        bookingId = transaction.bookingId
                        if bookingId != '' :
                            try :
                                bookingInfo = BookingInfo.objects.get(id = bookingId)
                                bookingInfo.status = '9'
                                bookingInfo.save()
                            except :
                                print '--------the booking info is not exist. Id = ' + bookingId
                            
        outDic['paymentList'] = paymentList
        outDic['serviceAmount'] = serviceAmount
        outDic['prodctAmount'] = prodctAmount
        outDic['amount'] = amount
    except :
        outDic['messages'] = 'FAILT'
    
    usedTemplate = get_template('admin/prepaymentresultlist.html')
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

def sendPaymentLogToWebchat(membership, amount):
    webchatId = membership.webchatid
    textTemplate = get_template('webchat/paymentlog.html')
    textDic = {}
    textDic['Name'] = membership.vipname
    textDic['today'] = getToday().strftime('%Y/%m/%d %H:%M')
    textDic['amount'] = amount
    textDic['membershipAmount'] = membership.amount
    text = textTemplate.render(textDic)
    #print text
    sendMessage(openId = webchatId, text = text)

def createPayment(transaction):
    payment = Payment()
    payment.id = transaction.id
    payment.paymenttype = transaction.paymentType
    payment.amount = transaction.amount
    payment.serviceamount = transaction.serviceamount
    payment.productamount = transaction.productamount
    payment.discount = transaction.discount
    # update the date show style by 2018/02/05
    # payment.paymentdate = transaction.transactionDate
    transactionDate = date.strftime(transaction.transactionDate, '%Y-%m-%d')
    payment.paymentdate = transactionDate
    # update the date show style by 2018/02/05
    payment.bookingId = transaction.bookingId
    payment.successFlag = transaction.successFlag
    payment.username = transaction.username
    # add for preamount by 2018/02/05
    payment.preamount = transaction.preamount
    # add for preamount by 2018/02/05
    payment.ordertype = transaction.ordertype # added by 20180721
    
    try :
        paymentType = PaymentType.objects.get(paymenttype = transaction.paymentType)
        payment.paymenttypename = paymentType.paymenttypename
    except :
        payment.paymenttypename = ''
        
    try :    
        membership = Membership.objects.get(id=transaction.membershipId, deleteFlag = '0')
        payment.vipname = membership.vipname
        payment.vipno = membership.vipno
        payment.isMembership = 'Yes'
        payment.membershiAmount = membership.amount
        payment.membershiId = membership.id
    except :
        payment.vipname = ''
        payment.vipno = ''
        payment.isMembership = 'No'
        payment.membershiAmount = ''
        payment.membershiId = ''
        
    try :    
        doctor = DoctorInfo.objects.get(id=transaction.doctorId)
        payment.doctorId = doctor.id
        payment.doctorname = doctor.doctorname
    except :
        payment.doctorname = ''
        payment.doctorId = ''
        
    try :
        service = ServiceType.objects.get(id=transaction.servicetypeId)
        payment.servicename = service.servicename
        payment.servicetypeId = service.id
    except :
        payment.servicename = ''
        payment.servicetypeId = ''
    
    try :
        productNames = ''
        for productId in transaction.productIds.split(',') :
            if productId != '' :
                product = Product.objects.get(id = productId)
                productNames = productNames + product.productname + ' & '
        productNames = productNames[0:len(productNames) - 3]
        if transaction.successFlag == '9' :
            messages = Messages.objects.get(messageId = 'P00004')
            productNames = messages.message
        payment.productname = productNames
        payment.productIds = transaction.productIds
    except :
        payment.servicename = ''
        payment.productIds = ''
        
    return payment

def goUnpayedList(request):
    res = checksession(request=request)
    if True != res:
        return res

    outDic = createResponseDic(request=request)
    outDic['hightlight'] = '5'
    
    transactionList = Transaction.objects.filter(successFlag = '0')
    paymentList = []
    for transaction in transactionList :
        payment = createPayment(transaction = transaction)
        paymentList.append(payment)
    outDic['paymentList'] = paymentList
    
    usedTemplate = get_template('admin/unpayedlist.html')
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

def goUnpayedCopy(request):
    res = checksession(request=request)
    if True != res:
        return res

    #unpayed copy start 20170217
    paymenttype = '00'
    try :
        transactionId = request.GET['transactionId']
        transaction = Transaction.objects.get(id = transactionId)
        try :
            newTransaction = Transaction()
            newTransaction.membershipId = transaction.membershipId
            newTransaction.bookingId = transaction.bookingId
            newTransaction.doctorId = transaction.doctorId
            newTransaction.servicetypeId = transaction.servicetypeId
            newTransaction.amount = transaction.amount
            newTransaction.productamount = transaction.productamount
            newTransaction.serviceamount = transaction.serviceamount
            newTransaction.productIds = transaction.productIds
            newTransaction.discount = transaction.discount
            newTransaction.ordertype = transaction.ordertype  # added by 20180721
            newTransaction.paymentType = paymenttype
            newTransaction.successFlag = '0'
            newTransaction.transactionDate = getToday()
            newTransaction.save()
        except :
            print 'copy failt transactionId: ' + transactionId
    except :
        print 'there is no transaction record transactionId :' + transactionId
    #unpayed copy end 20170217
    
    return HttpResponseRedirect("../gounpayedlist/")

def doDeleteUnpayed(request):
    res = checksession(request=request)
    if True != res:
        return res

    outDic = createResponseDic(request=request)
    outDic['hightlight'] = '5'
    
    transactionId = request.GET['transactionId']
    try :
        transaction = Transaction.objects.get(id = transactionId)
        transaction.delete()
    except :
        print '----------------the transaction that you want to delete is not exist. Tansaction ID : ' + transactionId
    
    transactionList = Transaction.objects.filter(successFlag = '0')
    paymentList = []
    for transaction in transactionList :
        payment = createPayment(transaction = transaction)
        paymentList.append(payment)
    outDic['paymentList'] = paymentList
    
    usedTemplate = get_template('admin/unpayedlist.html')
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

def goPaymentList(request):
    res = checksession(request=request)
    if True != res:
        return res

    outDic = createResponseDic(request=request)
    outDic['hightlight'] = '6'
    
    #query form show
    dayList = []
    tempday = getToday()
    for i in range(0, 29) :
        dayList.append((tempday + timedelta(days=-i)).strftime('%Y-%m-%d'))
    outDic['dayList'] = dayList
    doctrList = DoctorInfo.objects.all()
    outDic['doctrList'] = doctrList
    #query form show
        
    #today = str(date.today())
    today = tempday.strftime('%Y-%m-%d')
    paymentList = getPaymentList(querydate=today)
    outDic['paymentList'] = paymentList
    usedTemplate = get_template('admin/paymentlist.html')
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

def searchPaymentList(request):
    res = checksession(request=request)
    if True != res:
        return res

    outDic = createResponseDic(request=request)
    outDic['hightlight'] = '6'
    
    #query form show
    dayList = []
    tempday = getToday()
    for i in range(0, 8) :
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

def getPaymentList(querydate='', doctorId='', queryyear='', querymonth='', isSummary=True):
    transactionList = Transaction.objects.all()
    
    if querydate != '' :
        transactionList = transactionList.filter(transactionDate=querydate)
    
    if queryyear != '' :
        transactionList = transactionList.filter(transactionDate__year=queryyear)

    if querymonth != '' :
        transactionList = transactionList.filter(transactionDate__month=querymonth)
    
    if doctorId != '' :
        transactionList = transactionList.filter(doctorId=doctorId)
        
    transactionList = transactionList.exclude(successFlag='0')
    transactionList = transactionList.exclude(successFlag='8')
    
    paymentList = []
    totalamount = 0
    
    #init the payment total by payment type
    paymentTypeList = PaymentType.objects.all()
    paymentTypeTotal = {}
    for paymentType in paymentTypeList :
        paymentTypeTotal[paymentType.paymenttype] = 0
        
    paymentTypeTotal['P00002'] = 0
    paymentTypeTotal['P00003'] = 0
    paymentTypeTotal['P00004'] = 0
    paymentTypeTotal['OrderTypeA'] = 0 # add by 20180721
    paymentTypeTotal['OrderTypeB'] = 0 # add by 20180721
    
    adminUserList = AdminUser.objects.all()
    for adminUser in adminUserList :
        paymentTypeTotal[adminUser.username.upper()] = 0
    #init the payment total by payment type
        
    for transaction in transactionList :
        payment = createPayment(transaction = transaction)
        paymentList.append(payment)
        totalamount = totalamount + transaction.amount
        paymentTypeTotal[transaction.paymentType] = paymentTypeTotal[transaction.paymentType] + transaction.amount
        if transaction.successFlag == '9' :
            paymentTypeTotal['P00004'] = paymentTypeTotal['P00004'] + transaction.productamount
        else :
            paymentTypeTotal['P00002'] = paymentTypeTotal['P00002'] + transaction.productamount
            
        paymentTypeTotal['P00003'] = paymentTypeTotal['P00003'] + transaction.serviceamount * transaction.discount
        
        if transaction.paymentType != '02' and transaction.username <> '' :
            paymentTypeTotal[transaction.username.upper()] = paymentTypeTotal[transaction.username.upper()] + transaction.amount

        # add summary for ordertype 20180721
        if transaction.ordertype == 'A':
            paymentTypeTotal['OrderTypeA'] += transaction.serviceamount * transaction.discount + transaction.productamount
        elif transaction.ordertype == 'B':
            paymentTypeTotal['OrderTypeB'] += transaction.serviceamount * transaction.discount + transaction.productamount
        # add summary for ordertype 20180721
    
    summarydate = ''
    if querydate != '' :
        # update the date show style by 2018/02/05
        # summarydate = datetime.strptime(querydate, '%Y-%m-%d').date
        summarydate = querydate
        # update the date show style by 2018/02/05
    if queryyear != '' :
        summarydate = queryyear
    if querymonth != '' :
        summarydate = summarydate + '-' +querymonth
        
    if isSummary :    
        for paymentType in paymentTypeList :
            payment = Payment()
            payment.id = ''
            payment.servicename = paymentType.paymenttypename
            payment.amount = paymentTypeTotal[paymentType.paymenttype]
            payment.paymentdate = summarydate
            paymentList.append(payment)
            
        payment = Payment()
        message = getMessage(messageId = 'P00001')
        payment.id = ''
        payment.servicename = message
        payment.amount = totalamount
        payment.paymentdate = summarydate
        paymentList.append(payment)
        
        payment = Payment()
        message = getMessage(messageId = 'P00003')
        payment.id = ''
        payment.servicename = message
        payment.amount = paymentTypeTotal['P00003']
        payment.paymentdate = summarydate
        paymentList.append(payment)
        
        payment = Payment()
        message = getMessage(messageId = 'P00002')
        payment.id = ''
        payment.servicename = message
        payment.amount = paymentTypeTotal['P00002']
        payment.paymentdate = summarydate
        paymentList.append(payment)
        
        payment = Payment()
        message = getMessage(messageId = 'P00004')
        payment.id = ''
        payment.servicename = message
        payment.amount = paymentTypeTotal['P00004']
        payment.paymentdate = summarydate
        paymentList.append(payment)

        # add summary for ordertype 20180721
        payment = Payment()
        message = getMessage(messageId='OrderTypeA')
        payment.id = ''
        payment.servicename = message
        payment.amount = paymentTypeTotal['OrderTypeA']
        payment.paymentdate = summarydate
        paymentList.append(payment)

        payment = Payment()
        message = getMessage(messageId='OrderTypeB')
        payment.id = ''
        payment.servicename = message
        payment.amount = paymentTypeTotal['OrderTypeB']
        payment.paymentdate = summarydate
        paymentList.append(payment)
        # add summary for ordertype 20180721
        
        adminUserList = adminUserList.exclude(username = 'wzy')
        for adminUser in adminUserList :
            payment = Payment()
            message = adminUser.username.upper()
            payment.id = ''
            payment.servicename = message
            payment.amount = paymentTypeTotal[message]
            payment.paymentdate = summarydate
            paymentList.append(payment)
            
    
    return paymentList

def goPaymentSummaryList(request):
    res = checksession(request=request)
    if True != res:
        return res

    outDic = createResponseDic(request=request)
    outDic['hightlight'] = '6'
    
    #query form show
    today = getToday()
    yearList = []
    year = datetime.strftime(today, '%Y')
    month = datetime.strftime(today, '%m')

    for i in range(0, 5) :
        yearList.append(int(year) - i)
    outDic['yearList'] = yearList
    doctrList = DoctorInfo.objects.all()
    outDic['doctrList'] = doctrList
    #query form show
        
    #today = str(date.today())
    paymentList = getPaymentList(queryyear=year, querymonth=month)
    outDic['paymentList'] = paymentList
    usedTemplate = get_template('admin/paymentsummarylist.html')
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

def searchPaymentSummaryList(request):
    res = checksession(request=request)
    if True != res:
        return res

    outDic = createResponseDic(request=request)
    outDic['hightlight'] = '6'
    
    #query form show
    yearList = []
    year = getToday().strftime('%Y')
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

@csrf_exempt
def goAccounting(request):
    res = checksession(request=request)
    if True != res:
        return res

    outDic = createResponseDic(request=request)
    outDic['hightlight'] = '6'
    
    yearStart = getToday().strftime('%Y')
    yearList = [yearStart]
    for i in range(1, 3) :
        yearList.append(int(yearStart) - i)
    outDic['yearList'] = yearList
    
    monthList = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    outDic['monthList'] = monthList
    currentMonth = getToday().strftime('%m')
    outDic['currentMonth'] = currentMonth
    
    try :
        year = request.POST['queryyear']
        month = request.POST['querymonth']
        #day = '01'
    except :
        today = getToday()
        year = datetime.strftime(today, '%Y')
        month = datetime.strftime(today, '%m')
        #day = datetime.strftime(today, '%d')
    
    #today = datetime.now() + timedelta(hours=timeBJ)
    doctorMonthProduct = {}
    doctorMonthService = {}
    doctorDayProduct = {}
    doctorDayService = {}
    
    
    
    doctorList = DoctorInfo.objects.all()
    for doctor in doctorList :
        doctorMonthService[doctor.id] = 0
        doctorMonthProduct[doctor.id] = 0
        doctorDayService[doctor.id] = 0
        doctorDayProduct[doctor.id] = 0
        
    paymentList = getPaymentList(queryyear=year, querymonth=month, isSummary=False)    
    for payment in paymentList :
        if payment.doctorId != '' :
            doctorMonthService[payment.doctorId] = doctorMonthService[payment.doctorId] + payment.serviceamount * payment.discount
            doctorMonthProduct[payment.doctorId] = doctorMonthProduct[payment.doctorId] + payment.productamount
            
    '''paymentList = getPaymentList(querydate=today.strftime('%Y-%m-%d'), isSummary=False)    
    for payment in paymentList :
        if payment.doctorId != '' :
            doctorDayService[payment.doctorId] = doctorDayService[payment.doctorId] + payment.serviceamount * payment.discount
            doctorDayProduct[payment.doctorId] = doctorDayProduct[payment.doctorId] + payment.productamount'''

    doctorPaymentList = []
    for doctor in doctorList :
        payment = Payment()
        payment.paymenttypename = doctor.doctorname
        '''payment.dayserviceamount = doctorDayService[doctor.id]
        payment.dayproductamount = doctorDayProduct[doctor.id]'''
        payment.monthserviceamount = doctorMonthService[doctor.id]
        payment.monthproductamount = doctorMonthProduct[doctor.id]
        
        doctorPaymentList.append(payment)
    
        
    outDic['doctorPaymentList'] = doctorPaymentList
    #outDic['day'] = day
    outDic['month'] = month 
    outDic['year'] = year 
    usedTemplate = get_template('admin/accounting.html')
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

def deletePayment(request):
    res = checksession(request=request)
    if True != res:
        return res

    id = request.GET['id']
    operation = request.GET['type']
    try :
        transaction = Transaction.objects.get(id = id)
        transaction.delete()
    except :
        print '-------------there is no transaction id = ' + id
        
    finally: 
        if operation == 'Summary' :
            return HttpResponseRedirect('../summaryquery/')
        else :
            return HttpResponseRedirect('../gopaymentlist/')
    
def cancelPayment(request):
    res = checksession(request=request)
    if True != res:
        return res

    id = request.GET['id']
    try :
        transaction = Transaction.objects.get(id = id)
        successFlag = transaction.successFlag
        with dbTransaction.atomic() :
            if successFlag == '1' :
                transaction.successFlag = '8'
                transaction.save()
                
                membershipId = transaction.membershipId
                if membershipId != '' :
                    amount = transaction.amount
                    membership = Membership.objects.get(id = membershipId, deleteFlag = '0')
                    membership.amount = membership.amount + amount
                    membership.save()
                
                bookingId = transaction.bookingId
                if bookingId != '' :
                    bookingInfo = BookingInfo.objects.get(id = bookingId)
                    bookingInfo.status = '1'
                    bookingInfo.save()
         
    except :
        print '-------------there is no transaction id = ' + id
        
    finally: 
        return HttpResponseRedirect('../gopaymentlist/')


@csrf_exempt
def bookedSummary(request):
    res = checksession(request=request)
    if True != res:
        return res

    outDic = createResponseDic(request=request)
    outDic['hightlight'] = '6'

    yearStart = getToday().strftime('%Y')
    yearList = [yearStart]
    for i in range(1, 3):
        yearList.append(int(yearStart) - i)
    outDic['yearList'] = yearList

    today = getToday()
    currentMonth = today.strftime('%m')

    monthList = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    outDic['monthList'] = monthList

    try:
        year = request.POST['queryyear']
        month = request.POST['querymonth']
        # day = '01'
    except:
        year = datetime.strftime(today, '%Y')
        month = datetime.strftime(today, '%m')

    # calculate the summary the booked or defined by doctor by product
    doctors_summary = {}
    paymentList = getPaymentList(queryyear=year, querymonth=month, isSummary=False)
    for payment in paymentList:
        doctorId = payment.doctorId
        if doctors_summary.has_key(doctorId):
            doctor_summary = doctors_summary[doctorId]
        else:
            doctor_summary = {}
            doctor_summary['doctorname'] = payment.doctorname
            doctors_summary[doctorId] = doctor_summary
        servicetypeId = payment.servicetypeId
        if doctor_summary.has_key(servicetypeId):
            servicetypeContents = doctor_summary[servicetypeId]
        else:
            servicetypeContents = {}
            servicetypeContents['servicename'] = payment.servicename
            servicetypeContents['OrderTypeA'] = 0
            servicetypeContents['OrderTypeB'] = 0
            doctor_summary[servicetypeId] = servicetypeContents
        if payment.ordertype == 'A':
            servicetypeContents['OrderTypeA'] += payment.serviceamount * payment.discount
        elif payment.ordertype == 'B':
            servicetypeContents['OrderTypeB'] += payment.serviceamount * payment.discount
    outDic['doctors_summary'] = doctors_summary
    # print(doctors_summary)

    outDic['currentMonth'] = currentMonth
    outDic['month'] = month
    outDic['year'] = year
    usedTemplate = get_template('admin/bookedsummary.html')
    html = usedTemplate.render(outDic)
    return HttpResponse(html)
