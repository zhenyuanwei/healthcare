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
        membership = Membership.objects.get(vipno=vipno)
        doctorInfo = DoctorInfo.objects.get(id=doctor)
        service = ServiceType.objects.get(id=servicetype)
    except :
        print '--------there is no membership : vipno = ' + vipno + '------------'
        outDic['isMessage'] = 'OK'
        usedTemplate = get_template('admin/prepayment.html')
        html = usedTemplate.render(outDic)
        #return HttpResponse(html)
    finally:
        outDic['amount'] = amount
    #calculate the amount end
    
    usedTemplate = get_template('admin/prepaymentresult.html')
    html = usedTemplate.render(outDic)
    return HttpResponse(html)
