from django.db import models
from django.conf import settings

from User.models import User, HouseworkTag
from calendarapp.models import CalendarEvent

class Housework(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                             related_name='user_housework', blank=True, null=True)
    tag = models.ForeignKey(HouseworkTag, on_delete=models.CASCADE, related_name='user_housework')

    houseworkId = models.AutoField(primary_key=True)
    houseworkDate = models.DateField('date published', blank=True, null=True)
    houseworkPlace = models.CharField(max_length=100, blank=True, null=True)
    houseworkDetail = models.CharField(max_length=100, blank=True, null=True)
    houseworkDone = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user}이(가) {self.houseworkPlace}에서 {self.houseworkDetail}"
