'''
Created on Jul 28, 2016

@author: weizhenyuan
'''
from django.http import HttpResponse
from django.template.loader import get_template

def introduce(request):
    usedTemplate = get_template('webchat/introduce.html')
    html = usedTemplate.render()
    return HttpResponse(html)
