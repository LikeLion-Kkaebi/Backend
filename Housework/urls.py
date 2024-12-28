from django.urls import path
from .views import *

app_name = 'housework'

urlpatterns = [
    path('posting/', HouseworkPostView.as_view()),
    path('delete/<int:housework_id>/', HouseworkDeleteView.as_view()),
    path('manager/', HomeworkUserPostView.as_view()),
    path('recommend-tag/', RecommendTagByChatGPTView.as_view()),
    path('recommend-member/', RecommendMemberByChatGPTView.as_view()),
]
