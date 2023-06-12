from django.contrib import admin
from .models import MyUser, MyUserManager, AccountBalance, Transaction, Loan, Contact
# Register your models here.
admin.site.register(MyUser)
admin.site.register(AccountBalance)
admin.site.register(Transaction)
admin.site.register(Loan)
admin.site.register(Contact)
# admin.site.register(DepositValidationRequest)