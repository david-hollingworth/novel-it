from django.urls import path
from . import views

urlpatterns = [
    # Modal endpoints
    path('novel/<int:novel_pk>/modal/characters/', views.modal_character_list, name='modal_character_list'),
    path('novel/<int:novel_pk>/modal/characters/create/', views.modal_character_create, name='modal_character_create'),
    path('novel/<int:novel_pk>/modal/characters/<int:pk>/', views.modal_character_detail, name='modal_character_detail'),
    path('novel/<int:novel_pk>/modal/characters/<int:pk>/edit/', views.modal_character_edit, name='modal_character_edit'),
    path('novel/<int:novel_pk>/modal/locations/', views.modal_location_list, name='modal_location_list'),
    path('novel/<int:novel_pk>/modal/locations/create/', views.modal_location_create, name='modal_location_create'),
    path('novel/<int:novel_pk>/modal/locations/<int:pk>/', views.modal_location_detail, name='modal_location_detail'),
    path('novel/<int:novel_pk>/modal/locations/<int:pk>/edit/', views.modal_location_edit, name='modal_location_edit'),
    path('novel/<int:novel_pk>/modal/items/', views.modal_item_list, name='modal_item_list'),
    path('novel/<int:novel_pk>/modal/items/create/', views.modal_item_create, name='modal_item_create'),
    path('novel/<int:novel_pk>/modal/items/<int:pk>/', views.modal_item_detail, name='modal_item_detail'),
    path('novel/<int:novel_pk>/modal/items/<int:pk>/edit/', views.modal_item_edit, name='modal_item_edit'),

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
