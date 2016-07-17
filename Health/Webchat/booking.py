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
import math

"@csrf_exempt"
def booking_form(request):
    doctorInfoList = DoctorInfo.objects.all()
    serviceTypeList = ServiceType.objects.all()
    today = datetime.datetime.now()
    dayList = []
    for i in range(1, 8):
        dayList.append((today + datetime.timedelta(days=i)).strftime('%Y%m%d'))
    
    ListDic = {'doctorInfoList' : doctorInfoList, 'serviceTypeList' : serviceTypeList, 'dayList' : dayList}
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
    
    checkFlag = True;
    if not required(name) :
        checkFlag = False
        
    if not required(phonenumber) :
        checkFlag = False
    elif not phoneNumberCheck(phonenumber) :
        checkFlag = False
        
    if not required(bookedtime) :
        checkFlag = False
    
    if checkFlag :
        bookingInfo = BookingInfo()
        bookingInfo.name = name
        bookingInfo.phonenumber = phonenumber
        bookingInfo.membercard = membercard
        bookingInfo.bookeddoctor = bookeddoctor + ' '
        bookingInfo.bookeditem = bookeditem + ' '
        bookingInfo.bookedtime = bookedtime
        bookingInfo.webchatid = ' '
        bookingInfo.status = '1'
        bookingInfo.save()
        '''return to next page'''
        usedTemplate = get_template('webchat/booking.html')
        html = usedTemplate.render(request.GET)
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
    