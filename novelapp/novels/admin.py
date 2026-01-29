from django.contrib import admin

# Register your models here.
from .models import Novel, Chapter, Scene

admin.site.register(Novel)
admin.site.register(Chapter)
admin.site.register(Scene)

