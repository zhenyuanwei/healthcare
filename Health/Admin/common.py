'''
Created on Sep 10, 2016

@author: weizhenyuan
'''
from datetime import datetime
from datetime import timedelta
from HealthModel.models import Messages
from HealthModel.models import Membership

def checkSession(request):
    returnValue = True
    try :
        username = request.session.get('username', default=None)
        if username == None :
            returnValue = False
        
    except :
        returnValue = False
        
    finally:
        
        return returnValue
    
def createResponseDic(request):
    outDic = {}
    username = request.session.get('username')
    userId = request.session.get('userId')
    role = request.session.get('role')
    explorer = request.session.get('explorer')
    outDic['userId'] = userId
    outDic['username'] = username
    outDic['role'] = role
    outDic['explorer'] = explorer
    return outDic

def getToday():
    timeBJ = 8
    today = datetime.now() + timedelta(hours=timeBJ)
    return today

def getMessage(messageId):
    message = ''
    try :
        message = Messages.objects.get(messageId = messageId).message
    except :
        message = '7'
    return message

def getMembership(openId):
    membership = Membership.objects.get(webchatid=openId, deleteFlag = '0')
    return membership

def getMembership2(vipno = '', phonenumber = ''):
    membership = None
    try:
        if vipno == '' :
            membership = Membership.objects.get(phonenumber = phonenumber, deleteFlag = '0')
        elif phonenumber == '' :
            membership = Membership.objects.get(vipno = vipno, deleteFlag = '0')

    except:
        membership = None
    finally:
        return membership

def getDiscount(phonenumber):
    discount = 1
    try :
        membership = getMembership2(phonenumber = phonenumber)
        discount = membership.discountrate
        now = getToday().strftime('%H')
        if now < '12' :
            discount = membership.discountrate2
    except :
        discount = 1
        
    return discount