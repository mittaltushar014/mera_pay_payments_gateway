'''Models required in the website'''

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from decimal import Decimal
from datetime import datetime


class Profile(AbstractUser):
    # Model for recording all users basic profile

    '''
    username - from Inbuilt User table
    first_name - from Inbuilt User table
    last_name - from Inbuilt User table   
    email - from Inbuilt User table
    date_joined - from Inbuilt User table
    password - from Inbuilt User table '''

    phone = models.IntegerField(unique=True, null=True)
    wallet = models.DecimalField(default=Decimal(
        1000.0), decimal_places=2, max_digits=64, null=True)
    profile_type = models.CharField(max_length=50, null=True)
    credit_number = models.IntegerField(default=1000, null=True)
    debit_number = models.IntegerField(default=10000, null=True)
    debit_balance = models.IntegerField(default=50000, null=True)
    credit_balance = models.IntegerField(default=50000, null=True)

    def __str__(self):
        return "{}".format(self.username)


class Price(models.Model):
    price = models.IntegerField(default=0, null=True)
    # price = models.DecimalField(default=Decimal(
    #     0.0), decimal_places=10, max_digits=64, null=True)

    def __str__(self):
        return "{}".format(self.price)


class Service(models.Model):
    # Model for registering the services

    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='image', blank=True)
    business_profile = models.ManyToManyField(
        "BusinessProfile", blank=True, related_name="business_of_services")
    price = models.ForeignKey(Price, on_delete=models.CASCADE)
    description = models.CharField(
        max_length=100, default="No Description Added")

    def __str__(self):
        return "{}".format(self.name)


class BusinessProfile(models.Model):
    # Model for recording business profile

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             null=True, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=100, unique=True)
    register_date = models.DateTimeField(default=timezone.now)
    pan_number = models.IntegerField(unique=True)
    pan_name = models.CharField(max_length=100)
    address = models.TextField(max_length=200)
    pincode = models.IntegerField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    business_url_endpoint = models.CharField(max_length=200, null=True)

    service = models.ManyToManyField(
        "Service", blank=True, related_name="services_of_business")

    def __str__(self):
        return "{}".format(self.business_name)


class Transaction(models.Model):
    # Model for recording transactions.

    by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True,
                           on_delete=models.SET_NULL, related_name='by_profile')
    to = models.ForeignKey("BusinessProfile", null=True,
                           on_delete=models.SET_NULL, related_name='to_profile')
    amount = models.IntegerField(default=0)
    service = models.ForeignKey(
        "Service", null=True, on_delete=models.SET_NULL)
    date = models.DateField(default=timezone.now)
    time = models.TimeField(default=timezone.now)

    def __str__(self):
        return "Transaction by {} to {} on {}".format(self.by, self.to, self.date, self.time)
