'''
Created on Jul 19, 2016

@author: weizhenyuan
'''
from wechatpy.oauth import WeChatOAuth
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.template.loader import get_template

def goUrl(request):
    page = request.GET['page']
    redirectURL = goRedirect(page=page)
    return HttpResponseRedirect(redirectURL)

def goRedirect(page):
    APP_ID = 'wx21c7501e68d463df'
    APP_SECRET = '82fcc8a8bb59b2318f1e97a6292a7ecc'
    baseurl = 'http://www.pengchengguoyi.cn/health/webchat/'
    #baseurl = 'http://127.0.0.1:8000/webchat/'
    REDIRECT_URI = baseurl + page
    #scope = 'snsapi_userinfo'
    weChatOAuth = WeChatOAuth(app_id=APP_ID, secret=APP_SECRET, redirect_uri=REDIRECT_URI)
    goUrl = weChatOAuth.authorize_url
    return goUrl
    #return REDIRECT_URI

def getOpenID(code, page=''):
    APP_ID = 'wx21c7501e68d463df'
    APP_SECRET = '82fcc8a8bb59b2318f1e97a6292a7ecc'
    baseurl = 'http://www.pengchengguoyi.cn/health/webchat/'
    REDIRECT_URI = baseurl + page
    #scope = 'snsapi_userinfo'
    weChatOAuth = WeChatOAuth(app_id=APP_ID, secret=APP_SECRET, redirect_uri=REDIRECT_URI)
    res = weChatOAuth.fetch_access_token(code=code)
    openId = res['openid']
    return openId
