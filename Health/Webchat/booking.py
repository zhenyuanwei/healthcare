'''
Created on May 22, 2016

@author: wzy
'''
# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.template.loader import get_template
from HealthModel.models import BookingInfo
from Health.formatValidation import phoneNumberCheck
from Health.formatValidation import required
from HealthModel.models import DoctorInfo
from HealthModel.models import ServiceType
import datetime
from Health.Webchat.myweixin import getOpenID
from membershipmanage import getMembership
from HealthModel.models import Membership

"@csrf_exempt"
timeBJ = 8
starttime = 8
endtime = 21
canceltime = timeBJ + 1

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

def initForm(openId, doctorservice = '', doctorId='', queryDate=''):
    doctorInfoList = DoctorInfo.objects.all()
    serviceTypeList = getServiceList(doctorservice=doctorservice)
    
    dayList = getDaysList()
    timeList = getTimeList(doctorId=doctorId, queryDate=queryDate)

    
    vipno = ''
    vipname = ''
    phonenumber = ''
    
    try :
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

def getDaysList():
    dayList = []
    today = datetime.datetime.now()
    now = int(today.strftime('%H')) + timeBJ + 1
    print now
    if now >= endtime :
        for i in range(1, 8):
            dayList.append((today + datetime.timedelta(days=i)).strftime('%Y/%m/%d'))
    else :
        for i in range(0, 7):
            dayList.append((today + datetime.timedelta(days=i)).strftime('%Y/%m/%d'))
        
    return dayList

def getTimeList(doctorId = '', queryDate = ''):
    #queryDate = '2016/07/30'
    #doctorId = '1'
    
    timeList = []
    today = datetime.datetime.now().strftime('%Y/%m%d')
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
            
        bookingList = BookingInfo.objects.filter(bookeddoctor=doctorId)
        bookingList = bookingList.filter(status='1')
        bookingList = bookingList.filter(bookedtime__startswith=queryDate)
        for i in range(now, endtime):
            time = getTime(value=i)
            addflag = True
            for booking in bookingList :
                bookedtime = booking.bookedtime.split(' ')[1]
                if bookedtime == time :
                    addflag = False
            if addflag :
                timeList.append(time)
    
    return timeList

def getTime(value):
    time = ''
    if value < 10 :
        time = '0' + str(value) + ':00'
    else :
        time = str(value) + ':00'
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
    membercard = request.GET['membercard']
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
    if tempBookingList :
        checkDBFlag = True

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
    
def refershDoctor(request):
    vipname = request.GET['name']
    phonenumber = request.GET['phonenumber']
    vipno = request.GET['membercard']
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
        
    outDic = initForm(openId=openId, doctorservice=doctorservice, doctorId=bookeddoctor, queryDate=bookeddate)
    
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

'''def refershDate(request):
    vipname = request.GET['name']
    phonenumber = request.GET['phonenumber']
    vipno = request.GET['membercard']
    bookeddoctor = request.GET['bookeddoctor']
    bookeditem = request.GET['bookeditem']
    bookeddate = request.GET['bookeddate']
    #bookedhour = request.GET['bookedhour']
    openId = request.GET['openId']
    try :
        doctor = DoctorInfo.objects.get(id=bookeddoctor)
        doctorservice = doctor.service
    except :
        doctorservice = ''
        print '----------- there is no doctor selected -----------'
        
    outDic = initForm(openId=openId, doctorservice=doctorservice, doctorId=bookeddoctor, queryDate=bookeddate)
    
    outDic['vipname'] = vipname
    outDic['openId'] = openId
    outDic['phonenumber'] = phonenumber
    outDic['vipno'] = vipno
    outDic['bookeddoctor'] = int(bookeddoctor)
    outDic['bookeditem'] = int(bookeditem)
    outDic['bookeddate'] = bookeddate
    
    usedTemplate = get_template('webchat/booking_form.html')
    html = usedTemplate.render(outDic)
    return HttpResponse(html)'''

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
    usedTemplate = get_template('admin/bookinglist.html')
    bookingList = BookingInfo.objects.all().extra(where=["status in ('1')"])
    bookingListDic = {'bookingList' : bookingList}
    html = usedTemplate.render(bookingListDic)
    return HttpResponse(html)

def cancelBooking(request):
    tempId = request.GET['id']
    updateBooking(tempId=tempId, tempStatus='0')
    usedTemplate = get_template('webchat/cancelbooking.html')
    html = usedTemplate.render()
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
    
def getCancelFlag(bookedtime):
    now = datetime.datetime.now()
    now = now + datetime.timedelta(hours=canceltime)
    nowstr = now.strftime('%Y/%m/%d %H:%M')
    cancelFlag = ''
    if nowstr < bookedtime :
        cancelFlag = 'OK'
    return cancelFlag