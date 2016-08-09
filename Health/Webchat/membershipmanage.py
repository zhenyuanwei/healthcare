'''
Created on Jul 28, 2016

@author: weizhenyuan
'''
from django.http import HttpResponse
from django.template.loader import get_template
from Health.Webchat.myweixin import getOpenID
from HealthModel.models import Membership
from Health.formatValidation import phoneNumberCheck
def getMembership(openId):
    membership = Membership.objects.get(webchatid=openId)
    return membership

def getMembership2(vipno, phonenumber):
    membership = Membership.objects.get(vipno=vipno, phonenumber=phonenumber)
    return membership

def bindMembershipCheck(request):
    #get webchat user
    openId = '000'
    try :
        code = request.GET['code']
        openId = getOpenID(code=code)
    except :
        openId = '000'
        print '------------this user is not binded-----------'
    #get webchat user
    membership = getMembership(openId=openId)
    if membership :
        usedTemplate = get_template('webchat/membershipinfo.html')
        membershipDic = {'membership' : membership}
        html = usedTemplate.render(membershipDic)
        return HttpResponse(html)
    else :
        outDic = {}
        outDic['openId'] = openId
        usedTemplate = get_template('webchat/memberbind.html')
        html = usedTemplate.render()
        return HttpResponse(html)
    
def bindMembership(request):
    openId = request.GET['openId']
    phonenumber = request.GET['phonenumber']
    vipno = request.GET['vipno']
    try :
        membership = getMembership2(vipno=vipno, phonenumber=phonenumber)
        membership.webchatid = openId
        membership.save()
        usedTemplate = get_template('webchat/membershipinfo.html')
        membershipDic = {'membership' : membership}
        html = usedTemplate.render(membershipDic)
        return HttpResponse(html)
    except :
        usedTemplate = get_template('webchat/memberbind.html')
        messageDic = {'messages' : 'OK'}
        html = usedTemplate.render(messageDic)
        return HttpResponse(html)
        
    
    
    
    