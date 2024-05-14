from django.db import models
from django.utils import timezone

# Create your models here.


def _str_(self):
    return self.name


class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    CNIC = models.CharField(max_length=14, unique=True)
    phone = models.CharField(max_length=13, unique=True)
    username = models.CharField(max_length=150,unique=True, null=False,default="")  # Added username field




class Accounts(models.Model):
    SAVING = 'Saving'
    CURRENT = 'Current'
    FIXED_DEPOSIT = 'Fixed Deposit'

    ACCOUNT_TYPE_CHOICES = [
        (SAVING, 'Saving'),
        (CURRENT, 'Current'),
        (FIXED_DEPOSIT, 'Fixed Deposit'),
    ]

    ACTIVE = 'Active'
    INACTIVE = 'Inactive'

    STATUS_CHOICES = [
        (ACTIVE, 'Active'),
        (INACTIVE, 'Inactive'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=100, unique=True)
    balance = models.FloatField()
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES, default=CURRENT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=ACTIVE)
    bank_id = models.ForeignKey('Banks', on_delete=models.CASCADE, default=11)


class ATMcards(models.Model):
    VISA = 'Visa'
    MASTERCARD = 'Mastercard'
    AMERICAN_EXPRESS = 'American Express'

    CARD_TYPE_CHOICES = [
        (VISA, 'Visa'),
        (MASTERCARD, 'Mastercard'),
        (AMERICAN_EXPRESS, 'American Express'),
    ]
    accounts = models.ForeignKey(Accounts, on_delete=models.CASCADE)
    card_number = models.CharField(max_length=16, unique=True)
    pin = models.CharField(max_length=4)
    expiry_date = models.DateField()
    card_type = models.CharField(max_length=20, choices=CARD_TYPE_CHOICES)
    is_active = models.BooleanField(default=False)


class Transactions(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20)  # e.g., 'Deposit', 'Withdrawal', 'Transfer'
    description = models.TextField(blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    
class Banks(models.Model):
    name = models.CharField(max_length=100)
    swift_code = models.CharField(max_length=20,unique= True)

class Beneficiary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=20, default=0)
    name = models.CharField(max_length=100)
    bank = models.ForeignKey(Banks, on_delete=models.CASCADE, default=11)  

class UserBeneficiaryRelationship(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'beneficiary')



class Network(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class MobileNumber(models.Model):
    name = models.CharField(max_length=100, default=None)
    mobile_number = models.CharField(max_length=13)
    network = models.ForeignKey(Network, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.mobile_number})"

class MobileTopUp(models.Model):
    mobile_number = models.ForeignKey(MobileNumber, on_delete=models.CASCADE)
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Top-up for {self.mobile_number} by {self.user}"
    

class BillCompany(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class BillCustomer(models.Model):
    bill_number = models.CharField(max_length=25)
    name = models.CharField(max_length=255)
    company = models.ForeignKey(BillCompany, on_delete=models.CASCADE, related_name='customers')

    def __str__(self):
        return self.name

class UserBill(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bills')
    customer = models.ForeignKey(BillCustomer, on_delete=models.CASCADE, related_name='bills')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Bill {self.pk} for {self.user.username}'