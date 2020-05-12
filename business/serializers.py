'''For serializing all data'''

from .models import BusinessProfile, Profile
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer

class ProfileSerializer(serializers.ModelSerializer):
    #Serializing all users profile

    class Meta:
        model = Profile
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'date_joined',
            'phone',
            'wallet'
            'profile_type'
        ]

class BusinessProfileSerializer(serializers.ModelSerializer):
    #Serializing Business profile

    class Meta:
        model = BusinessProfile
        fields = [
            'user',
            'business_name',
            'register_date',
            'pan_number',
            'pan_name',
            'address',
            'pincode',
            'city',
            'state',
            'service',
        ]
