from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from .models import Character, CharacterRole, Location, LocationType, Item, ItemType, Relationship, RelationshipType
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
@login_required
def character_edit_view(request, novel_pk, pk):
    novel = get_object_or_404(Novel, pk=novel_pk, user=request.user, archived=False)
    character = get_object_or_404(Character, pk=pk, novel=novel, archived=False)
    
    if request.method == 'POST':
        form = CharacterForm(request.POST, request.FILES, instance=character, novel=novel)
        if form.is_valid():
            form.save()
            messages.success(request, f"Character '{character.fullname}' updated.")
            return redirect('character_detail', novel_pk=novel.pk, pk=character.pk)
    else:
        form = CharacterForm(instance=character, novel=novel)
    
    return render(request, 'planning/character_form.html', {
        'novel': novel, 
        'form': form,
        'character': character,
        'is_edit': True
    })

# Role/Type Management Views
# ─── Modal Views ────────────────────────────────────────────────────────────

@login_required
def modal_character_list(request, novel_pk):
    novel = get_object_or_404(Novel, pk=novel_pk, user=request.user, archived=False)
    characters = novel.characters.filter(archived=False)
    return render(request, 'planning/modal_character_list.html', {'novel': novel, 'characters': characters})

@login_required
def modal_character_detail(request, novel_pk, pk):
    novel = get_object_or_404(Novel, pk=novel_pk, user=request.user, archived=False)
    character = get_object_or_404(Character, pk=pk, novel=novel, archived=False)
    return render(request, 'planning/modal_character_detail.html', {
        'novel': novel,
        'character': character,
        'relationships': _get_relationships_for_entity(character),
        'scene_occurrences': _get_scene_occurrences(character),
    })

@login_required
def modal_character_create(request, novel_pk):
    novel = get_object_or_404(Novel, pk=novel_pk, user=request.user, archived=False)
    if request.method == 'POST':
        form = CharacterForm(request.POST, request.FILES, novel=novel)
        if form.is_valid():
            character = form.save(commit=False)
            character.novel = novel
            character.save()
            characters = novel.characters.filter(archived=False)
            return render(request, 'planning/modal_character_list.html', {'novel': novel, 'characters': characters})
    else:
        form = CharacterForm(novel=novel)
    return render(request, 'planning/modal_character_form.html', {'novel': novel, 'form': form})

@login_required
def modal_character_edit(request, novel_pk, pk):
    novel = get_object_or_404(Novel, pk=novel_pk, user=request.user, archived=False)
    character = get_object_or_404(Character, pk=pk, novel=novel, archived=False)
    if request.method == 'POST':
        form = CharacterForm(request.POST, request.FILES, instance=character, novel=novel)
        if form.is_valid():
            form.save()
            characters = novel.characters.filter(archived=False)
            return render(request, 'planning/modal_character_list.html', {'novel': novel, 'characters': characters})
    else:
        form = CharacterForm(instance=character, novel=novel)
    return render(request, 'planning/modal_character_form.html', {
        'novel': novel, 'form': form, 'character': character,
        'entity': character, 'entity_type': 'character',
        'relationships': _get_relationships_for_entity(character),
        'relationship_types': novel.relationship_types.all(),
        'all_characters': novel.characters.filter(archived=False),
        'all_locations': novel.locations.filter(archived=False),
        'all_items': novel.items.filter(archived=False),
        'scene_occurrences': _get_scene_occurrences(character) if character else [],
    })

@login_required
def modal_location_list(request, novel_pk):
    novel = get_object_or_404(Novel, pk=novel_pk, user=request.user, archived=False)
    locations = novel.locations.filter(archived=False)
    return render(request, 'planning/modal_location_list.html', {'novel': novel, 'locations': locations})

@login_required
def modal_location_detail(request, novel_pk, pk):
    novel = get_object_or_404(Novel, pk=novel_pk, user=request.user, archived=False)
    location = get_object_or_404(Location, pk=pk, novel=novel, archived=False)
    return render(request, 'planning/modal_location_detail.html', {
        'novel': novel,
        'location': location,
        'relationships': _get_relationships_for_entity(location),
        'scene_occurrences': _get_scene_occurrences(location),
    })

@login_required
def modal_location_create(request, novel_pk):
    novel = get_object_or_404(Novel, pk=novel_pk, user=request.user, archived=False)
    if request.method == 'POST':
        form = LocationForm(request.POST, request.FILES, novel=novel)
        if form.is_valid():
            location = form.save(commit=False)
            location.novel = novel
            location.save()
            locations = novel.locations.filter(archived=False)
            return render(request, 'planning/modal_location_list.html', {'novel': novel, 'locations': locations})
    else:
        form = LocationForm(novel=novel)
    return render(request, 'planning/modal_location_form.html', {'novel': novel, 'form': form})

@login_required
def modal_location_edit(request, novel_pk, pk):
    novel = get_object_or_404(Novel, pk=novel_pk, user=request.user, archived=False)
    location = get_object_or_404(Location, pk=pk, novel=novel, archived=False)
    if request.method == 'POST':
        form = LocationForm(request.POST, request.FILES, instance=location, novel=novel)
        if form.is_valid():
            form.save()
            locations = novel.locations.filter(archived=False)
            return render(request, 'planning/modal_location_list.html', {'novel': novel, 'locations': locations})
    else:
        form = LocationForm(instance=location, novel=novel)
    return render(request, 'planning/modal_location_form.html', {
        'novel': novel, 'form': form, 'location': location,
        'entity': location, 'entity_type': 'location',
        'relationships': _get_relationships_for_entity(location),
        'relationship_types': novel.relationship_types.all(),
        'all_characters': novel.characters.filter(archived=False),
        'all_locations': novel.locations.filter(archived=False),
        'all_items': novel.items.filter(archived=False),
        'scene_occurrences': _get_scene_occurrences(location) if location else [],
    })

@login_required
def modal_item_list(request, novel_pk):
    novel = get_object_or_404(Novel, pk=novel_pk, user=request.user, archived=False)
    items = novel.items.filter(archived=False)
    return render(request, 'planning/modal_item_list.html', {'novel': novel, 'items': items})

@login_required
def modal_item_detail(request, novel_pk, pk):
    novel = get_object_or_404(Novel, pk=novel_pk, user=request.user, archived=False)
    item = get_object_or_404(Item, pk=pk, novel=novel, archived=False)
    return render(request, 'planning/modal_item_detail.html', {
        'novel': novel,
        'item': item,
        'relationships': _get_relationships_for_entity(item),
        'scene_occurrences': _get_scene_occurrences(item),
    })

@login_required
def modal_item_create(request, novel_pk):
    novel = get_object_or_404(Novel, pk=novel_pk, user=request.user, archived=False)
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES, novel=novel)
        if form.is_valid():
            item = form.save(commit=False)
            item.novel = novel
            item.save()
            items = novel.items.filter(archived=False)
            return render(request, 'planning/modal_item_list.html', {'novel': novel, 'items': items})
    else:
        form = ItemForm(novel=novel)
    return render(request, 'planning/modal_item_form.html', {'novel': novel, 'form': form})

@login_required
def modal_item_edit(request, novel_pk, pk):
    novel = get_object_or_404(Novel, pk=novel_pk, user=request.user, archived=False)
    item = get_object_or_404(Item, pk=pk, novel=novel, archived=False)
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES, instance=item, novel=novel)
        if form.is_valid():
            form.save()
            items = novel.items.filter(archived=False)
            return render(request, 'planning/modal_item_list.html', {'novel': novel, 'items': items})
    else:
        form = ItemForm(instance=item, novel=novel)
    return render(request, 'planning/modal_item_form.html', {
        'novel': novel, 'form': form, 'item': item,
        'entity': item, 'entity_type': 'item',
        'relationships': _get_relationships_for_entity(item),
        'relationship_types': novel.relationship_types.all(),
        'all_characters': novel.characters.filter(archived=False),
        'all_locations': novel.locations.filter(archived=False),
        'all_items': novel.items.filter(archived=False),
        'scene_occurrences': _get_scene_occurrences(item) if item else [],
    })

# ─── End Modal Views ─────────────────────────────────────────────────────────

@login_required
def modal_manage_location_types(request, novel_pk):
    """HTMX fragment for managing location types inline within the location edit modal."""
    from django.urls import reverse
    novel = get_object_or_404(Novel, pk=novel_pk, user=request.user, archived=False)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            name = request.POST.get('name', '').strip()
            if name:
                LocationType.objects.get_or_create(novel=novel, name=name)
        elif action == 'rename':
            cat_id = request.POST.get('category_id')
            name = request.POST.get('name', '').strip()
            if cat_id and name:
                lt = get_object_or_404(LocationType, pk=cat_id, novel=novel)
                lt.name = name
                lt.save()
        elif action == 'delete':
            cat_id = request.POST.get('category_id')
            if cat_id:
                lt = get_object_or_404(LocationType, pk=cat_id, novel=novel)
                lt.delete()
    types = novel.location_types.all()
    return render(request, 'planning/modal_manage_types.html', {
        'novel': novel,
        'types': types,
        'manage_url': reverse('modal_manage_location_types', args=[novel_pk]),
        'field_id': 'id_type',
    })


@login_required
def modal_manage_item_types(request, novel_pk):
    """HTMX fragment for managing item types inline within the item edit modal."""
    from django.urls import reverse
    novel = get_object_or_404(Novel, pk=novel_pk, user=request.user, archived=False)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            name = request.POST.get('name', '').strip()
            if name:
                ItemType.objects.get_or_create(novel=novel, name=name)
        elif action == 'rename':
            cat_id = request.POST.get('category_id')
            name = request.POST.get('name', '').strip()
            if cat_id and name:
                it = get_object_or_404(ItemType, pk=cat_id, novel=novel)
                it.name = name
                it.save()
        elif action == 'delete':
            cat_id = request.POST.get('category_id')
            if cat_id:
                it = get_object_or_404(ItemType, pk=cat_id, novel=novel)
                it.delete()
    types = novel.item_types.all()
    return render(request, 'planning/modal_manage_types.html', {
        'novel': novel,
        'types': types,
        'manage_url': reverse('modal_manage_item_types', args=[novel_pk]),
        'field_id': 'id_type',
    })


@login_required
def modal_manage_character_roles(request, novel_pk):
    """HTMX fragment for managing character roles inline within the character edit modal."""
    from django.urls import reverse
    novel = get_object_or_404(Novel, pk=novel_pk, user=request.user, archived=False)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            name = request.POST.get('name', '').strip()
            if name:
                CharacterRole.objects.get_or_create(novel=novel, name=name)
        elif action == 'rename':
            cat_id = request.POST.get('category_id')
            name = request.POST.get('name', '').strip()
            if cat_id and name:
                role = get_object_or_404(CharacterRole, pk=cat_id, novel=novel)
                role.name = name
                role.save()
        elif action == 'delete':
            cat_id = request.POST.get('category_id')
            if cat_id:
                role = get_object_or_404(CharacterRole, pk=cat_id, novel=novel)
                role.delete()
    roles = novel.character_roles.all()
    return render(request, 'planning/modal_manage_types.html', {
        'novel': novel,
        'types': roles,
        'manage_url': reverse('modal_manage_character_roles', args=[novel_pk]),
        'field_id': 'id_role',
    })


@login_required
def modal_type_options(request, novel_pk, type_model):
    """Returns a fresh <select> options fragment after type changes, for refreshing the form select."""
    novel = get_object_or_404(Novel, pk=novel_pk, user=request.user, archived=False)
    if type_model == 'location':
        options = novel.location_types.all()
    elif type_model == 'item':
        options = novel.item_types.all()
    elif type_model == 'character':
        options = novel.character_roles.all()
    else:
        options = []
    return render(request, 'planning/modal_type_options.html', {'options': options})


@login_required
def character_role_list_view(request, novel_pk):
    novel = get_object_or_404(Novel, pk=novel_pk, user=request.user, archived=False)
    roles = novel.character_roles.all()
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            name = request.POST.get('name', '').strip()
            if name:
                CharacterRole.objects.get_or_create(novel=novel, name=name)
                messages.success(request, f"Role '{name}' added.")
        elif action == 'rename':
            cat_id = request.POST.get('category_id')
            name = request.POST.get('name', '').strip()
            if cat_id and name:
                role = get_object_or_404(CharacterRole, pk=cat_id, novel=novel)
                role.name = name
                role.save()
                messages.success(request, f"Role renamed to '{name}'.")
        elif action == 'delete':
            cat_id = request.POST.get('category_id')
            if cat_id:
                role = get_object_or_404(CharacterRole, pk=cat_id, novel=novel)
                role.delete()
                messages.success(request, "Role deleted.")
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
        action = request.POST.get('action')
        if action == 'add':
            name = request.POST.get('name', '').strip()
            if name:
                LocationType.objects.get_or_create(novel=novel, name=name)
                messages.success(request, f"Type '{name}' added.")
        elif action == 'rename':
            cat_id = request.POST.get('category_id')
            name = request.POST.get('name', '').strip()
            if cat_id and name:
                lt = get_object_or_404(LocationType, pk=cat_id, novel=novel)
                lt.name = name
                lt.save()
                messages.success(request, f"Type renamed to '{name}'.")
        elif action == 'delete':
            cat_id = request.POST.get('category_id')
            if cat_id:
                lt = get_object_or_404(LocationType, pk=cat_id, novel=novel)
                lt.delete()
                messages.success(request, "Type deleted.")
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
        action = request.POST.get('action')
        if action == 'add':
            name = request.POST.get('name', '').strip()
            if name:
                ItemType.objects.get_or_create(novel=novel, name=name)
                messages.success(request, f"Type '{name}' added.")
        elif action == 'rename':
            cat_id = request.POST.get('category_id')
            name = request.POST.get('name', '').strip()
            if cat_id and name:
                it = get_object_or_404(ItemType, pk=cat_id, novel=novel)
                it.name = name
                it.save()
                messages.success(request, f"Type renamed to '{name}'.")
        elif action == 'delete':
            cat_id = request.POST.get('category_id')
            if cat_id:
                it = get_object_or_404(ItemType, pk=cat_id, novel=novel)
                it.delete()
                messages.success(request, "Type deleted.")
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
def location_edit_view(request, novel_pk, pk):
    novel = get_object_or_404(Novel, pk=novel_pk, user=request.user, archived=False)
    location = get_object_or_404(Location, pk=pk, novel=novel, archived=False)
    
    if request.method == 'POST':
        form = LocationForm(request.POST, request.FILES, instance=location, novel=novel)
        if form.is_valid():
            form.save()
            messages.success(request, f"Location '{location.name}' updated.")
            return redirect('location_detail', novel_pk=novel.pk, pk=location.pk)
    else:
        form = LocationForm(instance=location, novel=novel)
    
    return render(request, 'planning/location_form.html', {
        'novel': novel, 
        'form': form,
        'location': location,
        'is_edit': True
    })

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
@login_required
def item_edit_view(request, novel_pk, pk):
    novel = get_object_or_404(Novel, pk=novel_pk, user=request.user, archived=False)
    item = get_object_or_404(Item, pk=pk, novel=novel, archived=False)
    
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES, instance=item, novel=novel)
        if form.is_valid():
            form.save()
            messages.success(request, f"Item '{item.name}' updated.")
            return redirect('item_detail', novel_pk=novel.pk, pk=item.pk)
    else:
        form = ItemForm(instance=item, novel=novel)
    
    return render(request, 'planning/item_form.html', {
        'novel': novel, 
        'form': form,
        'item': item,
        'is_edit': True
    })


# ─── Planning Entity Reorder Views ─────────────────────────────────────────

@login_required
def character_reorder_view(request, novel_pk):
    novel = get_object_or_404(Novel, pk=novel_pk, user=request.user, archived=False)
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            character_ids = data.get('character_ids', [])
            valid_pks = set(novel.characters.filter(archived=False).values_list('pk', flat=True))
            valid_ids = [int(cid) for cid in character_ids if int(cid) in valid_pks]
            for index, cid in enumerate(valid_ids):
                Character.objects.filter(pk=cid).update(order=index + 1)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)


@login_required
def location_reorder_view(request, novel_pk):
    novel = get_object_or_404(Novel, pk=novel_pk, user=request.user, archived=False)
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            location_ids = data.get('location_ids', [])
            valid_pks = set(novel.locations.filter(archived=False).values_list('pk', flat=True))
            valid_ids = [int(lid) for lid in location_ids if int(lid) in valid_pks]
            for index, lid in enumerate(valid_ids):
                Location.objects.filter(pk=lid).update(order=index + 1)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)


@login_required
def item_reorder_view(request, novel_pk):
    novel = get_object_or_404(Novel, pk=novel_pk, user=request.user, archived=False)
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            item_ids = data.get('item_ids', [])
            valid_pks = set(novel.items.filter(archived=False).values_list('pk', flat=True))
            valid_ids = [int(iid) for iid in item_ids if int(iid) in valid_pks]
            for index, iid in enumerate(valid_ids):
                Item.objects.filter(pk=iid).update(order=index + 1)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)


# ─── Scene Occurrence Helper ────────────────────────────────────────────────

def _get_scene_occurrences(entity):
    """Return SceneEntity records for this entity, with scene info, ordered by chapter/scene."""
    from .models import SceneEntity
    ct = ContentType.objects.get_for_model(entity)
    return (
        SceneEntity.objects
        .filter(content_type=ct, object_id=entity.pk)
        .select_related('scene', 'scene__chapter')
        .order_by('scene__chapter__order', 'scene__order')
    )


# ─── Relationship Helpers ────────────────────────────────────────────────────

def _get_entity(novel, entity_type, entity_id):
    """Return the entity object and its ContentType for a given type string and id."""
    model_map = {'character': Character, 'location': Location, 'item': Item}
    model = model_map.get(entity_type)
    if not model:
        return None, None
    obj = get_object_or_404(model, pk=entity_id, novel=novel)
    ct = ContentType.objects.get_for_model(model)
    return obj, ct


# Map model classes to their type string
_MODEL_TYPE_MAP = {
    'character': 'character',
    'location': 'location',
    'item': 'item',
}


def _entity_type_str(obj):
    """Return 'character', 'location', or 'item' for a given entity object."""
    return obj.__class__.__name__.lower()


def _get_relationships_for_entity(entity):
    """Return all relationships involving this entity, annotated with direction and other_type."""
    ct = ContentType.objects.get_for_model(entity)
    forward = Relationship.objects.filter(from_content_type=ct, from_object_id=entity.pk)
    reverse = Relationship.objects.filter(to_content_type=ct, to_object_id=entity.pk)
    results = []
    for r in forward:
        other = r.to_entity
        results.append({'rel': r, 'display_label': r.label, 'other': other,
                        'other_type': _entity_type_str(other), 'direction': 'forward'})
    for r in reverse:
        other = r.from_entity
        results.append({'rel': r, 'display_label': r.reverse_label, 'other': other,
                        'other_type': _entity_type_str(other), 'direction': 'reverse'})
    return results


# ─── Relationship Views ──────────────────────────────────────────────────────

@login_required
def relationship_add(request, novel_pk):
    """Add a relationship between two entities and its reverse."""
    novel = get_object_or_404(Novel, pk=novel_pk, user=request.user, archived=False)
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    from_type = request.POST.get('from_type')
    from_id = request.POST.get('from_id')
    to_type = request.POST.get('to_type')
    to_id = request.POST.get('to_id')
    label = request.POST.get('label', '').strip()
    reverse_label = request.POST.get('reverse_label', '').strip()
    notes = request.POST.get('notes', '').strip()

    from_obj, from_ct = _get_entity(novel, from_type, from_id)
    to_obj, to_ct = _get_entity(novel, to_type, to_id)

    if not from_obj or not to_obj or not label or not reverse_label:
        return JsonResponse({'error': 'Invalid data'}, status=400)

    Relationship.objects.create(
        novel=novel,
        from_content_type=from_ct, from_object_id=from_obj.pk,
        to_content_type=to_ct, to_object_id=to_obj.pk,
        label=label, reverse_label=reverse_label, notes=notes
    )

    # Return updated relationships partial for the from_entity
    relationships = _get_relationships_for_entity(from_obj)
    return render(request, 'planning/modal_relationships.html', {
        'novel': novel,
        'entity': from_obj,
        'entity_type': from_type,
        'relationships': relationships,
        'relationship_types': novel.relationship_types.all(),
        'all_characters': novel.characters.filter(archived=False),
        'all_locations': novel.locations.filter(archived=False),
        'all_items': novel.items.filter(archived=False),
    })


@login_required
def relationship_edit(request, novel_pk, pk):
    """Edit a relationship's labels and notes."""
    novel = get_object_or_404(Novel, pk=novel_pk, user=request.user, archived=False)
    rel = get_object_or_404(Relationship, pk=pk, novel=novel)

    entity_type = request.POST.get('entity_type')
    entity_id = request.POST.get('entity_id')
    entity, _ = _get_entity(novel, entity_type, entity_id)

    label = request.POST.get('label', '').strip()
    reverse_label = request.POST.get('reverse_label', '').strip()
    notes = request.POST.get('notes', '').strip()

    if label and reverse_label:
        rel.label = label
        rel.reverse_label = reverse_label
        rel.notes = notes
        rel.save()

    relationships = _get_relationships_for_entity(entity) if entity else []
    return render(request, 'planning/modal_relationships.html', {
        'novel': novel,
        'entity': entity,
        'entity_type': entity_type,
        'relationships': relationships,
        'relationship_types': novel.relationship_types.all(),
        'all_characters': novel.characters.filter(archived=False),
        'all_locations': novel.locations.filter(archived=False),
        'all_items': novel.items.filter(archived=False),
    })


@login_required
def relationship_delete(request, novel_pk, pk):
    """Delete a relationship."""
    novel = get_object_or_404(Novel, pk=novel_pk, user=request.user, archived=False)
    rel = get_object_or_404(Relationship, pk=pk, novel=novel)

    # Determine the current entity from the request so we can re-render its list
    entity_type = request.POST.get('entity_type')
    entity_id = request.POST.get('entity_id')
    entity, _ = _get_entity(novel, entity_type, entity_id)

    rel.delete()

    relationships = _get_relationships_for_entity(entity) if entity else []
    return render(request, 'planning/modal_relationships.html', {
        'novel': novel,
        'entity': entity,
        'entity_type': entity_type,
        'relationships': relationships,
        'relationship_types': novel.relationship_types.all(),
        'all_characters': novel.characters.filter(archived=False),
        'all_locations': novel.locations.filter(archived=False),
        'all_items': novel.items.filter(archived=False),
    })


@login_required
def relationship_type_list(request, novel_pk):
    """Manage relationship types for a novel."""
    novel = get_object_or_404(Novel, pk=novel_pk, user=request.user, archived=False)
    if request.method == 'POST':
        forward = request.POST.get('forward_label', '').strip()
        reverse = request.POST.get('reverse_label', '').strip()
        if forward and reverse:
            RelationshipType.objects.get_or_create(
                novel=novel, forward_label=forward,
                defaults={'reverse_label': reverse}
            )
    relationship_types = novel.relationship_types.all()
    return render(request, 'planning/modal_relationship_types.html', {
        'novel': novel,
        'relationship_types': relationship_types,
    })


@login_required
def entity_search(request, novel_pk):
    """Search for entities to link in a relationship. Returns JSON."""
    novel = get_object_or_404(Novel, pk=novel_pk, user=request.user, archived=False)
    q = request.GET.get('q', '').strip()
    entity_type = request.GET.get('type', '')
    results = []
    if entity_type == 'character':
        qs = novel.characters.filter(archived=False, fullname__icontains=q)[:10]
        results = [{'id': c.pk, 'name': c.fullname} for c in qs]
    elif entity_type == 'location':
        qs = novel.locations.filter(archived=False, name__icontains=q)[:10]
        results = [{'id': l.pk, 'name': l.name} for l in qs]
    elif entity_type == 'item':
        qs = novel.items.filter(archived=False, name__icontains=q)[:10]
        results = [{'id': i.pk, 'name': i.name} for i in qs]
    return JsonResponse({'results': results})
