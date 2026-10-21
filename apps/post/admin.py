from django.contrib import admin
from .models import Application, Project, Membership ,RoleNeeded ,RequestJoinProjet
# Register your models here.
admin.site.register(Application)
admin.site.register(Project)
admin.site.register(RoleNeeded)
admin.site.register(Membership)
admin.site.register(RequestJoinProjet)