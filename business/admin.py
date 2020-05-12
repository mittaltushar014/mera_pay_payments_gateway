from django.contrib import admin
from django.contrib.auth.models import User
from .models import Profile, Service, BusinessProfile, Transaction

admin.site.register(Profile)
admin.site.register(Service)
admin.site.register(BusinessProfile)
admin.site.register(Transaction)

