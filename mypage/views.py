from django.shortcuts import render
from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from User.models import User, House
from .serializers import UserInfoSerializer, HouseInfoSerializer, HouseMemberSerializer, RemoveMemberSerializer
# Create your views here.

class UserInfoView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserInfoSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class HouseInfoView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            house = user.house
            serializer = HouseInfoSerializer(house)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except AttributeError:
            return Response({"error": "사용자가 속한 집이 없습니다."}, status=status.HTTP_404_NOT_FOUND)
    
class HouseMemberInfoView(views.APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            user = request.user
            house = user.house

            members = house.users_house.all()

            serializer = HouseMemberSerializer(members, many=True)
            return Response({"housemembers" : serializer.data}, status=status.HTTP_200_OK)
        
        except AttributeError:
            return Response({"error": "사용자가 속한 집의 식구 정보가 없습니다."}, status=status.HTTP_404_NOT_FOUND)

class RemoveMemberView(views.APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        serializer = RemoveMemberSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data.get('user_id')

            try:
                user_to_remove = User.objects.get(id=user_id)
                house = request.user.house

                if user_to_remove.house == house:
                    user_to_remove.house = None
                    user_to_remove.save()
                    return Response({"message": "우리집에서 선택한 식구가 삭제되었습니다."}, status=status.HTTP_200_OK)
            
                return Response({"error": "해당 식구가 우리집에 속해 있지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)
            
            except User.DoesNotExist:
                return Response({"error": "찾을 수 없는 사용자입니다."}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)