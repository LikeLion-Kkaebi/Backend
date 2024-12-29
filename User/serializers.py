from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, HouseworkTag

class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['id', 'username', 'password', 'nickname', 'plan']

    def create(self, validated_data):  
        user = User.objects.create(
            username=validated_data['username'],
            nickname=validated_data['nickname'],
            userCharacter=validated_data['userCharacter'],
            house=validated_data['house'],
            plan = validated_data['plan'],
        )
        user.set_password(validated_data['password'])
        user.save()

        token = RefreshToken.for_user(user)
        refresh = str(token)
        access = str(token.access_token)
        
        return user, access
    
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=64)
    password = serializers.CharField(max_length=128, write_only=True)

    def validate(self, data):
        username = data.get("username", None)
        password = data.get("password", None)

        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            if not user.check_password(password):
                raise serializers.ValidationError('잘못된 비밀번호입니다.')
            else:
                token = RefreshToken.for_user(user)
                refresh = str(token)
                access = str(token.access_token)

                user_info = {
                    'id': user.id,
                    'nickname': user.nickname
                }

                data = {
                    'access_token': access,
                    'user_info': user_info
                }

                return data
        else:
            raise serializers.ValidationError('존재하지 않는 사용자입니다.')

class KakaoLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=64)
    password = serializers.CharField(max_length=128, write_only=True)

    def validate(self, data):
        username = data.get("username", None)
        password = data.get("password", None)

        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            if not user.check_password(password):
                raise serializers.ValidationError('잘못된 비밀번호입니다.')
            else:
                token = RefreshToken.for_user(user)
                refresh = str(token)
                access = str(token.access_token)

                data = {
                    'id': user.id,
                    'nickname': user.nickname ,
                    'access_token': access
                }

                return data
        else:
            raise serializers.ValidationError('존재하지 않는 사용자입니다.')

class UserHouseworkSerializer(serializers.ModelSerializer):
    userid = serializers.IntegerField(source="id")
    houseworkTag = serializers.PrimaryKeyRelatedField(
        queryset=HouseworkTag.objects.all(), many=True
    )

    class Meta:
        model=User
        fields=['userid', 'nickname', 'houseworkTag']

class UserListSerializer(serializers.ModelSerializer):
    userid = serializers.IntegerField(source="id", read_only=True)
    
    class Meta:
        model=User
        fields=['userid', 'nickname', 'userCharacter']
