from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from Housework.models import Housework
from User.models import User
from notification.models import Notification

@receiver(post_save, sender=Housework)
def check_today_tasks_done(sender, instance, **kwargs):
    today = now().date()
    user = instance.user
    today_tasks = Housework.objects.filter(user=user, houseworkDate=today)

    if today_tasks.filter(houseworkDone=False).exists():
        return

    if user is None:
        return 
    if not user.house:
        return
    
    house = user.house
    if house:
        family_members = User.objects.filter(house=house).exclude(id=user.id)
        for member in family_members:
            notification = Notification.objects.create(
                sender=user,
                receiver=member,
                message=f"{user.nickname}님이 오늘의 할 일을 모두 완료했어요."
            )

            # WebSocket으로 알림 전송
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"user_{member.id}",
                {
                    "type": "send_notification",
                    "message": notification.message,
                }
            )

@receiver(post_save, sender=Notification)
def send_notification(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{instance.receiver.id}",
        {
            "type": "send_notification",
            "message": instance.message,
        }
    )
