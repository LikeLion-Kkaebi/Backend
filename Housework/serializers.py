from rest_framework import serializers

from User.models import User, HouseworkTag
from .models import Housework
from User.serializers import UserHouseworkSerializer, UserListSerializer

class HouseworkTagSerializer(serializers.Serializer):
    tagid = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = HouseworkTag
        fields = ['tagid', 'tag']

class HouseworkSerializer(serializers.ModelSerializer):
    user=UserHouseworkSerializer(read_only=True)
    tag=HouseworkTagSerializer(read_only=True) 

    class Meta:
        model = Housework
        fields = ['houseworkId', 'user', 'tag', 'houseworkDate', 
                  'houseworkPlace', 'houseworkDetail', 'houseworkDone']

class CalendarHouseworkSerializer(serializers.ModelSerializer):
    user=UserListSerializer(read_only=True)
    tag=HouseworkTagSerializer(read_only=True)

    class Meta:
        model = Housework
        fields = ['houseworkId', 'user', 'tag', 'houseworkDate', 
                  'houseworkPlace', 'houseworkDetail', 'houseworkDone']
