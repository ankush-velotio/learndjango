from django.contrib import admin

from . import models

admin.site.register(models.Reporter)
admin.site.register(models.Article)
