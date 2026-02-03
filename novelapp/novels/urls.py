from django.urls import path
from . import views

urlpatterns = [
    path('', views.novel_list_view, name='novel_list'),
    path('archived/', views.archived_novel_list_view, name='archived_novel_list'),
    path('create/', views.novel_create_view, name='novel_create'),
    path('<int:pk>/', views.novel_detail_view, name='novel_detail'),
    path('<int:pk>/edit/', views.novel_update_view, name='novel_edit'),
    path('<int:pk>/delete/', views.novel_delete_view, name='novel_delete'),
    path('<int:pk>/archive/', views.novel_archive_view, name='novel_archive'),
    path('<int:pk>/unarchive/', views.novel_unarchive_view, name='novel_unarchive'),
    path('<int:novel_pk>/chapter/create/', views.chapter_create_view, name='chapter_create'),
    path('<int:novel_pk>/chapter/<int:chapter_pk>/', views.chapter_detail_view, name='chapter_detail'),
    path('<int:novel_pk>/chapter/<int:chapter_pk>/scene/create/', views.scene_create_view, name='scene_create'),
    path('<int:novel_pk>/chapter/<int:chapter_pk>/scene/<int:scene_pk>/editor/', views.scene_editor_view, name='scene_editor'),
]
