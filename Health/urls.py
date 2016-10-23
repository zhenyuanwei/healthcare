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
from Health.Admin import adminuserDB
from Health.Admin import dbmainten
from Health.Webchat import membershipmanage
from Health.Webchat import introduce
from Health.Admin import payment
from Health.Webchat import myweixin
from Health.Webchat import doctorManagement
from Health.Admin import message

urlpatterns = [
    url(r'^hello/$', helloworld.hello),
    url(r'^webchat/goredirect/$', myweixin.goUrl),
    url(r'^webchat/introduce/$', introduce.introduce),
    url(r'^webchat/booking_form/$', booking.booking_form),
    url(r'^webchat/refershdoctor/$', booking.refershDoctor),
    #url(r'^webchat/refershdate/$', booking.refershDate),
    url(r'^webchat/booking/$', booking.booking),
    url(r'^webchat/cancelbooking/$', booking.cancelBooking),
    url(r'^webchat/bindMembershipCheck/$', membershipmanage.bindMembershipCheck),
    url(r'^webchat/bindMembership/$', membershipmanage.bindMembership),
    url(r'^webchat/mybooking/$', booking.mybooking),
    url(r'^webchat/prepayment/$', booking.prePay),
    url(r'^webchat/paymenttype/$', booking.goPaymentType),
    url(r'^webchat/dopayment/$', booking.doPayment),
    url(r'^webchat/gobinddoctor/$', doctorManagement.gobindDoctor),
    url(r'^webchat/dobinddoctor/$', doctorManagement.dobindDoctor),
    url(r'^webchat/godoctorquery/$', doctorManagement.goDoctorQuery),
    url(r'^webchat/godoctormonthquery/$', doctorManagement.goDoctorMonthQuery),
    url(r'^webchat/doctorbooking/$', doctorManagement.doctorBooking),
    url(r'^webchat/govacationapplication/$', doctorManagement.goVacationApply),
    url(r'^webchat/dovacationapplication/$', doctorManagement.doVacationApply),
    #Below is for administrator
    url(r'^admin/login/$', loginAction.login),
    url(r'^admin/doLogin/$', loginAction.doLogin),
    url(r'^admin/gopasswordchange/$', adminuserDB.goChangePassword),
    url(r'^admin/dopasswordchange/$', adminuserDB.doChangePassword),
    url(r'^admin/booking/$', booking.goAdminBooking),
    url(r'^admin/refershdoctor/$', booking.adminRefershDoctor),
    url(r'^admin/dobooking/$', booking.doAdminBooking),
    url(r'^admin/complatedBooking/$', booking.bookingCompleted),
    url(r'^admin/cancelBooking/$', booking.bookingCancel),
    url(r'^admin/bookinglist/$', loginAction.bookingList),
    url(r'^admin/doctor/$', dbmainten.goDoctorInfo),
    url(r'^admin/doctorlist/$', dbmainten.goDoctorInfoList),
    url(r'^admin/dodoctor/$', dbmainten.addDoctorInfo),
    url(r'^admin/dodoctordelete/$', dbmainten.deleteDoctorInfo),
    url(r'^admin/doctorupdate/$', dbmainten.goUpdateDoctorInfo),
    url(r'^admin/servicetype/$', dbmainten.goServiceType),
    url(r'^admin/servicetypelist/$', dbmainten.goServiceTypeList),
    url(r'^admin/servicetypedelete/$', dbmainten.deleteServiceType),
    url(r'^admin/servicetypeupdate/$', dbmainten.goServiceTypeUpdate),
    url(r'^admin/doservicetype/$', dbmainten.doServiceType),
    url(r'^admin/membershiplist/$', dbmainten.goMembershipList),
    url(r'^admin/membershipquery/$', dbmainten.membershipListQuery),
    url(r'^admin/membershipdetail/$', dbmainten.goMembershipDetail),
    url(r'^admin/membershipdelete/$', dbmainten.goMembershipDelete),
    url(r'^admin/membershipupdate/$', dbmainten.goMembershipUpdate),
    url(r'^admin/membershipupdateamount/$', dbmainten.goMembershipAmountUpdate),
    url(r'^admin/membership/$', dbmainten.goMembership),
    url(r'^admin/domembership/$', dbmainten.doMembership),
    url(r'^admin/godiscountlist/$', dbmainten.goDiscountRateList),
    url(r'^admin/godiscount/$', dbmainten.goDiscountRate),
    url(r'^admin/dodiscount/$', dbmainten.doDiscountRate),
    url(r'^admin/goupdatediscount/$', dbmainten.goUpdateDiscountRate),
    url(r'^admin/deletediscount/$', dbmainten.deleteDiscountRate),
    url(r'^admin/goproductlist/$', dbmainten.goProductList),
    url(r'^admin/goproduct/$', dbmainten.goProduct),
    url(r'^admin/doproduct/$', dbmainten.doProduct),
    url(r'^admin/deleteproduct/$', dbmainten.deleteProduct),
    url(r'^admin/gopaymenttypelist/$', dbmainten.goPaymentTypeList),
    url(r'^admin/gopaymenttype/$', dbmainten.goPaymentType),
    url(r'^admin/dopaymenttype/$', dbmainten.doPaymentType),
    url(r'^admin/goprepayment/$', payment.goPrePayment),
    url(r'^admin/doprepayment/$', payment.doPrePayment),
    url(r'^admin/gopaymenttypeselect/$', payment.goPaymentTypeSelect),
    url(r'^admin/gounpayedlist/$', payment.goUnpayedList),
    url(r'^admin/dodeleteunpayed/$', payment.doDeleteUnpayed),
    url(r'^admin/dopaymenttypeselect/$', payment.doPaymentTypeSelect),
    url(r'^admin/dopayment/$', payment.doPayment),
    url(r'^admin/gopaymentlist/$', payment.goPaymentList),
    url(r'^admin/deletepayment/$', payment.deletePayment),
    url(r'^admin/cancelpayment/$', payment.cancelPayment),
    url(r'^admin/querypaymentlist/$', payment.searchPaymentList),
    url(r'^admin/summaryquery/$', payment.goPaymentSummaryList),
    url(r'^admin/querysummaryquery/$', payment.searchPaymentSummaryList),
    url(r'^admin/goaccounting/$', payment.goAccounting),
    url(r'^admin/govacationlist/$', dbmainten.goVacatinList),
    url(r'^admin/cancelvacation/$', dbmainten.doCancelVacation),
    url(r'^admin/vacationapplication/$', dbmainten.goAdminVacatinApplication),
    url(r'^admin/dovacationapplication/$', dbmainten.doAdminVacatinApplication),
    url(r'^admin/gosendmessage/$', message.goSendMessage),
    url(r'^admin/sendmessage/$', message.sendMessage),
] 



