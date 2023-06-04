from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .models import MyUser , Loan
from django.contrib.auth import authenticate, login
from django.contrib.auth import authenticate, login as auth_login
from django.urls import reverse
from django.utils import timezone

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
        amount = request.POST.get('amount')
        return render (request, 'tramsaction_pin')
        transaction_pin = request.POST.get('transaction_pin')
        user = request.user

        

        try:
            user.withdraw(amount, transaction_pin)
            messages.success(request, 'Withdrawal successful.')
            return redirect('dashboard')
        except ValueError as e:
            messages.error(request, str(e))

    return render(request, 'withdraw.html')


#trasfer function
from django.contrib.auth.decorators import login_required
from django.db.models import F
#The F() function is a very useful tool in Django for working with model fields.
#---It allows you to reference the value of a database column or field and use it in a query or a filter expression.

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
        customer = request.user
        amount = float(request.POST.get('amount'))
        network = request.POST.get('network')
        phonenumber = request.POST.get('phonenumber')
        if amount > customer.balance :
            messages.error(request, 'Insuficient funds')
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
        customer = request.user
        if amount > customer.balance :
            messages.error(request, 'Insuficient funds')
        else:
            user = request.user
            user.electricity(amount)
            transaction = Transaction.objects.create(user=user, transaction_type='Electricity', amount=amount)
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

@staff_member_required(login_url='signin')
def admin_dashboard(request):
    users = MyUser.objects.all()
    return render(request, 'admin_dashboard.html', {'users': users})

@staff_member_required
def adminpanel(request):
    # your code to authenticate the user goes here
    user = request.user 
    # account_balance = AccountBalance.objects.get(user=user)
    context = {'user': request.user, 'account_number': request.user.account_number, 'balance': request.user.balance,}
    return render(request, 'admin_panel.html', context,)

from django.shortcuts import get_object_or_404, redirect

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

from .models import Loan

@login_required
def apply_loan(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        # Additional fields from the loan application form
        # ...
        loan = Loan.objects.create(user=request.user, amount=amount)
        # Set any other fields on the loan object as needed
        loan.calculate_due_date()  # Calculate the due date for the loan
        loan.save()
        messages.success(request, 'Loan application submitted successfully.')
        return redirect('dashboard')
    return render(request, 'apply_loan.html')

@staff_member_required
def loan_requests(request):
    loan_requests = Loan.objects.filter(status='pending')
    return render(request, 'loan_requests.html', {'loan_requests': loan_requests})

from datetime import datetime, timedelta

@login_required
def approve_loan(request, loan_id):
    loan = get_object_or_404(Loan, id=loan_id)
    
    # Check if the loan is already approved or has been paid
    if loan.status != 'pending':
        messages.error(request, 'Loan has already been approved or paid.')
        return redirect('dashboard')

    borrower = loan.user
    borrower.balance += loan.amount
    borrower.save()

    borrower_transaction = Transaction.objects.create(user=borrower, transaction_type='Bank-Loan', amount=loan.amount)
    borrower_transaction.save()

    # Set the loan status to "approved awaiting repayment"
    loan.status = 'approved awaiting repayment'
    loan.approved_by = request.user
    loan.date_approved = datetime.now()
    loan.calculate_due_date()
    loan.save()

    messages.success(request, 'Loan approved successfully.')
    return redirect('dashboard')

@staff_member_required
def reject_loan(request, loan_id):
    loan = get_object_or_404(Loan, id=loan_id)
    loan.status = 'rejected'
    loan.save()
    messages.success(request, 'Loan rejected successfully.')
    return redirect('loan_requests')

from django.shortcuts import render ,redirect

def pending_repayment(request):
    user = request.user
    pending_loans = Loan.objects.filter(user=user, status='approved awaiting repayment')
    return render(request, 'pending_repayment.html', {'pending_loans': pending_loans})

def repay_loan(request, loan_id):
    loan = Loan.objects.get(id=loan_id)

    # Check if the loan is in the pending repayment status
    if loan.status == 'approved awaiting repayment':
        user = loan.user
        amount = loan.amount

        # Deduct the loan amount from the user's balance
        user.balance -= amount
        user.save()

        # Update the loan status to indicate repayment
        loan.status = 'repaid'
        loan.save()
        
        borrower_transaction = Transaction.objects.create(user=user, transaction_type='Repayment-Loan', amount=loan.amount)
        borrower_transaction.save()
        # Redirect the user to a success page or perform any other necessary actions
        messages.success(request, 'repayment success')
        return redirect('dashboard')

    # If the loan is not in the correct status, handle the error or redirect to an appropriate page
    messages.success(request, 'repayment failure')
    return redirect('dashboard')