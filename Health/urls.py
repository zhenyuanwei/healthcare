"""Health URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
'''from django.conf.urls import url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
]'''
from django.conf.urls import url
from Health import helloworld
from Health.Webchat import booking
from Health.Admin import loginAction
from Health.Admin import dbmainten
from Health.Webchat import membershipmanage
from Health.Webchat import introduce

urlpatterns = [
    url(r'^Health/hello/$', helloworld.hello),
    url(r'^Health/introduce/$', introduce.introduce),
    url(r'^Health/booking_form/$', booking.booking_form),
    url(r'^Health/booking/$', booking.booking),
    url(r'^Health/bindMembershipCheck/$', membershipmanage.bindMembershipCheck),
    url(r'^Health/bindMembership/$', membershipmanage.bindMembership),
    url(r'^Health/mybooking/$', booking.mybooking),
    #Below is for administrator
    url(r'^Health/Admin/login/$', loginAction.login),
    url(r'^Health/Admin/doLogin/$', loginAction.doLogin),
    url(r'^Health/Admin/complatedBooking/$', booking.bookingCompleted),
    url(r'^Health/Admin/cancelBooking/$', booking.bookingCancel),
    url(r'^Health/Admin/bookinglist/$', loginAction.bookingList),
    url(r'^Health/Admin/doctor/$', dbmainten.goDoctorInfo),
    url(r'^Health/Admin/dodoctor/$', dbmainten.addDoctorInfo),
    url(r'^Health/Admin/servicetype/$', dbmainten.goServiceType),
    url(r'^Health/Admin/doservicetype/$', dbmainten.doServiceType),
    url(r'^Health/Admin/membershiplist/$', dbmainten.goMembershipList),
    url(r'^Health/Admin/membershipdelete/$', dbmainten.goMembershipDelete),
    url(r'^Health/Admin/membershipupdate/$', dbmainten.goMembershipUpdate),
    url(r'^Health/Admin/membershipupdateamount/$', dbmainten.goMembershipAmountUpdate),
    url(r'^Health/Admin/membership/$', dbmainten.goMembership),
    url(r'^Health/Admin/domembership/$', dbmainten.doMembership),
] 



