'''URL's for the customer app'''

from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('signupUser_individual/', views.signupUser_individual,
         name="signupUser_individual"),
    path('otp_verification_individual/', views.otp_verification_individual,
         name="otp_verification_individual"),
    path('', views.loginUser_individual, name="loginUser_individual"),
    path('individual/profile/', views.customer_profile, name="customer_profile"),

    path('home_individual/', views.home_individual, name='home_individual'),
    path('index_individual/', views.index_individual, name="index_individual"),
    path('individual/export/transaction/', views.export_transaction_individual,
         name="export_transaction_individual"),

    path('individual/transaction/', views.individual_transaction,
         name="individual_transaction"),
    path('individual/analysis/', views.individual_analysis,
         name="individual_analysis"),

    path('about_individual/', views.about_individual, name='about_individual'),

    path('logout_individual/', views.logout_individual, name="logout_individual"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
