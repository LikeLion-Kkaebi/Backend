from django.shortcuts import render, get_object_or_404
from rest_framework import views, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.decorators import login_required

from .models import Housework
from User.models import *
from calendarapp.models import CalendarEvent
from .serializers import HouseworkSerializer
from User.serializers import UserListSerializer

import os
from datetime import datetime
from openai import OpenAI
from django.http import JsonResponse

class HouseworkPostView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer=HouseworkSerializer(data=request.data)

        if serializer.is_valid():
            tag_id = request.data.get('tag')
            housework_tag = get_object_or_404(HouseworkTag, id=tag_id)
            serializer.save(tag=housework_tag)
            return Response({'message':'Housework post 성공', 'data':serializer.data}, status=status.HTTP_201_CREATED)
        return Response({'message':'Housework post 실패', 'error':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class HouseworkDeleteView(views.APIView):
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, housework_id, format=None):
        housework = get_object_or_404(Housework, houseworkId=housework_id)
        housework.delete()

        return Response({'message': 'Housework delete 성공'}, status=status.HTTP_200_OK)

class HomeworkUserPostView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user=request.user
        house=House.objects.get(id=user.house.id)

        housemember=User.objects.filter(house=house)
        serializer = UserListSerializer(housemember, many=True)

        return Response({
            'message': 'UserList get 성공',
            'data': {
                'housename': house.housename,
                'housemember': serializer.data
            }
        })

    def put(self, request, format=None):
        housework_id = request.data.get('houseworkId')
        manager = request.data.get('housework_manager')

        try:
            housework = Housework.objects.get(houseworkId=housework_id)
            user = User.objects.get(id=manager)

            housework.user = user
            housework.save()

            serializer = HouseworkSerializer(housework)

            return Response({
                'message': 'Housework manager put 성공',
                'data': serializer.data
            }, status=200)

        except Housework.DoesNotExist:
            return Response({'message': '해당 housework를 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({'message': '해당 user를 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': 'Housework manager put 실패', 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# OpenAI
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

class RecommendTagByChatGPTView(views.APIView):
    permission_classes = [IsAuthenticated]

        
    def get(self, request):
        if request.user.plan != "premium":
            return JsonResponse({"error": "AI 추천 기능은 프리미엄 요금제를 결제해야 사용할 수 있습니다."}, status=403)

        date_str = request.GET.get('date', '').strip()

        if not date_str:
            return JsonResponse({"error": "No message provided"}, status=400)
        
        try:
            housework_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return JsonResponse({"error": "YYYY-MM-DD 형식을 사용해야 합니다."}, status=400)
        
        day_of_week = housework_date.weekday() + 1
        if day_of_week == 7:
            day_of_week = 0

        housework_entries = Housework.objects.filter(houseworkDate__week_day=day_of_week+1)
        tags = [entry.tag.tag for entry in housework_entries if entry.tag]

        if not tags:
            return JsonResponse({"error": "지정된 집안일 태그가 없습니다."}, status=400)

        prompt = f"The following are the housework tags performed on {housework_date.strftime('%A')}:\n"
        prompt += "\n".join(tags)
        prompt += "\nBased on the above list of tags, what is the most frequent tag? Please give only the tag and no extra explanation."

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0
            )
            
        
            chatgpt_response = response.choices[0].message.content
            return JsonResponse({"response": chatgpt_response})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

class RecommendMemberByChatGPTView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.plan != "premium":
            return JsonResponse({"error": "AI 추천 기능은 프리미엄 요금제를 결제해야 사용할 수 있습니다."}, status=403)
        
        user = request.user

        housework_id = request.GET.get('houseworkId')

        if not housework_id:
            return JsonResponse({"error": "houseworkId가 필요합니다."}, status=400)

        housework = get_object_or_404(Housework, houseworkId=housework_id)
        
        housework_tag = housework.tag
        if not housework_tag:
            return JsonResponse({"error": "집안일에 태그가 지정되지 않았습니다."}, status=400)

        house = user.house
        if not house:
            return JsonResponse({"error": "사용자의 집 정보가 없습니다."}, status=400)
        
        house_members = User.objects.filter(house=house).exclude(id=user.id)

        users_list = []
        for member in house_members:
            member_tags = member.houseworkTag.all()
            users_list.append({
                "userid": member.id,
                "tags": [tag.tag for tag in member_tags]
            })

        prompt = f"Below are the users whose tags match the housework tag.\n" \
         f"Housework Tag: {housework_tag.tag}\n" \
         f"Users to recommend:\n{users_list}\n" \
         f"Please recommend the most suitable person to take care of this housework from the list above. Only return the ID of the recommended person."

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0
            )
            
        
            chatgpt_response = response.choices[0].message.content
            return JsonResponse({"response": chatgpt_response})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
