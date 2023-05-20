from django.contrib import admin
from .models import MyUser, MyUserManager, AccountBalance, Transaction
# Register your models here.
admin.site.register(MyUser)
admin.site.register(AccountBalance)
admin.site.register(Transaction)
# admin.site.register(DepositValidationRequest)