from django.contrib import admin
from .models import Profile ,Skill,ProfileLIke
# Register your models here.

admin.site.register(Profile)
admin.site.register(Skill)
admin.site.register(ProfileLIke)

