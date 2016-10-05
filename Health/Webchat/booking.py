'''
Created on May 22, 2016

@author: wzy
'''
# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.template.loader import get_template
from HealthModel.models import BookingInfo, Vacation
from Health.formatValidation import phoneNumberCheck
from Health.formatValidation import required
from HealthModel.models import DoctorInfo
from HealthModel.models import ServiceType
import datetime
from Health.Webchat.myweixin import getOpenID
from membershipmanage import getMembership
from HealthModel.models import Membership
from HealthModel.models import Transaction
from django.http import HttpResponseRedirect
from Health.Admin.common import createResponseDic

"@csrf_exempt"
timeBJ = 8
starttime = 7
endtime = 22
canceltime = timeBJ + 1
#booking time scale
bookingscale = 15
multiscale = 60 / bookingscale

def getBookingList():
    tmpList = BookingInfo.objects.all()
    tmpList = tmpList.filter(status='1')
    tmpList = tmpList.order_by('bookedtime')
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
    
    return bookingList

def booking_form(request):
    #get webchat user
    openId = '000'
    try :
        code = request.GET['code']
        openId = getOpenID(code=code)
    except :
        openId = '000'
        print '------------this user is not binded-----------'
        
    #get webchat user
    listDic = initForm(openId=openId)
    
    usedTemplate = get_template('webchat/booking_form.html')
    html = usedTemplate.render(listDic)
    return HttpResponse(html)

def initForm(openId='', doctorservice = '', doctorId='', queryDate='', selectedServiceId=''):
    
    
    try :
        doctorInfoList = DoctorInfo.objects.all()
        if doctorId == '' and doctorservice == '' :
            doctor = doctorInfoList[0]
            doctorId = doctor.id
            doctorservice = doctor.service
        serviceTypeList = getServiceList(doctorservice=doctorservice)
        if selectedServiceId == '' :
            selectedServiceId = serviceTypeList[0].id
        
        selectedService = ServiceType.objects.get(id=selectedServiceId)
        # delete how many bookingscale
        backCount = int((selectedService.serviceperiod -1) / bookingscale)
        
        dayList = getDaysList()
        if queryDate == '' :
            queryDate = dayList[0]
        timeList = getTimeList(doctorId=doctorId, queryDate=queryDate, backCount=backCount)
    
        
        vipno = ''
        vipname = ''
        phonenumber = ''
        
        membership = getMembership(openId=openId)
        vipno = membership.vipno
        vipname = membership.vipname
        phonenumber = membership.phonenumber
    except :
        vipno = ''
        vipname = ''
        phonenumber = ''
    
    listDic = {'doctorInfoList' : doctorInfoList, 
               'serviceTypeList' : serviceTypeList, 
               'dayList' : dayList,
               'vipno' : vipno,
               'vipname' : vipname,
               'phonenumber' : phonenumber,
               'openId' : openId,
               'timeList' : timeList}
    return listDic

def getDaysList(length = 7):
    dayList = []
    today = datetime.datetime.now()
    now = int(today.strftime('%H')) + timeBJ + 1
    if now >= endtime :
        for i in range(1, length + 1):
            dayList.append((today + datetime.timedelta(days=i)).strftime('%Y/%m/%d'))
    else :
        for i in range(0, length):
            dayList.append((today + datetime.timedelta(days=i)).strftime('%Y/%m/%d'))
        
    return dayList

def getTimeList(doctorId = '', queryDate = '', backCount = 0):
    timeList = []
    today = datetime.datetime.now().strftime('%Y/%m/%d')
    now = int(datetime.datetime.now().strftime('%H')) + timeBJ + 1
    if now < starttime :
        now = starttime
        
    if now >= endtime :
        now = starttime
        
    if doctorId == '' :
        for i in range(now, endtime):
            timeList.append(getTime(value=i))
            
    elif queryDate <> '' :
        if today < queryDate :
            now = starttime
            
        bookingList = BookingInfo.objects.filter(bookeddoctor = doctorId)
        bookingList = bookingList.filter(status = '1')
        bookingList = bookingList.filter(bookedtime__startswith = queryDate)
        
        vacationList = Vacation.objects.filter(doctorId = doctorId)
        vacationList = vacationList.filter(flag = '1')
        vacationList = vacationList.filter(vacationDate = queryDate)

        i = 0
        while (i < (endtime - now) * multiscale):
            time = getTime(value=i, now=now)
            addflag = True
            breakcount = 0
            #check booking for avoiding double booking
            for booking in bookingList :
                bookedtime = booking.bookedtime.split(' ')[1]
                serviceId = booking.bookeditem
                serviceperiod = 0
                try :
                    service = ServiceType.objects.get(id=serviceId)
                    serviceperiod = service.serviceperiod
                except :
                    serviceperiod = 0
                    
                if bookedtime == time :
                    addflag = False
                    
                    # delete the time scale for enough time to do selected service before the next booking
                    count = len(timeList)
                    if count < backCount :
                        backCount = count
                    for j in range(0, backCount) :
                        del timeList[count - j -1]
                    # delete the time scale for enough time to do selected service before the next booking
                        
                    breakcount = int((serviceperiod - 1) / bookingscale)
                    break
            #check booking for avoiding double booking
            
            #check doctor vacation to avoid booking in vacation period 
            for vacation in vacationList :
                vacationStartTime = vacation.starttime
                vacationEndTime = vacation.endtime
                if time == vacationStartTime :
                    count = len(timeList)
                    if count < backCount :
                        backCount = count
                    for j in range(0, backCount) :
                        del timeList[count - j -1]
                        
                if time >= vacationStartTime and time <= vacationEndTime :
                    addflag = False
                    break
            #check doctor vacation to avoid booking in vacation period
            
            if addflag :
                timeList.append(time)

            i = i + 1 + breakcount
    
    return timeList

def getTime(value, now):
    time = ''
    hours = now + int(value / multiscale)
    minutes = (value % multiscale) * bookingscale
    minutes_str = ''
    if minutes == 0 :
        minutes_str = '00'
    else :
        minutes_str = str(minutes)
        
    if hours < 10 :
        time = '0' + str(hours) + ':' + minutes_str
    else :
        time = str(hours) + ':' + minutes_str
    return time
    
def getServiceList(doctorservice = ''):
    if doctorservice == '' :
        serviceTypeList = ServiceType.objects.all()
    else :
        serviceTypeList = []
        services = doctorservice.split(',')
        for serviceId in services :
            try :
                service = ServiceType.objects.get(id=serviceId)
                serviceTypeList.append(service)
            except :
                print '----------------------there is no service =' + serviceId
                
    return serviceTypeList

def booking(request):
    name = request.GET['name']
    phonenumber = request.GET['phonenumber']
    #membercard = request.GET['membercard']
    membercard = phonenumber
    bookeddoctor = request.GET['bookeddoctor']
    bookeditem = request.GET['bookeditem']
    bookedtime = request.GET['bookeddate'] + ' ' + request.GET['bookedhour']
    openId = request.GET['openId']
    
    checkFlag = True;
    if not required(name) :
        checkFlag = False
        
    if not required(phonenumber) :
        checkFlag = False
    elif not phoneNumberCheck(phonenumber) :
        checkFlag = False
        
    if not required(bookedtime) :
        checkFlag = False
    
    #check booking
    checkDBFlag = False
    tempBookingList = BookingInfo.objects.filter(webchatid=openId, status='1')
    '''if tempBookingList :
        checkDBFlag = True'''

    if checkFlag :
        if checkDBFlag :
            tempBooking = tempBookingList.get()
            outputDic = {}
            outputDic['name'] = tempBooking.name
            outputDic['phonenumber'] = tempBooking.phonenumber
            outputDic['membercard'] = tempBooking.membercard
            outputDic['bookedtime'] = tempBooking.bookedtime
            
            if tempBooking.bookeddoctor.strip() == '0' :
                outputDic['bookeddoctor'] = ''
            else :
                outputDic['bookeddoctor'] = DoctorInfo.objects.get(id=tempBooking.bookeddoctor.strip()).doctorname
                
            if tempBooking.bookeditem.strip() == '0' :
                outputDic['bookeditem'] = '' 
            else :
                outputDic['bookeditem'] = ServiceType.objects.get(id=tempBooking.bookeditem.strip()).servicename
            
            outputDic['isMessage'] = 'OK'
            #cancel link show checked    
            cancelFlag = getCancelFlag(bookedtime=tempBooking.bookedtime)
            outputDic['cancelFlag'] = cancelFlag
            print '-------------------------------' + cancelFlag
            usedTemplate = get_template('webchat/booking.html')
            html = usedTemplate.render(outputDic)
            return HttpResponse(html) 
        else :
            bookingInfo = BookingInfo()
            bookingInfo.name = name
            bookingInfo.phonenumber = phonenumber
            bookingInfo.membercard = membercard
            bookingInfo.bookeddoctor = bookeddoctor
            bookingInfo.bookeditem = bookeditem
            bookingInfo.bookedtime = bookedtime
            bookingInfo.webchatid = openId
            bookingInfo.status = '1'
            bookingInfo.save()
            '''return to next page'''
            usedTemplate = get_template('webchat/booking.html')
            outputDic = {}
            outputDic['name'] = name
            outputDic['phonenumber'] = phonenumber
            outputDic['membercard'] = membercard
            outputDic['bookedtime'] = bookedtime
            outputDic['bookingId'] = bookingInfo.id
            outputDic['openId'] = openId
            
            #cancel link show checked    
            cancelFlag = getCancelFlag(bookedtime=bookedtime)
            outputDic['cancelFlag'] = cancelFlag
            
            if request.GET['bookeddoctor'].strip() == '0' :
                outputDic['bookeddoctor'] = ''
            else :
                outputDic['bookeddoctor'] = DoctorInfo.objects.get(id=bookeddoctor).doctorname
                
            if request.GET['bookeditem'].strip() == '0' :
                outputDic['bookeditem'] = '' 
            else :
                outputDic['bookeditem'] = ServiceType.objects.get(id=bookeditem).servicename
            html = usedTemplate.render(outputDic)
            return HttpResponse(html)
    else :
        #messageDic = {'messages' : 'OK'}
        listDic = initForm(openId=openId)
        listDic['messages'] = 'OK'
        usedTemplate = get_template('webchat/booking_form.html')
        html = usedTemplate.render(listDic)
        return HttpResponse(html)
    
def adminRefershDoctor(request):
    vipname = request.GET['name']
    phonenumber = request.GET['phonenumber']
    #vipno = request.GET['membercard']
    vipno = phonenumber
    bookeddoctor = request.GET['bookeddoctor']
    bookeditem = request.GET['bookeditem']
    bookeddate = request.GET['bookeddate']
    #bookedtime = request.GET['bookedhour']
    openId = request.GET['openId']
    try :
        doctor = DoctorInfo.objects.get(id=bookeddoctor)
        doctorservice = doctor.service
    except :
        doctorservice = ''
        print '----------- there is no doctor selected -----------'
        
    outDicForm = initForm(openId=openId, doctorservice=doctorservice, doctorId=bookeddoctor, queryDate=bookeddate, selectedServiceId=bookeditem)
    outDic = dict(createResponseDic(request).items() + outDicForm.items())
    outDic['vipname'] = vipname
    outDic['openId'] = openId
    outDic['phonenumber'] = phonenumber
    outDic['vipno'] = vipno
    outDic['bookeddoctor'] = int(bookeddoctor)
    outDic['bookeditem'] = int(bookeditem)
    outDic['bookeddate'] = bookeddate
    
    usedTemplate = get_template('admin/booking_form.html')
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

def refershDoctor(request):
    vipname = request.GET['name']
    phonenumber = request.GET['phonenumber']
    #vipno = request.GET['membercard']
    vipno = phonenumber
    bookeddoctor = request.GET['bookeddoctor']
    bookeditem = request.GET['bookeditem']
    bookeddate = request.GET['bookeddate']
    #bookedtime = request.GET['bookedhour']
    openId = request.GET['openId']
    try :
        doctor = DoctorInfo.objects.get(id=bookeddoctor)
        doctorservice = doctor.service
    except :
        doctorservice = ''
        print '----------- there is no doctor selected -----------'
        
    outDic = initForm(openId=openId, doctorservice=doctorservice, doctorId=bookeddoctor, queryDate=bookeddate, selectedServiceId=bookeditem)
    
    outDic['vipname'] = vipname
    outDic['openId'] = openId
    outDic['phonenumber'] = phonenumber
    outDic['vipno'] = vipno
    outDic['bookeddoctor'] = int(bookeddoctor)
    outDic['bookeditem'] = int(bookeditem)
    outDic['bookeddate'] = bookeddate
    
    usedTemplate = get_template('webchat/booking_form.html')
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

def bookingCompleted(request):
    tempId = request.GET['id']
    updateBooking(tempId=tempId, tempStatus='9')
    usedTemplate = get_template('admin/bookinglist.html')
    bookingList = BookingInfo.objects.all().extra(where=["status in ('1')"])
    bookingListDic = {'bookingList' : bookingList}
    html = usedTemplate.render(bookingListDic)
    return HttpResponse(html)
    
def updateBooking(tempId, tempStatus):
    bookingInfo = BookingInfo.objects.get(id = tempId)
    bookingInfo.status = tempStatus
    bookingInfo.save()
    
def bookingCancel(request):
    tempId = request.GET['id']
    updateBooking(tempId=tempId, tempStatus='0')
    return HttpResponseRedirect('../bookinglist/')
    '''usedTemplate = get_template('admin/bookinglist.html')
    bookingList = BookingInfo.objects.all().extra(where=["status in ('1')"])
    bookingListDic = {'bookingList' : bookingList}
    html = usedTemplate.render(bookingListDic)
    return HttpResponse(html)'''

def cancelBooking(request):
    tempId = request.GET['id']
    updateBooking(tempId=tempId, tempStatus='0')
    usedTemplate = get_template('webchat/cancelbooking.html')
    html = usedTemplate.render()
    return HttpResponse(html)

def goAdminBooking(request):
    outDicForm = initForm()
    outDicForm['hightlight'] = '1'
    outDic = dict(createResponseDic(request).items() + outDicForm.items())
    
    usedTemplate = get_template('admin/booking_form.html')
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

def doAdminBooking(request):
    outDicForm = initForm()
    outDicForm['hightlight'] = '1'
    outDic = dict(createResponseDic(request).items() + outDicForm.items())
    
    name = request.GET['name']
    phonenumber = request.GET['phonenumber']
    #membercard = request.GET['membercard']
    membercard = phonenumber
    bookeddoctor = request.GET['bookeddoctor']
    bookeditem = request.GET['bookeditem']
    bookedtime = request.GET['bookeddate'] + ' ' + request.GET['bookedhour']
    openId = ''
    
    bookingInfo = BookingInfo()
    bookingInfo.name = name
    bookingInfo.phonenumber = phonenumber
    bookingInfo.membercard = membercard
    bookingInfo.bookeddoctor = bookeddoctor
    bookingInfo.bookeditem = bookeditem
    bookingInfo.bookedtime = bookedtime
    bookingInfo.webchatid = openId
    bookingInfo.status = '1'
    bookingInfo.save()
    
    bookingList = getBookingList()
    usedTemplate = get_template('admin/bookinglist.html')
    outDic['bookingList'] = bookingList
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

def mybooking(request):
    #get webchat user
    openId = '000'
    try :
        code = request.GET['code']
        openId = getOpenID(code=code)
    except :
        openId = '000'
        print '------------this user is not binded-----------'
    #get webchat user
    
    try :
        bookingInfo = BookingInfo.objects.get(webchatid=openId, status=1)
        outputDic = {}
        outputDic['bookingid'] = bookingInfo.id
        outputDic['name'] = bookingInfo.name
        outputDic['phonenumber'] = bookingInfo.phonenumber
        outputDic['membercard'] = bookingInfo.membercard
        bookedtime = bookingInfo.bookedtime
        outputDic['bookedtime'] = bookedtime
        outputDic['bookingId'] = bookingInfo.id
        outputDic['openId'] = openId
        outputDic['paymentFlag'] = getPaymentFlag(memberCard=bookingInfo.membercard)
        
        if bookingInfo.bookeddoctor.strip() == '0' :
            outputDic['bookeddoctor'] = ''
        else :
            outputDic['bookeddoctor'] = DoctorInfo.objects.get(id=bookingInfo.bookeddoctor.strip()).doctorname
            
        if bookingInfo.bookeditem.strip() == '0' :
            outputDic['bookeditem'] = '' 
        else :
            outputDic['bookeditem'] = ServiceType.objects.get(id=bookingInfo.bookeditem.strip()).servicename
        
        #cancel link show checked    
        cancelFlag = getCancelFlag(bookedtime=bookedtime)
        outputDic['cancelFlag'] = cancelFlag
        
        usedTemplate = get_template('webchat/booking.html')
        html = usedTemplate.render(outputDic)
        return HttpResponse(html)
    except :
        usedTemplate = get_template('webchat/message.html')
        html = usedTemplate.render()
        return HttpResponse(html)
    
def getPaymentFlag(memberCard):
    try :
        Membership.objects.get(vipno=memberCard)
        returnValue = 'OK'
    except :
        returnValue = ''
    finally:
        return returnValue
    
def getCancelFlag(bookedtime):
    now = datetime.datetime.now()
    now = now + datetime.timedelta(hours=canceltime)
    nowstr = now.strftime('%Y/%m/%d %H:%M')
    cancelFlag = ''
    if nowstr < bookedtime :
        cancelFlag = 'OK'
    return cancelFlag

def prePay(request):
    openId = request.GET['openId']
    outputDic = {}
        
    try :
        mybookingInfo = BookingInfo.objects.get(webchatid=openId, status=1)
        bookingId = mybookingInfo.id
        outputDic['bookingid'] = bookingId
        outputDic['name'] = mybookingInfo.name
        outputDic['phonenumber'] = mybookingInfo.phonenumber
        outputDic['membercard'] = mybookingInfo.membercard
        
        membership = Membership.objects.get(vipno=mybookingInfo.membercard)
        servicediscount = membership.discountrate
        now = (datetime.timedelta(hours=timeBJ) + datetime.datetime.now()).strftime('%H')
        if now < '13' :
            servicediscount = membership.discountrate2
        outputDic['servicediscount'] = servicediscount
        outputDic['membershipId'] = membership.id
        
        bookeddoctorId = mybookingInfo.bookeddoctor
        doctor = DoctorInfo.objects.get(id=bookeddoctorId)
        outputDic['doctorname'] = doctor.doctorname
        
        bookedserviceId = mybookingInfo.bookeditem
        service = ServiceType.objects.get(id=bookedserviceId)
        outputDic['servicename'] = service.servicename
        outputDic['servicerate'] = service.servicerate
        outputDic['servicediscount'] = servicediscount
        amount = service.servicerate * servicediscount
        outputDic['amount'] = amount
        try :
            transaction = Transaction.objects.get(bookingId=bookingId, successFlag='0')
        except :
            today = datetime.datetime.now() + datetime.timedelta(hours=timeBJ)
            transaction = Transaction()
            transaction.membershipId = membership.id
            transaction.bookingId = mybookingInfo.id
            transaction.doctorId = doctor.id
            transaction.servicetypeId = bookedserviceId
            transaction.amount = amount
            transaction.paymentType = '00' #not decied
            transaction.successFlag = '0'
            transaction.transactionDate = today
            transaction.save()
        finally:
            outputDic['transactionId'] = transaction.id
        
        usedTemplate = get_template('webchat/prepay.html')
        html = usedTemplate.render(outputDic)
        
    except :
        print '-------------------can not do payment for openId = ' + openId
        usedTemplate = get_template('webchat/paymenterror.html')
        html = usedTemplate.render(outputDic)
        
    finally:
        return HttpResponse(html)

def goPaymentType(request):
    transactionId = request.GET['transactionId']
    amount = request.GET['amount']
    
    outputDic = {}
    outputDic['transactionId'] = transactionId
    outputDic['amount'] = amount
    
    usedTemplate = get_template('webchat/paymenttype.html')
    html = usedTemplate.render(outputDic)
    return HttpResponse(html)

def doPayment(request):
    transactionId = request.GET['transactionId']
    paymenttype = request.GET['paymenttype']
    try :
        transaction = Transaction.objects.get(id=transactionId)
        transaction.paymentType = paymenttype
        transaction.successFlag = '1'
        bookingId = transaction.bookingId
        membershipId = transaction.membershipId
        
        amount = 0
        if membershipId <> '' :
            membership = Membership.objects.get(id=membershipId)
            lastAmount = membership.amount
            membership.lastamount = lastAmount
            amount = lastAmount - transaction.amount
            membership.amount = amount
            
        
        bookingInfo = BookingInfo.objects.get(id=bookingId)
        bookingInfo.status = 9
        
        
        if amount >= 0 :
            transaction.save()
            bookingInfo.save()
            if membershipId <> '' :
                membership.save()
        
            usedTemplate = get_template('webchat/paymentresult.html')
            html = usedTemplate.render()
        else :
            usedTemplate = get_template('webchat/paymenterror2.html')
            html = usedTemplate.render()
    except :
        usedTemplate = get_template('webchat/paymenterror.html')
        html = usedTemplate.render()
    finally:
        return HttpResponse(html)