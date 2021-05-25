from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Person, MapSession, UserVideoLink, Label

admin.site.register(User, UserAdmin)
admin.site.register(Person)
admin.site.register(MapSession)
admin.site.register(UserVideoLink)
admin.site.register(Label)