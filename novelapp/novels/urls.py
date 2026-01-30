from django.urls import path
from . import views

urlpatterns = [
    path('', views.novel_list_view, name='novel_list'),
    path('create/', views.novel_create_view, name='novel_create'),
    path('<int:pk>/', views.novel_detail_view, name='novel_detail'),
    path('<int:novel_pk>/chapter/create/', views.chapter_create_view, name='chapter_create'),
    path('<int:novel_pk>/chapter/<int:chapter_pk>/', views.chapter_detail_view, name='chapter_detail'),
    path('<int:novel_pk>/chapter/<int:chapter_pk>/scene/create/', views.scene_create_view, name='scene_create'),
    path('<int:novel_pk>/chapter/<int:chapter_pk>/scene/<int:scene_pk>/', views.scene_view, name='scene_editor'),
]
