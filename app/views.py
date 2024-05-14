from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
from django.shortcuts import get_object_or_404
from .models import User, Accounts, ATMcards, Transactions,Banks, Beneficiary, MobileTopUp, MobileNumber, Network, BillCompany, BillCustomer, UserBill
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.utils import timezone
from django.db.models import Q




services = [
        {"name": "Fund Transfer", "url": "beneficiary", "icon": "bi-broadcast", "description": ""},
        {"name": "Mobile Top Up", "url": "mobile_top_up", "icon": "bi-broadcast", "description": ""},
        {"name": "Bill Payments", "url": "billpayment", "icon": "bi-broadcast", "description": ""},
        {"name": "Card Detail", "url": "carddetail", "icon": "bi-broadcast", "description": ""}, 
        {"name": "Transaction Details", "url": "transactionDetails", "icon": "bi-broadcast", "description": ""}, 
        {"name": "Account Statement", "url": "statement", "icon": "bi-broadcast", "description": ""},    
        {"name": "Account Info", "url": "accountInfo", "icon": "bi-broadcast", "description": ""},
    ]

def login(request):
    if 'user' in request.session:
        del request.session['user']
        
    if request.method == 'POST':
        if request.POST.get('Username_signup') and request.POST.get('Account_no'):
            username = request.POST.get('Username_signup')
            account_number = request.POST.get('Account_no')
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already taken. Please choose another one.')
                return redirect('signup')

            try:
                acc = Accounts.objects.get(account_number=request.POST.get('Account_no'))
                user = User.objects.get(id=acc.user_id)
                
                user.username = username
                user.password = request.POST.get('Password_signup1')
                user.save()
                
                messages.success(request, 'Account created successfully, please log in.')
                return redirect('login')
            
            except ObjectDoesNotExist:
                messages.error(request, 'Incorrect Account No or CNIC')  
                return redirect('login') 
        else:
            uname = request.POST.get('Username_signin')
            pword = request.POST.get('Password_signin')
            try:
                user = User.objects.get(username=uname)
                if (pword == user.password):  
                    request.session['user'] = user.id  
                    return redirect('dashboard') 
                else:
                    messages.error(request, "Invalid login credentials.")
            except User.DoesNotExist:
                messages.error(request, "User does not exist.")
            return redirect('login')  

    return render(request, 'authentication/index.html')


def recovery_password(request):
    if 'user' in request.session:
        del request.session['user']

    return render(request, 'authentication/recovery.html')


def verify_credentials(request):
    if request.method == 'POST':
        cnic = request.POST.get('cnic')
        account_no = request.POST.get('account_no')
        try:
            user = User.objects.get(CNIC=cnic)
            account = Accounts.objects.get(account_number=account_no, user=user)
            return JsonResponse({'success': True, 'user_id': user.id})
        except (User.DoesNotExist, Accounts.DoesNotExist):
            return JsonResponse({'success': False, 'error': 'Invalid CNIC or Account Number'}, status=404)

    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


def update_password(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            return JsonResponse({'success': False, 'error': 'Passwords do not match.'}, status=400)

        try:
            user = User.objects.get(id=user_id)
            user.set_password(new_password)  # Django's set_password method hashes the password
            user.save()
            return JsonResponse({'success': True, 'message': 'Password updated successfully.'})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User not found.'}, status=404)

    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

def dashboard(request):
    if 'user' in request.session: 
        return render(request, 'dashboard/index.html' ,{'services': services})
    else:
        messages.error(request, "You must be logged in to view the dashboard.")
        return redirect('login')  


def billpayment(request):
    user_id = request.session.get('user')
    user = get_object_or_404(User, pk=user_id)
    account = get_object_or_404(Accounts, user=user)
    bills = UserBill.objects.filter(user_id=user).select_related('customer', 'customer__company')
    billcompanies = BillCompany.objects.all()
    print(bills)
    return render(request, 'dashboard/billpayment.html', {
        'User': user,
        'billcompanies': billcompanies,
        'bills': bills,
        'account': account,
        'services': services
    })


def addbill(request):
    if request.method == 'POST':
        billcompany = request.POST.get('bill')
        number = request.POST.get('bill_number')
        user_id = request.session.get('user')

        if not all([billcompany, number]):
            return HttpResponseBadRequest('Missing required fields.')

        try:
            billcompany = int(billcompany)
        except ValueError:
            return HttpResponseBadRequest('Invalid Bill ID.')

        number = number.strip()

        print(f"Checking combination: Bill Comapny ID={billcompany}, Bill Number={number}")

        billcom = get_object_or_404(BillCompany, pk=billcompany)

        try:
            bill_number_instance = BillCustomer.objects.get(
                bill_number=number,
                company=billcompany
            )
            print(f"Found Bill number: {bill_number_instance}")
        except BillCustomer.DoesNotExist:
            print(f"Combination not found: Bill number '{number}' and Bill Company ID '{billcompany}'")
            return HttpResponseBadRequest('The Bill number and Company combination does not exist.')

        user = get_object_or_404(User, pk=user_id)

        user_bill_instance = UserBill.objects.create(
            customer=bill_number_instance,
            user=user,
            timestamp=timezone.now()
        )

        return JsonResponse({'message': 'Bill added successfully!'})

    return HttpResponseBadRequest('Invalid request method.')



def paybill(request):
    user_id = request.session.get('user')
    user = get_object_or_404(User, pk=user_id)
    name = request.GET.get('name')
    bill_no = request.GET.get('bill_no')
    curr_balance = request.GET.get('balance')
    account = Accounts.objects.get(user_id=user)
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        if account.balance < float(amount):
            return JsonResponse({'status': 'error', 'message': 'Insufficient balance.'}, status=400)
        else:
            account.balance -= float(amount)
            account.save()
            
            trans_debit = Transactions(
                amount=float(amount),
                transaction_type='Bill Payment',
                description='Bill Payed to bill number ' + bill_no,
                user_id=user.id
            )
            trans_debit.save()
            
            return JsonResponse({'status': 'success', 'message': 'Bill Payed successful.'}, status=200)

    return render(request, 'dashboard/paybill.html', {
        'User': user,
        'curr_balance': curr_balance,
        'account': account,
        'services': services
    })


def card(request):
    user_id = request.session.get('user')  # Make sure this session key is correct
    user = get_object_or_404(User, pk=user_id)
    account = get_object_or_404(Accounts, user_id=user)  # Use user instance here
    card = get_object_or_404(ATMcards, accounts_id=account)  # Use account instance here
    return render(request, 'dashboard/carddetail.html',{'card': card, 'account': account,'services': services,'user': user})

from django.http import JsonResponse

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import User, Accounts, Transactions

def fundtransfer(request):
    beneficiary_name = request.GET.get('name')
    account_number = request.GET.get('account')
    bank_id = request.GET.get('bank', '')
    curr_balance = request.GET.get('balance')
    user = User.objects.get(id=request.session.get('user'))
    account = Accounts.objects.get(user_id=user)
    if request.method == 'POST':
        amount = request.POST.get('amount')
        if account.balance < float(amount):
            return JsonResponse({'status': 'error', 'message': 'Insufficient balance.'}, status=400)
        
        if Accounts.objects.filter(account_number=account_number).exists() and account_number != account.account_number:
            reciver = Accounts.objects.get(account_number=account_number)
            account.balance -= float(amount)
            account.save()
            trans_debit = Transactions(
                amount=float(amount),
                transaction_type='debit',
                description='Funds transferred to account number ' + account_number,
                user_id=user.id
            )
            trans_debit.save()

            if bank_id == '11':  # Assuming '11' is the ID for intra-bank transfers
                reciver.balance += float(amount)
                reciver.save()
                trans_credit = Transactions(
                    amount=float(amount),
                    transaction_type='credit',
                    description='Funds received from account number ' + account.account_number,
                    user_id=reciver.user_id 
                )
                trans_credit.save()

            return JsonResponse({'status': 'success', 'message': 'Funds transferred successfully.'})
        
    return render(request, 'dashboard/fundtransfer.html', {'services': services, 'beneficiary_name': beneficiary_name, 'account_number': account_number , 'curr_balance': curr_balance})


def about(request):
    return render(request, 'dashboard/about.html')

def accountInfo(request):
    user_id = request.session.get('user')  # Make sure this session key is correct
    user = get_object_or_404(User, pk=user_id)
    account = get_object_or_404(Accounts, user_id=user)  # Use user instance here
    card = get_object_or_404(ATMcards, accounts_id=account)  # Use account instance here
    print(user,account,card)
    print(card.expiry_date)
    return render(request,'dashboard/accountInfo.html',{'User' : user, 'Account' : account,'ATMcards': card, 'services': services})

def transactionDetails(request):
    user_id=request.session.get('user')
    user=get_object_or_404(User,pk=user_id)
    transactions = Transactions.objects.filter(
    Q(user_id=user) & (Q(transaction_type='debit') | Q(transaction_type='Top up') | Q(transaction_type='Bill Payment'))
    )
    print(transactions)
    return render(request, 'dashboard/transactionDetails.html',{'transactions': transactions,'services' : services,'User':user})

def statement(request):
    user_id=request.session.get('user')
    user=get_object_or_404(User,pk=user_id)
    transactions = Transactions.objects.filter(user_id=user) 
    return render(request, 'dashboard/statement.html',{'transactions': transactions,'services' : services,'User':user})

from django.shortcuts import get_object_or_404, render

def beneficiary(request):
    user_id = request.session.get('user')
    user = get_object_or_404(User, pk=user_id)
    account = get_object_or_404(Accounts, user_id=user)
    beneficiaries = Beneficiary.objects.filter(user=user).select_related('bank')
    banks = Banks.objects.all()
    print(account.balance) 
    return render(request, 'dashboard/beneficiary.html', {
        'beneficiaries': beneficiaries,
        'services': services,
        'banks': banks,
        'account': account
    })


def addbeneficiary(request):
    if request.method == 'POST':
        user_id = request.session.get('user')
        account_no = request.POST.get('account_number')
        bank_id = request.POST.get('bank') 
        
        if not account_no or not bank_id:
            return JsonResponse({'error': 'Missing account number or bank ID'}, status=400)

        
        try:
            bank_id = int(bank_id)
            bank = Banks.objects.get(id=bank_id)
        except (ValueError, Banks.DoesNotExist):
            return JsonResponse({'error': 'Invalid bank selection'}, status=400)

        # Check if the account number exists in the Account table
        try:
            account = Accounts.objects.get(account_number=account_no)
        except Accounts.DoesNotExist:
            return JsonResponse({'error': 'Account not found'}, status=404)

        # Check if the user is trying to add his own account
        user_accounts = Accounts.objects.filter(user_id=user_id).values_list('account_number', flat=True)
        if account_no in user_accounts:
            return JsonResponse({'error': 'Cannot add your own account as a beneficiary'}, status=400)
        
        beneficiary = Beneficiary(
            user_id=user_id,
            account_number=account_no,
            bank_id=bank_id
        )

        beneficiary.name = request.POST.get('beneficiary_name') 
        try:
            beneficiary.save()
            return JsonResponse({'message': 'Beneficiary added successfully!'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


def mobile_top_up(request):
    user_id = request.session.get('user')
    user = get_object_or_404(User, pk=user_id)
    account = get_object_or_404(Accounts, user=user)
    top_ups = MobileTopUp.objects.filter(user_id=user).select_related('mobile_number', 'mobile_number__network')
    networks = Network.objects.all()

    return render(request, 'dashboard/mobiletopup.html', {
        'User': user,
        'networks': networks,
        'top_ups': top_ups,
        'account': account,
        'services': services
    })


def add_mobile_top_up(request):
    if request.method == 'POST':
        network_id = request.POST.get('network')
        number = request.POST.get('mobile_number')
        user_id = request.session.get('user')

        if not all([network_id, number]):
            return HttpResponseBadRequest('Missing required fields.')

        try:
            network_id = int(network_id)
        except ValueError:
            return HttpResponseBadRequest('Invalid network ID.')

        number = number.strip()

        print(f"Checking combination: Network ID={network_id}, Mobile Number={number}")

        network = get_object_or_404(Network, pk=network_id)

        try:
            mobile_number_instance = MobileNumber.objects.get(
                mobile_number=number,
                network=network
            )
            print(f"Found mobile number: {mobile_number_instance}")
        except MobileNumber.DoesNotExist:
            print(f"Combination not found: Mobile number '{number}' and network ID '{network_id}'")
            return HttpResponseBadRequest('The mobile number and network combination does not exist.')

        user = get_object_or_404(User, pk=user_id)

        mobile_top_up_instance = MobileTopUp.objects.create(
            mobile_number=mobile_number_instance,
            user=user,
            timestamp=timezone.now()
        )

        return JsonResponse({'message': 'Mobile Top Up added successfully!'})


def send_top_up(request):
    user_id = request.session.get('user')
    user = get_object_or_404(User, pk=user_id)
    name = request.GET.get('name')
    mobile_no = request.GET.get('mobile_no')
    curr_balance = request.GET.get('balance')
    account = Accounts.objects.get(user_id=user)
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        if account.balance < float(amount):
            return JsonResponse({'status': 'error', 'message': 'Insufficient balance.'}, status=400)
        else:
            account.balance -= float(amount)
            account.save()
            
            trans_debit = Transactions(
                amount=float(amount),
                transaction_type='Top up',
                description='Mobile Top to mobile number ' + mobile_no,
                user_id=user.id
            )
            trans_debit.save()
            
            return JsonResponse({'status': 'success', 'message': 'Top-up successful.'}, status=200)

    return render(request, 'dashboard/sendtopup.html', {
        'User': user,
        'curr_balance': curr_balance,
        'account': account,
        'services': services
    })
