from datetime import timedelta
from django.utils.timezone import now
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Notification

class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        three_days_ago = now() - timedelta(days=3)
        notifications = Notification.objects.filter(receiver=user, created_at__gte=three_days_ago).order_by('-created_at')

        def format_time(notification):
            time_delta = now() - notification.created_at
            if time_delta.total_seconds() < 86400:  # 24시간 이내
                if time_delta.seconds < 3600:
                    return f"{time_delta.seconds // 60}분 전"
                return f"{time_delta.seconds // 3600}시간 전"
            else:
                return notification.created_at.strftime('%Y-%m-%d')

        notification_data = [
            {
                "alert_id": notification.id,
                "message": notification.message,
                "time": format_time(notification),
                "absolute_time": notification.created_at.isoformat(),
                "is_new": (now() - notification.created_at).total_seconds() < 86400,
            }
            for notification in notifications
        ]

        return Response({"notifications": notification_data}, status=200)

