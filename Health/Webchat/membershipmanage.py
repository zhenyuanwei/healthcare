'''
Created on Jul 28, 2016

@author: weizhenyuan
'''
from django.http import HttpResponse
from django.template.loader import get_template
from Health.Webchat.myweixin import getOpenID
from HealthModel.models import Membership, Transaction
from Health.formatValidation import phoneNumberCheck
from Health.Admin.payment import createPayment

maxCount = 5 

def getMembership(openId):
    membership = Membership.objects.get(webchatid=openId, deleteFlag = '0')
    return membership

def getMembership2(vipno, phonenumber):
    if vipno == '' :
        membership = Membership.objects.get(phonenumber = phonenumber, deleteFlag = '0')
    else :
        membership = Membership.objects.get(vipno = vipno, phonenumber = phonenumber, deleteFlag = '0')
    return membership

def bindMembershipCheck(request):
    #get webchat user
    openId = '000'
    try :
        code = request.GET['code']
        openId = getOpenID(code=code)
    except :
        openId = '000'
        print '------------this user is not binded-------- ' + openId
    #get webchat user
    try :
        membership = getMembership(openId=openId)
        membershipDic = {'membership' : membership}
        
        paymentList = getPaymentLog(membershipId = membership.id)
        membershipDic['paymentList'] = paymentList
        
        usedTemplate = get_template('webchat/membershipinfo.html')
        html = usedTemplate.render(membershipDic)
        
        return HttpResponse(html)
    except :
        outDic = {}
        outDic['openId'] = openId
        usedTemplate = get_template('webchat/memberbind.html')
        html = usedTemplate.render(outDic)
        return HttpResponse(html)
    
def bindMembership(request):
    openId = request.GET['openId']
    phonenumber = request.GET['phonenumber']
    #vipno = request.GET['vipno']
    vipno = ''
    membershipDic = {}
    try :
        membership = getMembership2(vipno = vipno, phonenumber = phonenumber)
        membershipDic['membership'] = membership
        if membership.webchatid == '' :
            membership.webchatid = openId
            membership.save()
        else :
            membershipDic['messages'] = 'BINDED'
        
        paymentList = getPaymentLog(membershipId = membership.id)
        membershipDic['paymentList'] = paymentList
        
        usedTemplate = get_template('webchat/membershipinfo.html')
        html = usedTemplate.render(membershipDic)
        return HttpResponse(html)
    except :
        usedTemplate = get_template('webchat/memberbind.html')
        messageDic = {'messages' : 'OK'}
        html = usedTemplate.render(messageDic)
        return HttpResponse(html)
        
def getPaymentLog(membershipId):
    paymentList = []
    transactionList = Transaction.objects.filter(membershipId = membershipId)
    transactionList = transactionList.exclude(successFlag = '0').order_by('-transactionDate')
    count = len(transactionList)
    if count >= maxCount :
        count = maxCount
    i = 0
    for transaction in transactionList :
        if i < count :
            payment = createPayment(transaction = transaction)
            paymentList.append(payment)
            i = i + 1
        else :
            break
        
    return paymentList
    
    