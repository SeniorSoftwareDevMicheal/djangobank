from django.urls import path
from .import views

urlpatterns = [
    path('',views.index, name='index' ),
    path('home',views.home, name='home' ),
    path('signup',views.signup, name='signup' ),
    path('user_login',views.user_login, name='user_login'),
    path('signin',views.signin, name='signin' ),
    path('withdraw',views.withdraw, name='withdraw' ),
    path('deposit',views.deposit, name='deposit' ),
    path('transfer',views.transfer, name='transfer' ),
    path('dashboard',views.dashboard, name='dashboard' ),
    path('airtime',views.airtime, name='airtime' ),
    path('history',views.history, name='history' ),
    path('electricity',views.electricity, name='electricity' ),
    path('admindashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admindash',views.admindash, name='admindash' ),
    path('suspend_user/<int:user_id>/', views.suspend_user, name='suspend_user'),
    path('unsuspend_user/<int:user_id>/', views.unsuspend_user, name='unsuspend_user'),
    # path('validate_deposit',views.validate_deposit, name='validate_deposit')
]