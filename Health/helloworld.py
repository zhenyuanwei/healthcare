"""from django.http import HttpResponse

def hello(request):
    return HttpResponse("Hello world ! ")"""


from django.shortcuts import render
from Health.Webchat.myweixin import getOpenID

def hello(request):
    context          = {}
    openid = getOpenID('http://www.ibm.com/Health/booking_form/')
    context['hello'] = openid
    return render(request, 'hello.html', context)
    "return render(request, 'webchat/booking_form.html', context)"