'''
Created on Sep 10, 2016

@author: weizhenyuan
'''
from datetime import datetime
from datetime import timedelta
from HealthModel.models import Messages

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