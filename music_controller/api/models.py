from django.db import models
import random
import string

def generate_unique_code():
    """Return an unique string of upercase ascii characters"""
    length = 8
    while True:
        code = ''.join(random.choices(string.ascii_uppercase, k=length))
        if Room.objects.filter(code=code).count() == 0:
            break
    return code

# Create your models here.
class Room(models.Model):
    """Model a room with a table"""
    code = models.CharField(max_length=8, default='', unique=True)
    host = models.CharField(max_length=50, default='', unique=True)
    guest_can_paues = models.BooleanField(null=False, default=False)
    votes_to_skip = models.IntegerField(null=False, default=1)
    created_at = models.DateTimeField(auto_now_add=True)