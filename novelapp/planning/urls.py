from django.urls import path
from . import views

urlpatterns = [
    # Characters
    path('novel/<int:novel_pk>/characters/', views.character_list_view, name='character_list'),
    path('novel/<int:novel_pk>/characters/create/', views.character_create_view, name='character_create'),
    path('novel/<int:novel_pk>/characters/<int:pk>/', views.character_detail_view, name='character_detail'),
    path('novel/<int:novel_pk>/characters/<int:pk>/edit/', views.character_edit_view, name='character_edit'),
    path('novel/<int:novel_pk>/characters/roles/', views.character_role_list_view, name='character_role_list'),
    
    # Locations
    path('novel/<int:novel_pk>/locations/', views.location_list_view, name='location_list'),
    path('novel/<int:novel_pk>/locations/create/', views.location_create_view, name='location_create'),
    path('novel/<int:novel_pk>/locations/<int:pk>/', views.location_detail_view, name='location_detail'),
    path('novel/<int:novel_pk>/locations/<int:pk>/edit/', views.location_edit_view, name='location_edit'),
    path('novel/<int:novel_pk>/locations/types/', views.location_type_list_view, name='location_type_list'),
    
    # Items
    path('novel/<int:novel_pk>/items/', views.item_list_view, name='item_list'),
    path('novel/<int:novel_pk>/items/create/', views.item_create_view, name='item_create'),
    path('novel/<int:novel_pk>/items/<int:pk>/', views.item_detail_view, name='item_detail'),
    path('novel/<int:novel_pk>/items/<int:pk>/edit/', views.item_edit_view, name='item_edit'),
    path('novel/<int:novel_pk>/items/types/', views.item_type_list_view, name='item_type_list'),
]
