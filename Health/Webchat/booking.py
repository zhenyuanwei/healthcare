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
from Health.Webchat.myweixin import getOpenID, sendMessage
from Health.Admin.common import getMembership, getDiscount
from HealthModel.models import Membership
from HealthModel.models import Transaction
from django.http import HttpResponseRedirect
from Health.Admin.common import createResponseDic
from django.views.decorators.csrf import csrf_exempt
from Health.Admin.common import getToday
from Health.Admin.common import getMessage
from Health.Admin.common import getMembership2

"@csrf_exempt"
timeBJ = 8
starttime = 7
endtime = 22
canceltime = 1
#booking time scale
bookingscale = 15
multiscale = 60 / bookingscale
bookingDays = int(getMessage(messageId = 'bookingDay'))

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
        
        price = 0
        if bookinginfo.bookeditem.strip() != '0' :
            tmpStr = ''
            try :
                service = ServiceType.objects.get(id=bookinginfo.bookeditem)
                tmpStr = service.servicename
                price = service.servicerate
            except :
                print '-------there is no service type' + bookinginfo.bookeditem + '----------'
            finally:
                bookinginfo.bookeditem = tmpStr
        else :
            bookinginfo.bookeditem = ''
            
        phonenumber = bookinginfo.phonenumber
        try :
            membership = getMembership2(phonenumber = phonenumber)
            amount = membership.amount
            discount = getDiscount(phonenumber = phonenumber)
            membershipPrice = price * float(discount)
            bookinginfo.membershipAmount = amount
            bookinginfo.isEnoughtAmount = 'Yes'
            bookinginfo.membershipId = membership.id
            if amount < membershipPrice :
                bookinginfo.isEnoughtAmount = 'No'
        except :
            bookinginfo.membershipAmount = ''
            bookinginfo.isEnoughtAmount = ''
            bookinginfo.membershipId = ''
            print 'This is not a booking for membership : phonenumber = ' + phonenumber
        
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
    print '---------------doctorId = ' + doctorId
    print '---------------doctorservice = ' + doctorservice
    print '---------------queryDate = ' + queryDate
    print '---------------selectedServiceId = ' + selectedServiceId
    try :
        doctorInfoList = DoctorInfo.objects.all()
        doctorInfoList = doctorInfoList.exclude(service = '')
        if doctorId == '' and doctorservice == '' :
            doctor = doctorInfoList[0]
            doctorId = doctor.id
            
            doctorservice = doctor.service
        serviceTypeList = getServiceList(doctorservice=doctorservice)
        if selectedServiceId == '' :
            selectedServiceId = serviceTypeList[0].id
        
        selectedService = ServiceType.objects.get(id=selectedServiceId)
        
        #check the service provide by the selcted doctor 20170311
        if selectedService not in serviceTypeList :
            selectedService = serviceTypeList[0]
        #check the service provide by the selcted doctor 20170311
        
        # delete how many bookingscale
        backCount = int((selectedService.serviceperiod -1) / bookingscale)
        
        dayList = getDaysList()
        if queryDate == '' :
            queryDate = dayList[0]
        timeList = getTimeList(doctorId=doctorId, queryDate=queryDate, backCount=backCount)
    
        try :
            tmpdoctor = DoctorInfo.objects.get(id = doctorId)
            doctorintroduce = tmpdoctor.comments
        except :
            doctorintroduce = ''
        
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
               'timeList' : timeList,
               'doctorintroduce' : doctorintroduce}
    return listDic

def getDaysList(length = bookingDays):
    dayList = []
    #today = datetime.datetime.now()
    #now = int(today.strftime('%H')) + timeBJ + 1
    today = getToday()
    
    #update for booking in now 2016/1126 start
    #now = int(today.strftime('%H')) + 1
    now = int(today.strftime('%H'))
    #update for booking in now 2016/1126 end
    
    if now >= endtime :
        for i in range(1, length + 1):
            dayList.append((today + datetime.timedelta(days=i)).strftime('%Y/%m/%d'))
    else :
        for i in range(0, length):
            dayList.append((today + datetime.timedelta(days=i)).strftime('%Y/%m/%d'))
        
    return dayList

def getTimeList(doctorId = '', queryDate = '', backCount = 0):
    timeList = []
    #today = datetime.datetime.now().strftime('%Y/%m/%d')
    #now = int(datetime.datetime.now().strftime('%H')) + timeBJ + 1
    today = getToday().strftime('%Y/%m/%d')
    #update for booking in now 2016/1126 start
    #now = int(getToday().strftime('%H')) + 1
    now = int(getToday().strftime('%H'))
    now_minutes = getToday().strftime('%M')
    #update for booking in now 2016/1126 end 
    
    if now < starttime :
        now = starttime
        #update for booking in now 2016/1126 start
        now_minutes = '00'
        #update for booking in now 2016/1126 end 
        
    if now >= endtime :
        now = starttime
        #update for booking in now 2016/1126 start
        now_minutes = '00'
        #update for booking in now 2016/1126 end
    
    #update for booking in now 2016/1126 start
    now_time = ''
    if now < 10 :
        now_time = '0' + str(now) + ':' + now_minutes
    else :
        now_time = str(now) + ':' + now_minutes
    #update for booking in now 2016/1126 end
        
    if doctorId == '' :
        for i in range(now, endtime):
            #update for booking in now 2016/1126 start
            #timeList.append(getTime(value=i))
            if now_time <= getTime(value=i) :
                timeList.append(getTime(value=i))
            #update for booking in now 2016/1126 end 
            
    elif queryDate <> '' :
        if today < queryDate :
            now = starttime
            #update for booking in now 2016/1126 start
            now_minutes = '00'
            #update for booking in now 2016/1126 end
        #update for booking in now 2016/1126 start   
        if now < 10 :
            now_time = '0' + str(now) + ':' + now_minutes
        else :
            now_time = str(now) + ':' + now_minutes
        #update for booking in now 2016/1126 end 
            
        bookingList = BookingInfo.objects.filter(bookeddoctor = doctorId)
        bookingList = bookingList.filter(status = '1')
        bookingList = bookingList.filter(bookedtime__startswith = queryDate)
        
        vacationList = Vacation.objects.filter(doctorId = doctorId)
        vacationList = vacationList.filter(flag = '1')
        vacationList = vacationList.filter(vacationDate = queryDate)

        i = 0
        while (i < (endtime - now) * multiscale):
            time = getTime(value=i, now=now)
            #update for booking in now 2016/1126 start
            if now_time > time :
                i = i + 1
                continue
            #update for booking in now 2016/1126 end
            
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
                
                # bug fixing for booking when the service started 2016/11/26 start   
                bookedHour = int(bookedtime.split(':')[0])
                bookedMinutes = int(bookedtime.split(':')[1]) 
                bookedEndMinute = bookedMinutes + serviceperiod
                bookedEndHour = bookedHour
                if bookedEndMinute > 59 :
                    bookedEndHour = bookedHour + 1
                    bookedEndMinute = bookedEndMinute - 60
                if bookedEndHour < 10 :
                    bookedEndTime = '0' + str(bookedEndHour) + ':'
                else :
                    bookedEndTime = str(bookedEndHour) + ':'
                if bookedEndMinute == 0 :
                    bookedEndTime = bookedEndTime  + '0' + str(bookedEndMinute)
                else :
                    bookedEndTime = bookedEndTime  + str(bookedEndMinute)
                
                if time > bookedtime and time < bookedEndTime :
                        addflag = False
                    
                # bug fixing for booking when the service started 2016/11/26 end
                
                if bookedtime == time :
                    addflag = False
                    
                    # delete the time scale for enough time to do selected service before the next booking
                    count = len(timeList)
                    if count < backCount :
                        backCount = count
                    for j in range(0, backCount) :
                        del timeList[count - j -1]
                    # delete the time scale for enough time to do selected service before the next booking
                    if serviceperiod > 0 :    
                        breakcount = int((serviceperiod - 1) / bookingscale)
                    break
            #check booking for avoiding double booking
            
            if addflag :
                timeList.append(time)

            i = i + 1 + breakcount

        # check doctor vacation to avoid booking in vacation period
        vacationTimeList = []
        for vacation in vacationList:
            vacationStartTime = changeHourToNum(vacation.starttime)
            vacationEndTime = changeHourToNum(vacation.endtime)
            i = 0 - backCount # delete the booking period befor vacation start in order to finish the service
            while (i < (vacationEndTime - vacationStartTime) * multiscale):
                vacationTimeList.append(getTime(i, vacationStartTime))
                i = i + 1

        #print(vacationTimeList)
        for vacationtime in vacationTimeList:
            if vacationtime in timeList :
                timeList.remove(vacationtime)

            # check doctor vacation to avoid booking in vacation period
    
    return timeList

def changeHourToNum(hour):
    hours = {'01:00' : 1, '02:00' : 2, '03:00' : 3,
             '04:00' : 4, '05:00' : 5, '06:00' : 6,
             '07:00' : 7, '08:00' : 8, '09:00' : 9,
             '10:00' : 10, '11:00' : 11, '12:00' : 12,
             '13:00' : 13, '14:00' : 14, '15:00' : 15,
             '16:00' : 16, '17:00' : 17, '18:00' : 18,
             '19:00' : 19, '20:00' : 20, '21:00' : 21,
             '22:00' : 22, '23:00' : 23, '24:00' : 24}
    return hours[hour]

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
                if serviceId != '' :
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
    bookeddate = request.GET['bookeddate']
    bookedhour = request.GET['bookedhour']
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
    #checkDBFlag = False
    tempBookingList = BookingInfo.objects.filter(webchatid = openId, status = '1')
    tempBookingList = tempBookingList.filter(bookeddoctor = bookeddoctor, bookedtime = bookedtime)
    if tempBookingList :
        #checkDBFlag = True
        checkFlag = False
    
    #if not checkDBFlag :    
    selectedService = ServiceType.objects.get(id = bookeditem)
    # delete how many bookingscale
    backCount = int((selectedService.serviceperiod -1) / bookingscale)
    timeList = getTimeList(doctorId = bookeddoctor, queryDate = bookeddate, backCount = backCount)
    if bookedhour not in timeList :
        #checkDBFlag = True
        checkFlag = False

    if checkFlag :
        #if not checkDBFlag :
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
        
        #send message to doctor
        sendNoticeMessage(booking = bookingInfo, isBooking = True)
        #send message to doctor
            
        '''return to next page'''
        usedTemplate = get_template('webchat/bookingsucess.html')
        html = usedTemplate.render()
        return HttpResponse(html)
    else :
        #messageDic = {'messages' : 'OK'}
        listDic = initForm(openId=openId)
        listDic['messages'] = 'OK'
        usedTemplate = get_template('webchat/booking_form.html')
        html = usedTemplate.render(listDic)
        return HttpResponse(html)

def sendNoticeMessage(booking, isBooking = True):
    name = booking.name
    phonenumber = booking.phonenumber
    bookeddoctor = booking.bookeddoctor
    bookeditem = booking.bookeditem
    bookedtime = booking.bookedtime
    doctorname = ''
    doctorOpenId = ''
    userOpenId = booking.webchatid
    try :
        doctor = DoctorInfo.objects.get(id = bookeddoctor)
        doctorname = doctor.doctorname
        doctorOpenId = doctor.webchatid
    except :
        doctorname = ''
        doctorOpenId = ''
    
    serviceName = ''
    try :
        service = ServiceType.objects.get(id = bookeditem)
        serviceName = service.servicename
    except :
        serviceName = ''
        
    textTemplate = get_template('webchat/bookingInfo.html')
    textDic = {}
    if isBooking :
        textDic['isBooking'] = 'True'
    else :
        textDic['isBooking'] = 'False'
    textDic['Name'] = name
    #textDic['PhoneNumber'] = phonenumber
    textDic['DoctorName'] = doctorname
    textDic['BookedItem'] = serviceName
    textDic['BookedTime'] = bookedtime
    
    text = textTemplate.render(textDic)
    if doctorOpenId != '' :
        sendMessage(openId = doctorOpenId, text = text)
    
    if userOpenId != '' :
        sendMessage(openId = userOpenId, text = text)
        
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
    if bookingInfo.status != tempStatus:
        bookingInfo.status = tempStatus
        bookingInfo.save()
        return bookingInfo
    else :
        raise Exception
    
    
def bookingCancel(request):
    tempId = request.GET['id']
    try :
        booking = updateBooking(tempId=tempId, tempStatus='0')
        #send message to doctor
        sendNoticeMessage(booking = booking, isBooking = False)
        #send message to doctor
    except :
        print 'double update checked'
    return HttpResponseRedirect('../bookinglist/')
    '''usedTemplate = get_template('admin/bookinglist.html')
    bookingList = BookingInfo.objects.all().extra(where=["status in ('1')"])
    bookingListDic = {'bookingList' : bookingList}
    html = usedTemplate.render(bookingListDic)
    return HttpResponse(html)'''

def cancelBooking(request):
    tempId = request.GET['id']
    try :
        booking = updateBooking(tempId=tempId, tempStatus='0')
        #send message to doctor
        sendNoticeMessage(booking = booking, isBooking = False)
        #send message to doctor
    except :
        print 'double update check'
    usedTemplate = get_template('webchat/cancelbooking.html')
    html = usedTemplate.render()
    return HttpResponse(html)
    #return HttpResponseRedirect('../mybooking/')

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
    
    tempBookingList = BookingInfo.objects.filter(status = '1')
    tempBookingList = tempBookingList.filter(bookeddoctor = bookeddoctor, bookedtime = bookedtime)
    if tempBookingList :
        print '------duplication booking is cancelled'
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
        outputDic = {}
        tmpBookingList = BookingInfo.objects.filter(webchatid=openId, status=1)
        
        bookingList = []
        for bookingInfo in tmpBookingList :
            bookedtime = bookingInfo.bookedtime
            cancelFlag = getCancelFlag(bookedtime=bookedtime)
            bookingInfo.cancelFlag = cancelFlag
            
            bookeddoctor = bookingInfo.bookeddoctor
            bookeditem = bookingInfo.bookeditem
            if bookeddoctor.strip() == '0' :
                doctorname = ''
            else :
                doctorname = DoctorInfo.objects.get(id=bookeddoctor).doctorname
            bookingInfo.doctorname = doctorname 
             
            if bookeditem.strip() == '0' :
                servicename = '' 
            else :
                servicename = ServiceType.objects.get(id=bookeditem).servicename
            bookingInfo.servicename = servicename 
            
            bookingList.append(bookingInfo)
            
        outputDic['bookingList'] = bookingList
        
        usedTemplate = get_template('webchat/booking.html')
        html = usedTemplate.render(outputDic)
        return HttpResponse(html)
    except :
        usedTemplate = get_template('webchat/message.html')
        html = usedTemplate.render()
        return HttpResponse(html)
    
def getPaymentFlag(memberCard):
    try :
        Membership.objects.get(vipno=memberCard, deleteFlag = '0')
        returnValue = 'OK'
    except :
        returnValue = ''
    finally:
        return returnValue
    
def getCancelFlag(bookedtime):
    now = getToday()
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
        
        membership = Membership.objects.get(vipno=mybookingInfo.membercard, deleteFlag = '0')
        servicediscount = membership.discountrate
        #now = (datetime.timedelta(hours=timeBJ) + datetime.datetime.now()).strftime('%H')
        now = getToday().strftime('%H')
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
            #today = datetime.datetime.now() + datetime.timedelta(hours=timeBJ)
            today = getToday()
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
            membership = Membership.objects.get(id=membershipId, deleteFlag = '0')
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