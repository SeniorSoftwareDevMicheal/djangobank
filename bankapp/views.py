#imports
from django.shortcuts import render, redirect, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .models import MyUser , Loan
from django.contrib.auth import authenticate, login
from django.contrib.auth import authenticate, login as auth_login
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from bankapp.models import Transaction, Contact
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseForbidden
from django import forms

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

def dashboard(request):
    user = request.user

    if user.is_suspended:
        return render(request, 'suspended_dashboard.html', {'balance': user.balance})
    else:
        context = {'user': user, 'account_number': user.account_number, 'balance': user.balance}
        return render(request, 'dashboard.html', context)

def base(request):
    user = request.user

    if user.is_suspended:
        return render(request, 'suspended_dashboard.html', {'balance': user.balance})
    else:
        context = {'user': user, 'account_number': user.account_number, 'balance': user.balance}
        return render(request, 'base.html', context)

def more_services(request):
    user = request.user

    if user.is_suspended:
        return render(request, 'suspended_dashboard.html', {'balance': user.balance})
    else:
        context = {'user': user, 'account_number': user.account_number, 'balance': user.balance}
        return render(request, 'more_services.html', context)
    
def userprofile(request):
    user = request.user

    if user.is_suspended:
        return render(request, 'suspended_dashboard.html', {'balance': user.balance})
    else:
        context = {'user': user, 'account_number': user.account_number, 'balance': user.balance}
        return render(request, 'userprofile.html', context)
    
@staff_member_required
def deposit(request):
    if request.method == 'POST':
        amount = float(request.POST.get('amount'))
        recipient_account_number = request.POST.get('accountnumber')
        
        try:
            recipient = MyUser.objects.get(account_number=recipient_account_number)
        except MyUser.DoesNotExist:
            messages.error(request, 'Recipient account not found')
            return render(request, 'deposit.html')
        
        if amount <= 0:
            messages.error(request, 'Amount must be greater than zero')
        else:
            user = request.user
            recipient.balance = F('balance') + amount
            recipient.save()
            
            transaction = Transaction.objects.create(user=user, transaction_type='Deposit', amount=amount)
            transaction.save()
            
            messages.success(request, f'Successfully added {amount:.2f} to account balance of {recipient_account_number}. Deposit authorized by {user}')
            return redirect('dashboard')
    
    return render(request, 'deposit.html')


@staff_member_required
def withdraw(request):
    if request.method == 'POST':
        amount = float(request.POST.get('amount'))
        customer = request.user
        if amount > customer.balance :
            messages.error(request, 'Insuficient funds')
        else:
            user = request.user
            user.withdraw(amount)
            transaction = Transaction.objects.create(user=user, transaction_type='Withdrawal', amount=amount)
            transaction.save() # add this line to save the transaction to the database
            messages.success(request, f'Successfully withdrew {amount:.2f} from your account balance.')
            return redirect('withdraw')
    return render(request, 'withdraw.html')

#trasfer function
from django.db.models import F
#The F() function is a very useful tool in Django for working with model fields.
#---It allows you to reference the value of a database column or field and use it in a query or a filter expression.

@login_required
def transfer(request):
    if request.method == 'POST':
        # Get the entered transaction PIN from the form
        transaction_pin = request.POST.get('password')

        # Verify the transaction PIN against the user's saved PIN
        if transaction_pin != request.user.transaction_pin:
            messages.error(request, 'Invalid transaction PIN.If you have not set your pin check user-profile')
            return redirect('transfer')

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
        messages.success(request, f'Transfer to {recipient} successful')
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

def pending_repayment(request):
    user = request.user
    pending_loans = Loan.objects.filter(user=user, status='approved awaiting repayment')
    return render(request, 'pending_repayment.html', {'pending_loans': pending_loans})

def repay_loan(request, loan_id):
    loan = Loan.objects.get(id=loan_id)

    # Check if the loan is in the pending repayment status
    if loan.status == 'approved awaiting repayment':
        user = loan.user
        loan_amount = loan.amount
        interest_rate = loan.interest_rate/100  # 14% interest rate or could be dynamic <3

        # Calculate the interest amount
        interest_amount = loan_amount * interest_rate

        # Deduct the loan amount and interest from the user's balance
        total_amount = loan_amount + interest_amount
        user.balance -= total_amount
        transaction = Transaction.objects.create(user=user, transaction_type='Loan', amount=total_amount)
        user.save()

        # Update the loan status to indicate repayment
        loan.status = 'repaid'
        loan.save()

        # Redirect the user to a success page or perform any other necessary actions
        messages.success(request, 'Repayment successful. Loan and interest amount deducted.')
        return redirect('dashboard')

    # If the loan is not in the correct status, handle the error or redirect to an appropriate page
    messages.error(request, 'Repayment failed. Loan is not in the correct status.')
    return redirect('dashboard')

@login_required
def set_transaction_pin(request):
    if request.method == 'POST':
        # Get the entered transaction PIN from the form
        transaction_pin = request.POST.get('transaction_pin')
        confirm_pin = request.POST.get('confirm_pin')

        # Validate the transaction PIN
        if len(transaction_pin) != 4 or not transaction_pin.isdigit():
            messages.error(request, 'Invalid transaction PIN.')
            return redirect('set_transaction_pin')

        # Confirm the transaction PIN
        if transaction_pin != confirm_pin:
            messages.error(request, 'Transaction PIN does not match the confirmation')
            return redirect('set_transaction_pin')

        # Save the transaction PIN for the logged-in user
        request.user.transaction_pin = transaction_pin
        request.user.save()

        messages.success(request, 'Transaction PIN set successfully')
        return redirect('transfer')

    return render(request, 'set_transaction_pin.html')


@login_required
def reset_transaction_pin(request):
    if request.method == 'POST':
        # Get the entered transaction PIN from the form
        transaction_pin = request.POST.get('transaction_pin')
        confirm_pin = request.POST.get('confirm_pin')

        # Validate the transaction PIN
        if len(transaction_pin) != 4 or not transaction_pin.isdigit():
            messages.error(request, 'Invalid transaction PIN')
            return redirect('set_transaction_pin')

        # Confirm the transaction PIN
        if transaction_pin != confirm_pin:
            messages.error(request, 'Transaction PIN does not match the confirmation')
            return redirect('set_transaction_pin')

        # Reset the transaction PIN for the logged-in user
        request.user.transaction_pin = transaction_pin
        request.user.save()

        messages.success(request, 'Transaction PIN reset successfully')
        return redirect('transfer')

    return render(request, 'set_transaction_pin.html')

def contact(request):
    if request.method=="POST":
        contact=Contact()
        name=request.POST.get('Name')
        email=request.POST.get('Email')
        message=request.POST.get('Message')
        contact.Name=name
        contact.Email=email
        contact.Message=message
        contact.save()
        return render(request, 'success.html')
    return render(request, 'contactus.html')

def success(request):
    return render(request, 'success.html')

class ContactForm(forms.Form):
    Name = forms.CharField(max_length=100)
    Email = forms.EmailField()
    Message = forms.CharField(widget=forms.Textarea)
