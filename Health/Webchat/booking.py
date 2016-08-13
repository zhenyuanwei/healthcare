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
    
    doctorInfoList = DoctorInfo.objects.all()
    serviceTypeList = ServiceType.objects.all()
    today = datetime.datetime.now()
    dayList = []
    for i in range(1, 8):
        dayList.append((today + datetime.timedelta(days=i)).strftime('%Y/%m/%d'))

    
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
    
    ListDic = {'doctorInfoList' : doctorInfoList, 
               'serviceTypeList' : serviceTypeList, 
               'dayList' : dayList,
               'vipno' : vipno,
               'vipname' : vipname,
               'phonenumber' : phonenumber,
               'openId' : openId}
    usedTemplate = get_template('webchat/booking_form.html')
    html = usedTemplate.render(ListDic)
    return HttpResponse(html)
    """return render_to_response('webchat/booking_form.html')"""


def booking(request):
    """valueDic = {'rlt' : request.GET('q')}
    htmlContext = Context(valueDic)'''
    content['rlt'] = request.GET['q']"""
    '''save to db
    '''
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
            
            if request.GET['bookeddoctor'].strip() == '0' :
                outputDic['bookeddoctor'] = ''
            else :
                outputDic['bookeddoctor'] = DoctorInfo.objects.get(id=bookeditem).doctorname
                
            if request.GET['bookeditem'].strip() == '0' :
                outputDic['bookeditem'] = '' 
            else :
                outputDic['bookeditem'] = ServiceType.objects.get(id=bookeditem).servicename
            html = usedTemplate.render(outputDic)
            return HttpResponse(html)
    else :
        messageDic = {'messages' : 'OK'}
        usedTemplate = get_template('webchat/booking_form.html')
        html = usedTemplate.render(messageDic)
        return HttpResponse(html)

def bookingCompleted(request):
    tempId = request.GET['id']
    updateBooking(tempId, '9')
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
    updateBooking(tempId, '0')
    usedTemplate = get_template('admin/bookinglist.html')
    bookingList = BookingInfo.objects.all().extra(where=["status in ('1')"])
    bookingListDic = {'bookingList' : bookingList}
    html = usedTemplate.render(bookingListDic)
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
        outputDic['bookedtime'] = bookingInfo.bookedtime
        
        if bookingInfo.bookeddoctor.strip() == '0' :
            outputDic['bookeddoctor'] = ''
        else :
            outputDic['bookeddoctor'] = DoctorInfo.objects.get(id=bookingInfo.bookeddoctor.strip()).doctorname
            
        if bookingInfo.bookeditem.strip() == '0' :
            outputDic['bookeditem'] = '' 
        else :
            outputDic['bookeditem'] = ServiceType.objects.get(id=bookingInfo.bookeditem.strip()).servicename
        usedTemplate = get_template('webchat/booking.html')
        html = usedTemplate.render(outputDic)
        return HttpResponse(html)
    except :
        usedTemplate = get_template('webchat/message.html')
        html = usedTemplate.render()
        return HttpResponse(html)