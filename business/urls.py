'''URL's for business app.'''

from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    path('registration/', views.registration, name='register'),
    path('login/', views.loginUser, name='login'),
    path('otp_verification/', views.otp_verification, name="otp_verification"),
    path('logout/', views.logoutUser, name="logout"),
    path('export/transaction/', views.export_transaction, name='exporttransaction'),

    path('', views.home, name="home"),
    path('business_index/', views.business_index, name="index"),
    path('about/', views.about, name='about'),

    path('business/signup/', views.business_signup, name='business_signup'),
    path('business/home/', views.business_home, name='business_home'),
    path('business/service_add/', views.business_service_add,
         name='business_service_add'),
    path('business/transaction/', views.business_transaction,
         name="business_transaction"),
    path('business/analysis/', views.business_analysis, name="business_analysis"),
    path('business/profile/', views.business_profile, name='business_profile'),
    path('pay_individual/<str:service_name>/<str:service_owner>/<int:service_price>/<str:payment_type>/',
         views.pay_link, name='pay_link'),

    path('business/404/', views.e_404, name='404'),
    path('business/403/', views.e_403, name='403'),
    path('business/400/', views.e_400, name='400'),
    path('business/500/', views.e_500, name='500'),

    path('business/profile/<int:pk>/',
         views.BusinessProfileDetail.as_view(), name='business_profile'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
