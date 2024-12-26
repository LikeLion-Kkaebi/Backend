from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from datetime import timedelta
from django.utils.timezone import now
from .models import Notification

class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        notifications = Notification.objects.filter(receiver=user).order_by('-created_at')

        def format_time(notification):
            time_delta = now() - notification.created_at
            if time_delta.total_seconds() < 86400:  # 24시간 이내
                if time_delta.seconds < 3600:  # 1시간 미만
                    return f"{time_delta.seconds // 60}분 전"
                return f"{time_delta.seconds // 3600}시간 전"
            else:  # 24시간 이상
                return notification.created_at.strftime('%Y-%m-%d')

        notification_data = [
            {
                "alert_id": notification.id,
                "message": notification.message,
                "time": format_time(notification),  # 시간 포맷 처리
                "absolute_time": notification.created_at.isoformat(),
                "is_new": (now() - notification.created_at).total_seconds() < 86400  # 24시간 기준 새 알림 여부
            }
            for notification in notifications
        ]

        return Response({"notifications": notification_data}, status=200)
