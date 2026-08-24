from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve
from django.http import HttpResponse
from core.views import dashboard_view


def health_check(request):
    return HttpResponse('ok')


urlpatterns = [
    path('health/', health_check, name='health_check'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('novels/', include('novels.urls')),
    path('planning/', include('planning.urls')),
    path('', dashboard_view, name='dashboard'),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

