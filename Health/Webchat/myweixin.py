'''
Created on Jul 19, 2016

@author: weizhenyuan
'''
from weixin.client import WeixinMpAPI

def getUser(REDIRECT_URI):
    scope = ("snsapi_base", )
    APP_ID = 'wx21c7501e68d463df'
    APP_SECRET = '82fcc8a8bb59b2318f1e97a6292a7ecc'
    api = WeixinMpAPI(appid=APP_ID,
                      app_secret=APP_SECRET,
                      redirect_uri=REDIRECT_URI)
    authorize_url = api.get_authorize_url(scope=scope)
    sPos = authorize_url.index('code=') + 5
    ePos = authorize_url.index('&')
    code = authorize_url[sPos : ePos]
    access_token = api.exchange_code_for_access_token(code=code)
    
    api = WeixinMpAPI(access_token=access_token)
    
    user = api.user(openid="openid")
    return user
