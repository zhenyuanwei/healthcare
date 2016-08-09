"""from django.http import HttpResponse

def hello(request):
    return HttpResponse("Hello world ! ")"""


from django.shortcuts import render
from Health.Webchat.myweixin import getOpenID

def hello(request):
    context          = {}
    
    #code = request.GET['code']
    #context['hello'] = code
    #return render(request, 'hello.html', context)
    return getOpenID(REDIRECT_URI='', CODE='')
