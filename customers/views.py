'''Views for customers'''

from plotly.graph_objs import Scatter
from plotly.offline import plot
import plotly.express as px
from django.views.generic import TemplateView
from django.http import JsonResponse
import csv

from decimal import Decimal
import random
from django.utils import timezone
import datetime
from random import randint

from django.core.mail import send_mail
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages

from django.contrib.auth import authenticate, login, logout as django_logout
from django.contrib.auth.decorators import login_required

from .models import Service, BusinessProfile, Transaction, Profile
from django.contrib.auth import get_user_model

User = get_user_model()

otp = 0


def signupUser_individual(request):
    # For individual signup

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        email = request.POST['email']

        Error = 0
        message_error = []
        credit_number = randint(10000000000000000, 99999999999999999)
        debit_number = randint(1000000000000, 9999999999999)

        if len(username) < 5:
            messages.error(
                request, "Length of username  must be of atleast 5 Digit")
            return render(request, 'individual_signup.html')

        if User.objects.filter(username=username).exists():
            messages.success(request, "Account already exist")
            return render(request, 'individual_login.html')

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

        # if User.objects.filter(phone=phone).exists():
        #     Error = Error + 1
        #     message_error = message_error + ['Phone registered with different account'

        check = True
        while check:
            if User.objects.filter(credit_number=credit_number).exists():
                credit_number = randint(100000000000000000, 99999999999999999)
            else:
                break

        while check:
            if User.objects.filter(debit_number=debit_number).exists():
                debit_number = randint(1000000000000, 9999999999999)
            else:
                break

        if Error > 0:
            return render(request, 'individual_signup.html', {'messages': message_error})

        user = User.objects.create_user(username=username, password=password, email=email, first_name=first_name,
                                        last_name=last_name, wallet=1000, credit_number=credit_number, debit_number=debit_number)
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        global otp
        otp = randint(100000, 999999)
        send_mail('django_test', str(otp), 'mishrapravin214@gmail.com', [
                  email], fail_silently=False)

        login(request, user)
        return render(request, 'individual_otp.html', {'user': request.user})

    return render(request, 'register_individual.html')


def otp_verification_individual(request):
    # For otp verification of individual

    if request.method == "POST":
        userotp = request.POST['otp']
        if str(otp) == userotp:
            return render(request, "individual_index.html")
        else:
            messages.error(request, "Invalid Otp! Please try again")
            return render(request, "individual_signup.html")

    return render(request, "individual_otp.html")


def loginUser_individual(request):
    # For logging in individual

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login Successful! You are welcome!")
            return render(request, 'individual_index.html')
        else:
            messages.error(request, "Invalid credentials! Please try again!")
            return redirect('loginUser_individual')

    return render(request, 'individual_login.html')


@login_required
def home_individual(request):
    # For home of individual

    return render(request, 'individual_home.html')


@login_required
def logout_individual(request):
    # For logging out individual

    django_logout(request)
    return render(request, 'main.html')


@login_required
def index_individual(request):
    # For index of individual

    data = []
    service = Service.objects.all()
    services = Service.objects.all()
    count = 1

    for service in services:
        for profile in service.services_of_business.all():
            count = count + 1
            logged_in_user = User.objects.filter(
                username=request.user.username).first()
            data = data + \
                [[service.name, str(profile.user), service.image,
                  count, int(service.price.price)]]
    logged_in_user = User.objects.filter(
        username=request.user.username).first()

    service = Service.objects.all()
    payment_type = ['wallet', 'credit', 'debit']
    try:
        return render(request, 'individual_index.html', {'service': data, 'balance': logged_in_user.wallet, 'credit_bal': logged_in_user.credit_balance, 'debit_bal': logged_in_user.debit_balance, 'credit_num': logged_in_user.credit_number, 'debit_num': logged_in_user.debit_number, 'payment_type': payment_type})
    except:
        return render(request, '500.html')


@login_required
def individual_transaction(request):
    # For transactions of individual

    transactions = Transaction.objects.filter(
        by=request.user).order_by('-date', '-time')
    messages.success(request, 'Welcome to the transactions page!')
    return render(request, 'individual_transaction.html', locals())


@login_required
def export_transaction_individual(request):
    # For exporting transactions of individual

    response = HttpResponse(content_type='text/csv')

    writer = csv.writer(response)
    writer.writerow(['From - Username', 'First Name', 'Last Name',
                     'To', 'Amount', 'Service', 'Date', 'Time'])

    for transaction in Transaction.objects.select_related('by', 'to', 'service').filter(by=request.user).values_list('by__username', 'by__first_name', 'by__last_name', 'to__business_name', 'amount', 'service__name', 'date', 'time'):
        writer.writerow(transaction)

    response['Content-Disposition'] = 'attachment;filename="transactions.csv"'
    messages.success(
        request, "Your transactions file was downloaded successfully!")
    return response


@login_required
def individual_analysis(request):
    # For transaction analysis of individual

    # day_wise_spendings
    x1_data = []
    y1_data = []

    transactions = Transaction.objects.filter(by=request.user).order_by('date')

    for transaction in transactions:
        x1_data.append(transaction.date)
        y1_data.append(transaction.amount)

    fig = px.bar(x=x1_data, y=y1_data, labels={'x': "Day", 'y': 'Amount'})
    daywise = fig.to_html(full_html=False)
    # service_wise_spendings
    x1_data = []
    y1_data = []

    transactions_individual = Transaction.objects.select_related('by', 'to', 'service').filter(by=request.user).values_list(
        'by__username', 'to__business_name', 'amount', 'service__name', 'date', 'time').order_by('date')

    service_wise_earning = {}

    for transaction in transactions_individual:
        if transaction[3] not in service_wise_earning.keys():
            service_wise_earning[transaction[3]] = transaction[2]
        else:
            service_wise_earning[transaction[3]] += transaction[2]

    x1_data = list(service_wise_earning.keys())
    y1_data = list(service_wise_earning.values())

    fig = px.bar(x=x1_data, y=y1_data, labels={'x': "Service", 'y': 'Amount'})
    service_spending = fig.to_html(full_html=False)
    # month_wise_earning
    month_wise_earning = {}

    for transaction in transactions_individual:
        month_name = datetime.date(
            2020, transaction[4].month, 1).strftime('%B')
        if month_name not in month_wise_earning.keys():
            month_wise_earning[month_name] = transaction[2]
        else:
            month_wise_earning[month_name] += transaction[2]

    x1_data = list(month_wise_earning.keys())
    y1_data = list(month_wise_earning.values())

    fig = px.bar(x=x1_data, y=y1_data, labels={'x': "Month", 'y': 'Amount'})
    month_spending = fig.to_html(full_html=False)

    # payments_day_wise
    x1_data = []
    y1_data = []

    transactions_per_month = Transaction.objects.filter(
        by=request.user).values_list("date").order_by("-date")
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

    # consumption_service_wise
    x1_data = []
    y1_data = []

    no_of_service_used = Transaction.objects.filter(
        by=request.user).values_list("service_id")

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

    messages.success(request, "Welcome to the analysis page!")
    logged_in_user = User.objects.filter(
        username=request.user.username).first()
    return render(request, 'individual_analysis.html', {'daywise': daywise,
                                                        'service_per_month': service_per_month,
                                                        'service_spending': service_spending,
                                                        'month_spending': month_spending,
                                                        'number_times_service': number_times_service,
                                                        'balance': logged_in_user.wallet, 'credit_bal': logged_in_user.credit_balance, 'debit_bal': logged_in_user.debit_balance, 'credit_num': logged_in_user.credit_number, 'debit_num': logged_in_user.debit_number})


@login_required
def customer_profile(request):
    # For rendering customer profile

    logged_in_user = User.objects.filter(
        username=request.user.username).first()
    return render(request, 'individual_profile.html', {'logged_in_user': logged_in_user})


@login_required
def about_individual(request):
    # About individual

    return render(request, 'about_individual.html')


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
