'''
Created on Aug 6, 2016

@author: weizhenyuan
'''
from django.http import HttpResponse
from django.template.loader import get_template
from django.http import HttpResponseRedirect
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
    outDic = createResponseDic(request=request)
    outDic['hightlight'] = '5'
    
    try :
        paymenttype = '00'
        phonenumber = request.POST['phonenumber']
        doctor = request.POST['doctor']
        servicetype = request.POST['servicetype']
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
        if paymentType == '02' :
            membership = Membership.objects.get(id = membershipId, deleteFlag = '0')
            lastamount = membership.amount
            membership.lastamount = lastamount
            membershipAmount = lastamount - amount
            if membershipAmount >= 0 :
                membership.amount = membershipAmount    
                membership.save()

                if membership.webchatid != '' :
                    sendPaymentLogToWebchat(membership = membership, amount = amount)
                
            else :
                isSave = False
                outDic['messages'] = 'ERROR'
        
        #do payment        
        if isSave :
            for transactionId in transactionIds :
                if transactionId != '' :
                    transaction = Transaction.objects.get(id = transactionId)
                    successFlag = transaction.successFlag
                    if successFlag != 1 :
                        username = outDic['username']
                        transaction.paymentType = paymentType
                        transaction.successFlag = '1'
                        transaction.username = username
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
    payment.paymentdate = transaction.transactionDate
    payment.bookingId = transaction.bookingId
    payment.successFlag = transaction.successFlag
    payment.username = transaction.username
    
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

def doDeleteUnpayed(request):
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
        
    #today = str(date.today())
    today = tempday.strftime('%Y-%m-%d')
    paymentList = getPaymentList(querydate=today)
    outDic['paymentList'] = paymentList
    usedTemplate = get_template('admin/paymentlist.html')
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

def searchPaymentList(request):
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
        transactionList = Transaction.objects.filter(transactionDate=querydate)
    
    if queryyear != '' :
        transactionList = Transaction.objects.filter(transactionDate__year=queryyear)
    
    if querymonth != '' :
        transactionList = Transaction.objects.filter(transactionDate__month=querymonth)
    
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
    
    summarydate = ''
    if querydate != '' :
        summarydate = datetime.strptime(querydate, '%Y-%m-%d').date
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

def goAccounting(request):
    outDic = createResponseDic(request=request)
    outDic['hightlight'] = '6'
    
    #today = datetime.now() + timedelta(hours=timeBJ)
    doctorMonthProduct = {}
    doctorMonthService = {}
    doctorDayProduct = {}
    doctorDayService = {}
    today = getToday()
    year = datetime.strftime(today, '%Y')
    month = datetime.strftime(today, '%m')
    day = datetime.strftime(today, '%d')
    
    
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
            
    paymentList = getPaymentList(querydate=today.strftime('%Y-%m-%d'), isSummary=False)    
    for payment in paymentList :
        if payment.doctorId != '' :
            doctorDayService[payment.doctorId] = doctorDayService[payment.doctorId] + payment.serviceamount * payment.discount
            doctorDayProduct[payment.doctorId] = doctorDayProduct[payment.doctorId] + payment.productamount

    doctorPaymentList = []
    for doctor in doctorList :
        payment = Payment()
        payment.paymenttypename = doctor.doctorname
        payment.dayserviceamount = doctorDayService[doctor.id]
        payment.dayproductamount = doctorDayProduct[doctor.id]
        payment.monthserviceamount = doctorMonthService[doctor.id]
        payment.monthproductamount = doctorMonthProduct[doctor.id]
        
        doctorPaymentList.append(payment)
    
        
    outDic['doctorPaymentList'] = doctorPaymentList
    outDic['day'] = day
    outDic['month'] = month  
    usedTemplate = get_template('admin/accounting.html')
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

def deletePayment(request):
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
    id = request.GET['id']
    try :
        transaction = Transaction.objects.get(id = id)
        successFlag = transaction.successFlag
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
