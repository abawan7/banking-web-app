from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name="login"),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('billpayment/', views.billpayment, name='billpayment'),
    path('billpayment/addbill/', views.addbill, name='addbill'),
    path('billpayment/paybill/', views.paybill, name='paybill'),
    path('card/', views.card, name='carddetail'),
    path('beneficiary/fundtransfer/', views.fundtransfer, name='fundtransfer'),
    path('about/', views.about, name='about'),
    path('accountInfo/', views.accountInfo, name="accountInfo"),
    path('transactionDetails/', views.transactionDetails, name="transactionDetails"),
    path('statement/', views.statement, name='statement'),
    path('beneficiary/', views.beneficiary, name='beneficiary'),
    path('beneficiary/addbeneficiary/', views.addbeneficiary, name='addbeneficiary'),
    path('mobileTopUp/', views.mobile_top_up, name='mobile_top_up'),
    path('mobileTopUp/addMobileTopUp/', views.add_mobile_top_up, name='add_mobile_top_up'),
    path('mobileTopUp/sendTopUp/', views.send_top_up, name='send_top_up'),
    path('recovery/', views.recovery_password, name="recovery_password"),
    path('verify-credentials/', views.verify_credentials, name='verify_credentials'),
    path('update-password/', views.update_password, name='update_password')
]
