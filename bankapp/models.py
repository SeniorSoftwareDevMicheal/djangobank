from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib import messages
import uuid
import random
from decimal import Decimal
class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.balance = 0
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

    
class MyUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=6, choices=[('M', 'Male'), ('F', 'Female')])
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    id_number = models.CharField(max_length=10, unique=True, editable=False)
    account_number = models.CharField(max_length=10, unique=True, default='')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=1000)
    transaction_pin = models.PositiveIntegerField(blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'date_of_birth', 'gender']

    objects = MyUserManager()

    def save(self, *args, **kwargs):
        if not self.id_number:
            self.id_number = self.generate_account_number()
        if not self.account_number:
            self.account_number = self.generate_account_number()
        super().save(*args, **kwargs)


    def generate_account_number(self):
        while True:
            account_number = f'{random.randint(1000000000, 9999999999)}'
            if not MyUser.objects.filter(account_number=account_number).exists():
                return account_number

    def withdraw(self, amount):
        amount = Decimal(str(amount))  # Convert the amount to a Decimal object
        if amount >= self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount
        self.save()

    def airtime(self, amount):
        if amount >= self.balance :
            raise ValueError("Insuficient funds")
        self.balance -= Decimal(str(amount))
        self.save()
    
    def electricity(self, amount):
        if amount >= self.balance:
            raise ValueError("Insuficient funds")
        self.balance -= Decimal(str(amount))
        self.save()
    
    is_suspended = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.id_number:
            self.id_number = self.generate_account_number()
        if not self.account_number:
            self.account_number = self.generate_account_number()
        if self.is_suspended:
            self.balance = self.balance
        super().save(*args, **kwargs)

from django.db import models
from django.contrib.auth import get_user_model

class AccountBalance(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)

from django.contrib.auth.models import User

class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('Deposit', 'Deposit'),
        ('Withdrawal', 'Withdrawal'),
        ('Airtime', 'Airtime'),
        ('Sent', 'Sent'),
        ('Received', 'Received'),
        ('Electricity', 'Electricity'),
        ('Bank-Loan', 'Bank-Loan'),
        ('Repayment-Loan', 'Repayment-Loan'),
    ]

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=15, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{str(self.user)}: {self.transaction_type} of {self.amount} on {self.date}"

from django.db import models
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta

class Loan(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='pending')
    approved_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_loans')
    date_approved = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Loan Request by {self.user.email}"

    def calculate_due_date(self):
        if self.date_approved:
            self.due_date = self.date_approved + timedelta(days=30)  # Assuming a 30-day repayment period
            self.save()

    def check_due_date(self):
        if self.due_date and self.due_date < datetime.now() and self.status != 'paid':
            # Deduct the loan amount from the user's balance
            user = self.user
            user.balance -= self.amount
            user.save()
            self.status = 'deducted'
            self.save()

    def save(self, *args, **kwargs):
        if not self.due_date:
            self.due_date = self.calculate_due_date()
        super().save(*args, **kwargs)