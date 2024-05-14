from django.contrib import admin
from apps.users import models

# Register your models here.
admin.site.register(models.User)
admin.site.register(models.Actor)
admin.site.register(models.Director)
admin.site.register(models.Film)
admin.site.register(models.Review)
