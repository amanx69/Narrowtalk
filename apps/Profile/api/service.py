from django.core.cache import cache
from ..models import ProfileLIke ,Profile
from django.db.models import F
from rest_framework import status
from django.db import transaction
from rest_framework.response import Response


def Profile_like(user,profile):
    
    with transaction.atomic():
        profile_obj=ProfileLIke.objects.filter(user=user,profile=profile).first()
        if profile_obj:
            profile_obj.delete()
            Profile.objects.filter(id=profile.id).update(
                profile_like=F('profile_like')-1
            )
            cache.delete(f'user_profile_v2:{profile.user.id}')
            cache.delete(f'user_profile_v2:{profile.user.id}')
            return Response({
                    "message":f"unlike{profile.id}"
                },status.HTTP_200_OK)
        
        create_Like=ProfileLIke.objects.create(
            user=user,
            profile=profile
        )
        Profile.objects.filter(id=profile.id).update(
                        profile_like=F('profile_like')+1
                    )
        cache.delete(f'user_profile_v2:{profile.user.id}')
        return Response({
            "message":f"like on{profile.id}"
        })
                
        
        
    
    
    
    