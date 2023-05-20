from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .models import MyUser
from django.contrib.auth import authenticate, login
from django.contrib.auth import authenticate, login as auth_login
from django.urls import reverse
# from .models import AccountBalance
# Create your views here.

#HOME PAGE FUNCTION
def index(request):
    return render(request, 'index.html')

def home(request):
    return render(request, 'index.html')

#SIGN IN FUNCTION


def signin(request):
    return render(request, 'signin.html')



def user_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        myuser = authenticate(request, email=email, password=password, backend='myapp.backends.EmailBackend')
        if myuser is not None:
            auth_login(request, myuser)
            return redirect(reverse('dashboard'))
        else:
            messages.error(request, 'Invalid credentials')
            return redirect(reverse('signin'))
    else:
        return render(request, 'signin.html')

def home(request):
    return redirect('/')

#SIGN UP Function
def signup(request):
    if request.method == 'POST':
        name = request.POST['name']
        date_of_birth = request.POST['date_of_birth']
        gender = request.POST['gender']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
 
        if password == password2:
            if MyUser.objects.filter(email=email).exists():
                messages.info(request, 'Email Already Used')
                return redirect('signup')                                                                
            else:
                new_user = MyUser.objects.create_user(email=email, password=password, date_of_birth=date_of_birth)
                new_user.name = name
                new_user.gender = gender
                new_user.save()
                return redirect('signin')
        else:
            messages.info(request, 'Password Not The Same')
            return redirect('signup')
    else:
        return render(request, 'signup.html')

from django.http import HttpResponseForbidden

def dashboard(request):
    user = request.user

    if user.is_suspended:
        return render(request, 'suspended_dashboard.html', {'balance': user.balance})
    else:
        context = {'user': user, 'account_number': user.account_number, 'balance': user.balance}
        return render(request, 'dashboard.html', context)


#deposit function
from django.shortcuts import render, redirect
from django.contrib import messages
from decimal import Decimal

from bankapp.models import Transaction

from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def deposit(request):
    if request.method == 'POST':
        amount = float(request.POST.get('amount'))
        recipient_account_number = request.POST.get('accountnumber')
        if amount <= 0:
            messages.error(request, 'Amount must be greater than zero')
        else:
            user = request.user
            recipient = MyUser.objects.get(account_number=recipient_account_number)
            recipient.balance = F('balance') + amount
            recipient.save()
            # Create a new Transaction object to record the deposit
            transaction = Transaction.objects.create(user=user, transaction_type='Deposit', amount=amount)
            transaction.save()
            messages.success(request, f'Successfully added {amount:.2f} to your account balance. deposit authorized by {user}')
            return redirect('dashboard')
    return render(request, 'deposit.html')

@staff_member_required
def withdraw(request):
    if request.method == 'POST':
        amount = float(request.POST.get('amount'))
        if amount <= 0:
            messages.error(request, 'Amount must be greater than zero')
        else:
            user = request.user
            user.withdraw(amount)
            transaction = Transaction.objects.create(user=user, transaction_type='Withdrawal', amount=amount)
            transaction.save() # add this line to save the transaction to the database
            messages.success(request, f'Successfully withdrew {amount:.2f} from your account balance.')
            return redirect('withdraw')
    return render(request, 'withdraw.html')


#trasfer function
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F
#The F() function is a very useful tool in Django for working with model fields.
#---It allows you to reference the value of a database column or field and use it in a query or a filter expression.
from .models import MyUser

@login_required
def transfer(request):
    if request.method == 'POST':
        sender = request.user
        recipient_account_number = request.POST.get('accountnumber')
        recipient_bank_name = request.POST.get('bank')
        amount = request.POST.get('amount')

        if not recipient_account_number or not recipient_bank_name or not amount:
            messages.error(request, 'Please fill all fields')
            return redirect('transfer')

        try:
            amount = float(amount)
        except ValueError:
            messages.error(request, 'Invalid amount')
            return redirect('transfer')

        if amount <= 0:
            messages.error(request, 'Invalid amount')
            return redirect('transfer')

        if sender.balance < amount:
            messages.error(request, 'Insufficient funds')
            return redirect('transfer')

        try:
            recipient = MyUser.objects.get(account_number=recipient_account_number)
        except MyUser.DoesNotExist:
            messages.error(request, 'Recipient account not found')
            return redirect('transfer')

        sender.balance = F('balance') - amount
        recipient.balance = F('balance') + amount

        sender.save()
        recipient.save()

        sender_transaction = Transaction.objects.create(user=sender, transaction_type='Sent', amount=amount)
        sender_transaction.save()
        recipient_transaction = Transaction.objects.create(user=recipient, transaction_type='Received', amount=amount)
        recipient_transaction.save()
        messages.success(request, f'Transfer to {recipient} successful ')
        return redirect('transfer')

    return render(request, 'transfer.html')


def airtime(request):
    if request.method == 'POST':
        amount = float(request.POST.get('amount'))
        network = request.POST.get('network')
        phonenumber = request.POST.get('phonenumber')
        if amount <= 0:
            messages.error(request, 'Amount must be greater than zero')
        else:
            user = request.user
            user.airtime(amount)
            transaction = Transaction.objects.create(user=user, transaction_type='Airtime', amount=amount)
            transaction.save()
            messages.success(request, f'Airtime Top up sucsessful to {phonenumber}, network:{network} amount:{amount:.2f}.')
            return redirect('dashboard')
    return render(request, 'airtime.html')

def electricity(request):
    if request.method == 'POST':
        amount = float(request.POST.get('amount'))
        biller = request.POST.get('biller')
        meternumber = request.POST.get('meternumber')
        category = request.POST.get('category')
        if amount <= 0:
            messages.error(request, 'Amount must be greater than zero')
        else:
            user = request.user
            user.electricity(amount)
            transaction = Transaction.objects.create(user=user, transaction_type='Utility', amount=amount)
            transaction.save()
            messages.success(request, f'sucsessfully recharged your {category} meter, Biller:{biller} amount:{amount:.2f}.')
            return redirect('dashboard')    
    return render(request, 'electricity.html')

@login_required
def history(request):
    # Get the current logged-in user
    user = request.user
    
    # Filter transactions based on the current user
    transactions = Transaction.objects.filter(user=user)

    return render(request, 'history.html', {'transactions': transactions})

from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .models import MyUser

@staff_member_required(login_url='signin')
def admin_dashboard(request):
    users = MyUser.objects.all()
    return render(request, 'admin_dashboard.html', {'users': users})

@staff_member_required
def admindash(request):
    # your code to authenticate the user goes here
    user = request.user 
    # account_balance = AccountBalance.objects.get(user=user)
    context = {'user': request.user, 'account_number': request.user.account_number, 'balance': request.user.balance,}
    return render(request, 'admin_dash.html', context,)

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import MyUser

def suspend_user(request, user_id):
    user = get_object_or_404(MyUser, id=user_id)
    user.is_suspended = True
    user.save()
    messages.success(request, 'User account suspended successfully.')
    return redirect('admin_dashboard')

def unsuspend_user(request, user_id):
    user = get_object_or_404(MyUser, id=user_id)
    user.is_suspended = False
    user.save()
    messages.success(request, 'User account unsuspended successfully.')
    return redirect('admin_dashboard')