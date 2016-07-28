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
    membership = Membership.objects.filter(webchatid=openId)
    return membership

def getMembership2(vipno, phonenumber):
    membership = Membership.objects.filter(vipno=vipno, phonenumber=phonenumber)
    return membership

def bindMembershipCheck(request):
    REDIRECT_URI = ''
    CODE = ''
    openId = getOpenID(REDIRECT_URI=REDIRECT_URI, CODE=CODE)
    membership = getMembership(openId=openId)
    if membership :
        usedTemplate = get_template('webchat/membershipinfo.html')
        membershipDic = {'membership' : membership}
        html = usedTemplate.render(membershipDic)
        return HttpResponse(html)
    else :
        usedTemplate = get_template('webchat/memberbind.html')
        html = usedTemplate.render()
        return HttpResponse(html)
    
def bindMembership(request):
    phonenumber = request.GET['phonenumber']
    vipno = request.GET['vipno']
    membership = getMembership2(vipno=vipno, phonenumber=phonenumber)
    if membership :
        REDIRECT_URI = ''
        CODE = ''
        openId = getOpenID(REDIRECT_URI=REDIRECT_URI, CODE=CODE)
        membership.webchatid = openId
        membership.save()
        usedTemplate = get_template('webchat/membershipinfo.html')
        membershipDic = {'membership' : membership}
        html = usedTemplate.render(membershipDic)
        return HttpResponse(html)
    else :
        usedTemplate = get_template('webchat/memberbind.html')
        messageDic = {'messages' : 'OK'}
        html = usedTemplate.render(messageDic)
        return HttpResponse(html)
        
    
    
    
    