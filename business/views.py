'''Views file for business'''

from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages

from django.contrib.auth import authenticate, login, logout as django_logout
from django.contrib.auth.decorators import login_required

from .models import Profile, Service, BusinessProfile, Transaction
from django.contrib.auth import get_user_model

from django.core.mail import send_mail
from random import randint
from django.utils import timezone
import datetime
from decimal import Decimal

from .serializers import ProfileSerializer, BusinessProfileSerializer
from rest_framework import generics, mixins
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from customers.views import index_individual, individual_transaction
from urllib.parse import urlencode

import csv
import random
from django.http import JsonResponse
from django.views.generic import TemplateView
import plotly.express as px
from plotly.offline import plot
from plotly.graph_objs import Scatter

User = get_user_model()

otp = 0


def home(request):
    # For rendering to home
    
    return render(request, 'home.html')


def registration(request):
    # For all users registration

    if request.method == "POST":
        username = request.POST['username']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        email = request.POST['email']
        phone = request.POST['phone']
        profile_type = 'business'
        Error = 0
        message_error = []
        credit_number = randint(10000000000000000, 99999999999999999)
        debit_number = randint(1000000000000, 9999999999999)

        if len(username) < 5:
            Error = Error + 1
            message_error = message_error + \
                ['Length of user must be atleast five digit']

        if User.objects.filter(username=username).exists():
            Error = Error + 1
            message_error = message_error + ['Username already exists']

        if User.objects.filter(first_name=first_name).exists():
            Error = Error + 1
            message_error = message_error + ['First name already exists']

        # if User.objects.filter(email=email).exists():
        #     Error = Error + 1
        #     message_error = message_error + ['Email registered with different account']

        if User.objects.filter(phone=phone).exists():
            Error = Error + 1
            message_error = message_error + \
                ['Phone registered with different account']
        check = True

        while check:
            if User.objects.filter(credit_number=credit_number).exists():
                credit_number = randint(10000000000000000, 99999999999999999)
            else:
                check = False
        check = True

        while check:
            if User.objects.filter(debit_number=debit_number).exists():
                debit_number = randint(1000000000000, 9999999999999)
            else:
                check = False

        if Error > 0:
            return render(request, 'register.html', {'messages': message_error})

        user = User.objects.create_user(username=username, password=request.POST.get('password'),
                                        email=email, first_name=first_name,
                                        last_name=last_name, phone=phone, profile_type=profile_type, credit_number=credit_number, debit_number=debit_number)
        user.save()

        global otp
        otp = randint(100000, 999999)
        send_mail('django_test', str(otp), 'mishrapravin214@gmail.com', [
                  email], fail_silently=False)

        login(request, user)
        return render(request, 'otp.html', {'user': request.user})

    return render(request, 'register.html')


def otp_verification(request):
    # For otp verification

    if request.method == "POST":
        userotp = request.POST['otp']
        if str(otp) == userotp:
            service = Service.objects.all()
            return render(request, 'business_signup.html', {'service': service})
        else:
            messages.error(request, "Invalid OTP! Please try again!")
            return render(request, "register.html")

    return render(request, "otp.html")


def business_signup(request):
    # For registering business details

    if request.method == "POST":
        business_profile = BusinessProfile(business_name=request.POST.get("business_name"),
                                           pan_number=request.POST.get(
                                               "pan_number"),
                                           pan_name=request.POST.get(
                                               "pan_name"),
                                           address=request.POST.get("address"),
                                           pincode=request.POST.get("pincode"),
                                           city=request.POST.get("city"),
                                           state=request.POST.get("state"))

        service_name = request.POST.get("service")

        business_profile.user = request.user
        business_profile.save()

        service = Service.objects.filter(name=service_name).first()
        service.save()

        business_profile_service_list = []
        services = Service.objects.prefetch_related(
            'business_profile').filter(business_profile__user=request.user)

        for index, current_service in enumerate(services):
            if current_service in business_profile_service_list:
                messages.success(request, "You Service already exists!")
                service = Service.objects.all()
                return render(request, 'business_signup.html', {'service': service})
            else:
                business_profile_service_list = business_profile_service_list + \
                    [current_service]

        service.business_profile.add(business_profile)
        business_profile.service.add(
            Service.objects.filter(name=service_name).first())

        service_list = Service.objects.all()
        services = Service.objects.prefetch_related(
            'business_profile').filter(business_profile__user=request.user)
        messages.success(request, "You details are added successfully added!")
        return render(request, 'business_home.html', {'services': services, 'service_list': service_list})

    service = Service.objects.all()
    return render(request, 'business_signup.html', {'service': service})


def loginUser(request):
    # For logging all type of users

    if request.method == "POST":
        username = request.POST.get('username')

        user = authenticate(username=username,
                            password=request.POST.get('password'))

        if user is not None:
            login(request, user)
            messages.success(request, "Login Successful! You are welcome!")
            services = Service.objects.prefetch_related(
                'business_profile').filter(business_profile__user=request.user)
            service_list = Service.objects.all()
            return render(request, 'business_home.html', {'services': services, 'service_list': service_list})
        else:
            messages.error(request, "Invalid credentials! Please try again!")
            return redirect('home')

    return render(request, 'login.html')


@login_required
def logoutUser(request):
    # For logging out of user

    django_logout(request)
    return render(request, 'main.html')


@login_required
def business_index(request):
    # For rendering index page

    logged_in_user = User.objects.filter(
        username=request.user.username).first()
    return render(request, 'index.html', {'credit_num': logged_in_user.credit_number, 'debit_num': logged_in_user.debit_number, 'credit_bal': logged_in_user.credit_balance, 'debit_bal': logged_in_user.debit_balance})


@login_required
def business_home(request):
    # For rendering business page

    services = Service.objects.prefetch_related(
        'business_profile').filter(business_profile__user=request.user)
    service_list = Service.objects.all()
    logged_in_user = User.objects.filter(
        username=request.user.username).first()
    return render(request, 'business_home.html', {'services': services, 'service_list': service_list, 'balance': logged_in_user.wallet, 'credt_bal': logged_in_user.credit_balance, 'debit_bal': logged_in_user.debit_balance})


@login_required
def business_service_add(request):
    # For adding service to business profile

    if request.method == "POST":
        service_name = request.POST.get("service")
        business_profile = BusinessProfile.objects.filter(
            user=request.user).first()
        business_profile.service.add(
            Service.objects.filter(name=service_name).first())
        service = Service.objects.filter(name=service_name).first()
        service.save()
        service.business_profile.add(business_profile)
        service_list = Service.objects.all()
        services = Service.objects.prefetch_related(
            'business_profile').filter(business_profile__user=request.user)
        messages.success(request, "Your details are added successfully added!")

        return render(request, 'business_home.html', {'services': services, 'service_list': service_list})


@login_required
def pay_link(request):
    #For pay link generation

    service_name = request.GET.get('service_name')
    service_owner = request.GET.get('service_owner')
    service_price = request.GET.get('service_price')
    payment_type = request.GET.get('payment_type')

    end_point = 'http://127.0.0.1:8000/pay_link/?'
    link_dict = {'service_name': service_name, 'service_owner': service_owner,
                 'service_price': service_price, 'payment_type': payment_type}
    link = end_point + urlencode(link_dict)

    return render(request, 'payment.html', {'link': link, 'service_name': service_name, 'service_owner': service_owner, 'service_price': service_price, 'payment_type': payment_type})


@login_required
def individual_pay(request, service_name, service_owner, service_price, payment_type):
    #For paying to the business by individual

    service_owner = str(service_owner)

    logged_in_user = User.objects.filter(
        username=request.user.username).first()

    if payment_type == 'credit':
        if logged_in_user.credit_balance - service_price <= 0:
            messages.warning(
                request, 'Sorry, you dont have sufficient balance in your Credit Card!')
            return redirect('index_individual')
        logged_in_user.credit_balance = logged_in_user.credit_balance - service_price

    elif payment_type == 'wallet':
        if logged_in_user.wallet - service_price <= 0:
            messages.warning(
                request, 'Sorry, You dont have sufficient balance in Wallet!')
            return redirect('index_individual')
        logged_in_user.wallet = logged_in_user.wallet - service_price

    elif payment_type == 'debit':
        if logged_in_user.debit_balance - service_price <= 0:
            messages.warning(
                request, 'Sorry, you dont have sufficient balance in your Debit Card!')
            return redirect('index_individual')
        logged_in_user.debit_balance = logged_in_user.debit_balance - service_price

    logged_in_user.save()

    business_user = User.objects.filter(username=service_owner).first()
    business_user.wallet += service_price
    business_user.save()

    transaction = Transaction.objects.create(by=request.user,
                                             to=BusinessProfile.objects.filter(user=User.objects.filter(
                                                 username=service_owner).first()).first(),
                                             amount=service_price, service=Service.objects.filter(name=service_name).first())
    transaction.save()

    logged_in_user = User.objects.filter(
        username=request.user.username).first()

    messages.success(request, 'Payment successful!')
    return redirect('individual_transaction')


@login_required
def business_transaction(request):
    # For business transactions table rendering

    transactions = Transaction.objects.filter(to=BusinessProfile.objects.filter(
        user=request.user).first()).order_by('-date', '-time')
    messages.success(request, "Welcome to the transactions page!")
    return render(request, 'business_transaction.html', locals())


@login_required
def export_transaction(request):
    # For exporting transactions

    response = HttpResponse(content_type='text/csv')

    writer = csv.writer(response)
    writer.writerow(['From - Username', 'First Name', 'Last Name', 'To', 'Amount', 'Service', 'Date', 'Time'])

    for transaction in Transaction.objects.select_related('by', 'to', 'service').filter(to=BusinessProfile.objects.filter(user=request.user).first()).values_list('by__username', 'by__first_name', 'by__last_name', 'to__business_name', 'amount', 'service__name', 'date', 'time'):
        writer.writerow(transaction)

    response['Content-Disposition'] = 'attachment;filename="transactions.csv"'
    messages.success(
        request, "Your transactions file was downloaded successfully!")
    return response


@login_required
def business_analysis(request):
    # For business analyis charts rendering


    # day_wise_earning
    x1_data = []
    y1_data = []

    transactions = Transaction.objects.filter(
        to=BusinessProfile.objects.filter(user=request.user).first()).order_by('date')

    for transaction in transactions:
        x1_data.append(transaction.date)
        y1_data.append(transaction.amount)

    fig = px.bar(x=x1_data, y=y1_data, labels={'x': "Day", 'y': 'Amount'})
    daywise = fig.to_html(full_html=False)


    #service_wise_earning
    x1_data = []
    y1_data = []
  
    transactions_business = Transaction.objects.select_related('by', 'to', 'service').filter(to=BusinessProfile.objects.filter(user=request.user).first()).values_list('by__username', 'to__business_name', 'amount', 'service__name', 'date', 'time')
    
    service_wise_earning ={}

    for transaction in transactions_business:
        if transaction[3] not in service_wise_earning.keys():
            service_wise_earning[transaction[3]] = transaction[2]
        else:
            service_wise_earning[transaction[3]] += transaction[2]

    x1_data = list(service_wise_earning.keys())
    y1_data = list(service_wise_earning.values())

    fig = px.bar(x=x1_data, y=y1_data, labels={'x': "Service", 'y': 'Amount'})
    service_earning = fig.to_html(full_html=False)


    #month_wise_earning
    month_wise_earning ={}

    for transaction in transactions_business:
        if transaction[4].month not in month_wise_earning.keys():
            month_name = datetime.date(2020, transaction[4].month, 1).strftime('%B')
            month_wise_earning[month_name] = transaction[2]
        else:
            month_wise_earning[month_name] += transaction[2]        

    x1_data = list(month_wise_earning.keys())
    y1_data = list(month_wise_earning.values())

    fig = px.bar(x=x1_data, y=y1_data, labels={'x': "Month", 'y': 'Amount'})
    month_earning = fig.to_html(full_html=False)


    #day_wise_traffic
    x1_data = []
    y1_data = []

    transactions_per_month = Transaction.objects.filter(to=BusinessProfile.objects.filter(
        user=request.user).first()).values_list("date").order_by("-date")
    no_of_services_per_month_dict = {}

    for i in transactions_per_month:
        if i[0] in no_of_services_per_month_dict:
            no_of_services_per_month_dict[i[0]] += 1
        else:
            no_of_services_per_month_dict[i[0]] = 1

    x1_data = list(no_of_services_per_month_dict.keys())
    y1_data = list(no_of_services_per_month_dict.values())

    fig = px.line(x=x1_data, y=y1_data, labels={'x': "Day", 'y': 'Times'})
    service_per_month = fig.to_html(full_html=False)


    #service_wise_traffic
    x1_data = []
    y1_data = []

    no_of_service_used = Transaction.objects.filter(to=BusinessProfile.objects.filter(
        user=request.user).first()).values_list("service_id")

    service_type = Service.objects.values_list("id", "name")
    no_of_times_each_service_used_dict = {}

    for ser in no_of_service_used:
        temp = service_type[ser[0]-1][1]
        if temp in no_of_times_each_service_used_dict:
            no_of_times_each_service_used_dict[temp] += 1
        else:
            no_of_times_each_service_used_dict[temp] = 1

    x1_data = list(no_of_times_each_service_used_dict.keys())
    y1_data = list(no_of_times_each_service_used_dict.values())

    fig = px.pie(values=y1_data, names=x1_data)
    number_times_service = fig.to_html(full_html=False)


    #service_wise_subscribers
    service_wise_subscribers ={}
    temp_subscribers=[]

    for transaction in transactions_business:
        if transaction[3] not in service_wise_subscribers.keys():
            if transaction[0] not in temp_subscribers:
                temp_subscribers.append(transaction[3])
                service_wise_subscribers[transaction[3]] = 1
            else:
                service_wise_subscribers[transaction[3]] += 1    
        else:
            if transaction[0] not in temp_subscribers:
                temp_subscribers.append(transaction[3])
                service_wise_subscribers[transaction[3]] = 1
            else:
                service_wise_subscribers[transaction[3]] += 1       

    x1_data = list(service_wise_subscribers.keys())
    y1_data = list(service_wise_subscribers.values())

    fig = px.pie(values=y1_data, names=x1_data)
    service_subscribers = fig.to_html(full_html=False)
    
    messages.success(request, "Welcome to the analysis page!")
    return render(request, 'business_analysis.html', {'daywise': daywise,
                                                      'service_per_month': service_per_month,
                                                      'number_times_service': number_times_service,
                                                      'service_earning' : service_earning,
                                                      'month_earning' : month_earning,
                                                      'service_subscribers' : service_subscribers})


@login_required
def about(request):
    # About business

    return render(request, 'about.html')


class BusinessProfileDetail(APIView):
    # For serializing business profile data

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'business_profile.html'

    def get(self, request, pk):
        profile = get_object_or_404(BusinessProfile, pk=pk)
        serializer = BusinessProfile(profile)
        return Response({'serializer': serializer, 'profile': profile})


@login_required
def business_profile(request):
    # For rendering business profile

    logged_in_user = User.objects.filter(
        username=request.user.username).first()
    return render(request, 'business_profile.html', {'logged_in_user': logged_in_user})


def error_400(request, exception):
    return render(request, '400.html')


def error_403(request, exception):
    return render(request, '403.html')


def error_404(request, exception):
    return render(request, '404.html')


def error_500(request):
    return render(request, '500.html')


def e_400(request):
    return render(request, '400.html')


def e_403(request):
    return render(request, '403.html')


def e_404(request):
    return render(request, '404.html')


def e_500(request):
    return render(request, '500.html')
