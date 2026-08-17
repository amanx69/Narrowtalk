from django.db import models
import uuid
from django.contrib.auth import get_user_model
from .service import *


User=get_user_model()


class Room(models.Model):
    id=models.UUIDField(primary_key=True,editable=False,unique=True,default=uuid.uuid4)
    owner=models.ForeignKey(User,on_delete=models.CASCADE,related_name="room_owner")
    room_name=models.CharField(max_length=15)
    room_profile=models.ImageField(upload_to="rooms_profile/",null=True,blank=True)
    uniqe_id=models.CharField(unique=True,max_length=10,null=False,blank=False,default=gernate_uniqe_number)
    created_at=models.DateTimeField(auto_now_add=True)
    #TODO add decpriction in future
    participants = models.ManyToManyField(
        User, through='RoomParticipant', related_name='joined_rooms'
    )
    
    def __str__(self):
        return f"{self.room_name} owner is {self.owner.email}"
    

class RoomParticipant(models.Model):
    
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    is_mute=models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('room', 'user')
        
    
    def __str__(self):
        return f"{self.user.email} to join {self.room.room_name}"
    
    
    
    
class RoomInviteLink(models.Model):
    room=models.ForeignKey(Room,on_delete=models.CASCADE,related_name="room_link")
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name="room_link_creater")
    token=models.UUIDField(default=uuid.uuid4,editable=False,unique=True)
    created_at=models.DateTimeField(auto_now_add=True)
    is_active=models.BooleanField(default=True)
    use_count=models.PositiveIntegerField(default=0)
    
    
    
    def is_valid(self):
        return self.is_active
         