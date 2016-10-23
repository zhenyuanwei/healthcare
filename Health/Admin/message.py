'''
Created on Oct 23, 2016

@author: weizhenyuan
'''
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.template.loader import get_template
from Health.Admin.common import createResponseDic
from Health.Webchat.myweixin import sendMessageToAll

def goSendMessage(request):
    outDic = createResponseDic(request=request)
    outDic['hightlight'] = '12'
    
    usedTemplate = get_template('admin/sendmessagetoall.html')
    html = usedTemplate.render(outDic)
    return HttpResponse(html)

@csrf_exempt
def sendMessage(request):
    outDic = createResponseDic(request=request)
    outDic['hightlight'] = '12'
    try :
        message = request.POST['message']
        sendMessageToAll(message)
        return HttpResponse('Success!')
    except :
        return HttpResponse('Failt!')
