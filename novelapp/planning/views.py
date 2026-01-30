from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Character, CharacterRole, Location, LocationType, Item, ItemType
from .forms import CharacterForm, LocationForm, ItemForm
from novels.models import Novel
from django.contrib import messages

@login_required
def character_list_view(request, novel_pk):
    novel = get_object_or_404(Novel, pk=novel_pk, user=request.user, archived=False)
    characters = novel.characters.filter(archived=False)
    return render(request, 'planning/character_list.html', {'novel': novel, 'characters': characters})

@login_required
def character_detail_view(request, novel_pk, pk):
    novel = get_object_or_404(Novel, pk=novel_pk, user=request.user, archived=False)
    character = get_object_or_404(Character, pk=pk, novel=novel, archived=False)
    return render(request, 'planning/character_detail.html', {'novel': novel, 'character': character})

@login_required
def location_list_view(request, novel_pk):
    novel = get_object_or_404(Novel, pk=novel_pk, user=request.user, archived=False)
    locations = novel.locations.filter(archived=False)
    return render(request, 'planning/location_list.html', {'novel': novel, 'locations': locations})

@login_required
def location_detail_view(request, novel_pk, pk):
    novel = get_object_or_404(Novel, pk=novel_pk, user=request.user, archived=False)
    location = get_object_or_404(Location, pk=pk, novel=novel, archived=False)
    return render(request, 'planning/location_detail.html', {'novel': novel, 'location': location})

@login_required
def item_list_view(request, novel_pk):
    novel = get_object_or_404(Novel, pk=novel_pk, user=request.user, archived=False)
    items = novel.items.filter(archived=False)
    return render(request, 'planning/item_list.html', {'novel': novel, 'items': items})

@login_required
def item_detail_view(request, novel_pk, pk):
    novel = get_object_or_404(Novel, pk=novel_pk, user=request.user, archived=False)
    item = get_object_or_404(Item, pk=pk, novel=novel, archived=False)
    return render(request, 'planning/item_detail.html', {'novel': novel, 'item': item})
@login_required
def character_create_view(request, novel_pk):
    novel = get_object_or_404(Novel, pk=novel_pk, user=request.user, archived=False)
    if request.method == 'POST':
        form = CharacterForm(request.POST, request.FILES, novel=novel)
        if form.is_valid():
            character = form.save(commit=False)
            character.novel = novel
            character.save()
            messages.success(request, f"Character '{character.fullname}' created.")
            return redirect('character_list', novel_pk=novel.pk)
    else:
        form = CharacterForm(novel=novel)
    return render(request, 'planning/character_form.html', {'novel': novel, 'form': form})

# Role/Type Management Views
@login_required
def character_role_list_view(request, novel_pk):
    novel = get_object_or_404(Novel, pk=novel_pk, user=request.user, archived=False)
    roles = novel.character_roles.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            CharacterRole.objects.create(novel=novel, name=name)
            messages.success(request, f"Role '{name}' added.")
            return redirect('character_role_list', novel_pk=novel.pk)
    return render(request, 'planning/category_list.html', {
        'novel': novel, 
        'categories': roles, 
        'title': 'Character Roles',
        'back_url': 'character_list'
    })

@login_required
def location_type_list_view(request, novel_pk):
    novel = get_object_or_404(Novel, pk=novel_pk, user=request.user, archived=False)
    types = novel.location_types.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            LocationType.objects.create(novel=novel, name=name)
            messages.success(request, f"Type '{name}' added.")
            return redirect('location_type_list', novel_pk=novel.pk)
    return render(request, 'planning/category_list.html', {
        'novel': novel, 
        'categories': types, 
        'title': 'Location Types',
        'back_url': 'location_list'
    })

@login_required
def item_type_list_view(request, novel_pk):
    novel = get_object_or_404(Novel, pk=novel_pk, user=request.user, archived=False)
    types = novel.item_types.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            ItemType.objects.create(novel=novel, name=name)
            messages.success(request, f"Type '{name}' added.")
            return redirect('item_type_list', novel_pk=novel.pk)
    return render(request, 'planning/category_list.html', {
        'novel': novel, 
        'categories': types, 
        'title': 'Item Types',
        'back_url': 'item_list'
    })

@login_required
def location_create_view(request, novel_pk):
    novel = get_object_or_404(Novel, pk=novel_pk, user=request.user, archived=False)
    if request.method == 'POST':
        form = LocationForm(request.POST, request.FILES, novel=novel)
        if form.is_valid():
            location = form.save(commit=False)
            location.novel = novel
            location.save()
            messages.success(request, f"Location '{location.name}' created.")
            return redirect('location_list', novel_pk=novel.pk)
    else:
        form = LocationForm(novel=novel)
    return render(request, 'planning/location_form.html', {'novel': novel, 'form': form})

@login_required
def item_create_view(request, novel_pk):
    novel = get_object_or_404(Novel, pk=novel_pk, user=request.user, archived=False)
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES, novel=novel)
        if form.is_valid():
            item = form.save(commit=False)
            item.novel = novel
            item.save()
            messages.success(request, f"Item '{item.name}' created.")
            return redirect('item_list', novel_pk=novel.pk)
    else:
        form = ItemForm(novel=novel)
    return render(request, 'planning/item_form.html', {'novel': novel, 'form': form})
