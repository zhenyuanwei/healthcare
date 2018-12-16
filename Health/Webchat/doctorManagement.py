'''
Created on Aug 14, 2016

@author: weizhenyuan
'''
from django.http import HttpResponse
from django.template.loader import get_template
from Health.Webchat.myweixin import getOpenID
from HealthModel.models import DoctorInfo
from Health.Admin.payment import getPaymentList
from HealthModel.models import BookingInfo
from HealthModel.models import ServiceType
from HealthModel.models import Vacation
from datetime import time
from Health.Admin.common import getToday, getNextDay
from Health.Webchat.booking import getDaysList
from Health.Webchat.booking import bookingDays
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect

timeBJ = 8

def gobindDoctor(request):
    #get webchat user
    openId = '000'
    try :
        code = request.GET['code']
        openId = getOpenID(code=code)
    except :
        openId = '000'
        print '------------this is not from weixin-----------'
    #get webchat user
    
    outDic = {}
    outDic['openId'] = openId
    
    try :
        doctor = DoctorInfo.objects.get(webchatid=openId)
        outDic['doctor'] = doctor
        usedTemplate = get_template('webchat/doctorinfo.html')
        html = usedTemplate.render(outDic)
    except :
        usedTemplate = get_template('webchat/doctorbind.html')
        html = usedTemplate.render(outDic)
    return HttpResponse(html) 

def dobindDoctor(request):
    outDic = {}
    openId = request.GET['openId']
    bindno = request.GET['bindno']
    outDic['openId'] = openId
    outDic['bindno'] = bindno
    
    try :
        print '----------- bindno = ' + bindno
        doctor = DoctorInfo.objects.get(phonenumber=bindno)
        webchatId = doctor.webchatid
        if webchatId == '' :
            doctor.webchatid = openId
            doctor.save()
        else :
            outDic['messages'] = 'BINDED'
            
        outDic['doctor'] = doctor
        usedTemplate = get_template('webchat/doctorinfo.html')
        html = usedTemplate.render(outDic)
        return HttpResponse(html) 
    except :
        outDic['messages'] = 'OK'
        usedTemplate = get_template('webchat/doctorbind.html')
        html = usedTemplate.render(outDic)
        return HttpResponse(html) 

def goDoctorQuery(request):
    #get webchat user
    openId = '000'
    try :
        code = request.GET['code']
        openId = getOpenID(code=code)
    except :
        openId = '000'
        print '------------this is not from weixin-----------'
    #get webchat user
    outDic = {}
    outDic['openId'] = openId
    try :
        doctor = DoctorInfo.objects.get(webchatid=openId)
        doctorId = doctor.id
        #today = (datetime.now() + timedelta(hours=timeBJ)).strftime('%Y-%m-%d')
        today = getToday().strftime('%Y-%m-%d')
        paymentList = getPaymentList(doctorId=doctorId, querydate=today)
        outDic['paymentList'] = paymentList

        # fullprice 20181216
        fullpricepaymentList = getPaymentList(doctorId=doctorId, querydate=today, isFullPrice=True)
        outDic['fullpricepaymentList'] = fullpricepaymentList
        # fullprice 20181216

        usedTemplate = get_template('webchat/doctorpaymentlist.html')
        html = usedTemplate.render(outDic)
    except :
        outDic['messages'] = 'BIND'
        usedTemplate = get_template('webchat/doctorbind.html')
        html = usedTemplate.render(outDic)
    finally:
        return HttpResponse(html) 

    
def goDoctorMonthQuery(request):
    #get webchat user
    openId = '000'
    try :
        code = request.GET['code']
        openId = getOpenID(code=code)
    except :
        openId = '000'
        print '------------this is not from weixin-----------'
    #get webchat user
    outDic = {}
    outDic['openId'] = openId
    try :
        doctor = DoctorInfo.objects.get(webchatid=openId)
        doctorId = doctor.id
        today = getToday()
        year = today.strftime('%Y')
        month = today.strftime('%m')
        paymentList = getPaymentList(doctorId=doctorId, queryyear=year, querymonth=month)
        outDic['paymentList'] = paymentList

        # fullprice 20181216
        fullpricepaymentList = getPaymentList(doctorId=doctorId, queryyear=year, querymonth=month, isFullPrice=True)
        outDic['fullpricepaymentList'] = fullpricepaymentList
        # fullprice 20181216

        usedTemplate = get_template('webchat/doctorpaymentlist.html')
        html = usedTemplate.render(outDic)
    except :
        outDic['messages'] = 'BIND'
        usedTemplate = get_template('webchat/doctorbind.html')
        html = usedTemplate.render(outDic)
    finally:
        return HttpResponse(html) 

# doctor query the booking
def doctorBooking(request):
    #get webchat user
    openId = '000'
    try :
        code = request.GET['code']
        openId = getOpenID(code=code)
    except :
        openId = '000'
        print '------------this is not from weixin-----------'
    #get webchat user
    
    outDic = {}
    outDic['openId'] = openId
    try :
        doctor = DoctorInfo.objects.get(webchatid=openId)
        doctorId = doctor.id
        today = getToday().strftime('%Y/%m/%d')
        nextDay = getNextDay().strftime('%Y/%m/%d')

        # update by 20171021
        '''
        bookingList = []
        tmpList = BookingInfo.objects.filter(bookeddoctor=doctorId)
        tmpList = tmpList.filter(status='1')
        tmpList = tmpList.filter(bookedtime__startswith=today)
        tmpList = tmpList.order_by('bookedtime')
        for booking in tmpList :
            serviceId = booking.bookeditem
            service = ServiceType.objects.get(id=serviceId)
            time = booking.bookedtime.split(' ')[1]
            booking.bookedtime = time
            booking.bookeditem = service.servicename
            bookingList.append(booking)
        '''
        bookingList = getDoctorBookingList(doctorId=doctorId, date=today)
        bookingList = bookingList + (getDoctorBookingList(doctorId=doctorId, date=nextDay))
        # update by 20171021

        outDic['bookingList'] = bookingList
        usedTemplate = get_template('webchat/doctorbookinglist.html')
        html = usedTemplate.render(outDic)
    except :
        outDic['messages'] = 'BIND'
        usedTemplate = get_template('webchat/doctorbind.html')
        html = usedTemplate.render(outDic)
    finally:
        return HttpResponse(html)

def getDoctorBookingList(doctorId, date):
    bookingList = []
    tmpList = BookingInfo.objects.filter(bookeddoctor=doctorId)
    tmpList = tmpList.filter(status='1')
    tmpList = tmpList.filter(bookedtime__startswith=date)
    tmpList = tmpList.order_by('bookedtime')
    for booking in tmpList:
        serviceId = booking.bookeditem
        service = ServiceType.objects.get(id=serviceId)
        #time = booking.bookedtime.split(' ')[1]
        time = booking.bookedtime
        booking.bookedtime = time
        booking.bookeditem = service.servicename
        bookingList.append(booking)
    return bookingList

def goVacationApply(request):
    #get webchat user
    openId = '000'
    try :
        code = request.GET['code']
        openId = getOpenID(code=code)
    except :
        openId = '000'
        print '------------this is not from weixin-----------'
    #get webchat user
    
    outDic = {}
    outDic['openId'] = openId
    try :
        doctor = DoctorInfo.objects.get(webchatid=openId)
        doctorId = doctor.id
        doctorName = doctor.doctorname
        dayList = getDaysList(bookingDays + 7)
        outDic['doctorId'] = doctorId
        outDic['doctorName'] = doctorName
        outDic['dayList'] = dayList
        
        today = getToday().strftime('%Y/%m/%d')
        vacationList = Vacation.objects.filter(flag='1', doctorId = doctorId)
        vacationList = vacationList.filter(vacationDate__gte = today)
        outDic['vacationList'] = vacationList
        
        usedTemplate = get_template('webchat/vacationapplication.html')
        html = usedTemplate.render(outDic)
    except :
        outDic['messages'] = 'BIND'
        usedTemplate = get_template('webchat/doctorbind.html')
        html = usedTemplate.render(outDic)
    finally:
        return HttpResponse(html) 
    
@csrf_exempt    
def doVacationApply(request):
    
    outDic = {}
    
    try :
        doctorId = request.POST['doctorId']
        vacationDate  = request.POST['vacationDate']
        starttime = request.POST['starttime']
        endtime = request.POST['endtime']
        doctorName = request.POST['doctorName']
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
        
        return HttpResponseRedirect('../govacationapplication/')
    
    except :
        outDic['messages'] = 'ERROR'
        usedTemplate = get_template('webchat/vacation.html')
        html = usedTemplate.render(outDic)
        return HttpResponse(html)         
