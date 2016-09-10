'''
Created on Sep 10, 2016

@author: weizhenyuan
'''
from django.template.loader import get_template
from django.http import HttpResponse
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