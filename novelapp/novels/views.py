from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Max, F
import json
from .models import Novel, Part, Chapter, Scene
from .forms import NovelForm, PartForm, ChapterForm, SceneForm

@login_required
def part_detail_view(request, novel_pk, part_pk):
    novel = get_object_or_404(Novel, pk=novel_pk, user=request.user, archived=False)
    part = get_object_or_404(Part, pk=part_pk, novel=novel, archived=False)
    chapters = part.chapters.filter(archived=False)
    return render(request, 'novels/part_detail.html', {
        'novel': novel,
        'part': part,
        'chapters': chapters,
    })


@login_required
def part_edit_view(request, novel_pk, part_pk):
    novel = get_object_or_404(Novel, pk=novel_pk, user=request.user, archived=False)
    part = get_object_or_404(Part, pk=part_pk, novel=novel, archived=False)
    if request.method == 'POST':
        form = PartForm(request.POST, instance=part)
        if form.is_valid():
            form.save()
            messages.success(request, f"Part '{part.title}' updated successfully.")
            return redirect('part_detail', novel_pk=novel_pk, part_pk=part.pk)
    else:
        form = PartForm(instance=part)
    return render(request, 'novels/part_form.html', {
        'form': form,
        'novel': novel,
        'part': part,
        'title': 'Edit Part',
    })


@login_required
def part_create_view(request, novel_pk):
    novel = get_object_or_404(Novel, pk=novel_pk, user=request.user, archived=False)
    if request.method == 'POST':
        form = PartForm(request.POST)
        if form.is_valid():
            part = form.save(commit=False)
            part.novel = novel
            # Place after the last non-default part
            last_order = novel.parts.filter(archived=False).exclude(title='_default').aggregate(
                Max('order'))['order__max'] or 0
            part.order = last_order + 1
            part.save()
            messages.success(request, f"Part '{part.title}' created.")
            return redirect('novel_detail', pk=novel.pk)
    else:
        form = PartForm()
    return render(request, 'novels/part_form.html', {
        'form': form,
        'novel': novel,
        'title': 'Add Part',
    })


@login_required
def novel_list_view(request):
    novels = Novel.objects.filter(user=request.user, archived=False)
    return render(request, 'novels/novel_list.html', {'novels': novels})

@login_required
def novel_create_view(request):
    if request.method == 'POST':
        form = NovelForm(request.POST)
        if form.is_valid():
            novel = form.save(commit=False)
            novel.user = request.user
            novel.save()
            messages.success(request, f"Novel '{novel.title}' created successfully.")
            return redirect('novel_detail', pk=novel.pk)
    else:
        form = NovelForm()
    return render(request, 'novels/novel_form.html', {'form': form, 'title': 'Create New Novel'})

@login_required
def novel_detail_view(request, pk):
    novel = get_object_or_404(Novel, pk=pk, user=request.user, archived=False)
    parts = novel.parts.filter(archived=False)
    return render(request, 'novels/novel_detail.html', {
        'novel': novel,
        'parts': parts,
    })

@login_required
def novel_update_view(request, pk):
    novel = get_object_or_404(Novel, pk=pk, archived=False)
    if novel.user != request.user:
        messages.error(request, "You do not have permission to edit this novel.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = NovelForm(request.POST, instance=novel)
        if form.is_valid():
            form.save()
            messages.success(request, f"Novel '{novel.title}' updated successfully.")
            return redirect('novel_detail', pk=novel.pk)
    else:
        form = NovelForm(instance=novel)
    return render(request, 'novels/novel_form.html', {'form': form, 'novel': novel, 'title': 'Edit Novel'})

@login_required
def novel_delete_view(request, pk):
    novel = get_object_or_404(Novel, pk=pk, user=request.user)
    if request.method == 'POST':
        title = novel.title
        novel.delete()
        messages.success(request, f"Novel '{title}' deleted successfully.")
        return redirect('novel_list')
    return render(request, 'novels/novel_confirm_delete.html', {'novel': novel})

@login_required
def chapter_create_view(request, novel_pk):
    novel = get_object_or_404(Novel, pk=novel_pk, user=request.user, archived=False)
    # Chapters are always parented off a Part. When parts are not enabled the
    # novel has a single transparent Part — get or create it.
    part, _ = Part.objects.get_or_create(
        novel=novel,
        order=1,
        defaults={'title': '_default'},
    )
    if request.method == 'POST':
        form = ChapterForm(request.POST)
        if form.is_valid():
            chapter = form.save(commit=False)
            chapter.part = part
            chapter.order = part.get_chapter_count() + 1
            chapter.save()
            messages.success(request, f"Chapter '{chapter.title}' created.")
            if novel.parts_enabled:
                return redirect('part_detail', novel_pk=novel.pk, part_pk=part.pk)
            return redirect('novel_detail', pk=novel.pk)
    else:
        form = ChapterForm()
    return render(request, 'novels/chapter_form.html', {'form': form, 'novel': novel})

@login_required
def chapter_detail_view(request, novel_pk, chapter_pk):
    chapter = get_object_or_404(Chapter, pk=chapter_pk, part__novel__pk=novel_pk, part__novel__user=request.user, archived=False)
    scenes = chapter.scenes.filter(archived=False)
    return render(request, 'novels/chapter_detail.html', {
        'novel': chapter.novel,
        'chapter': chapter,
        'scenes': scenes
    })

@login_required
def scene_create_view(request, novel_pk, chapter_pk):
    chapter = get_object_or_404(Chapter, pk=chapter_pk, part__novel__pk=novel_pk, part__novel__user=request.user, archived=False)
    if request.method == 'POST':
        form = SceneForm(request.POST)
        if form.is_valid():
            scene = form.save(commit=False)
            scene.chapter = chapter
            scene.order = chapter.get_scene_count() + 1
            scene.save()
            messages.success(request, f"Scene '{scene.title}' created.")
            return redirect('chapter_detail', novel_pk=novel_pk, chapter_pk=chapter_pk)
    else:
        form = SceneForm()
    return render(request, 'novels/scene_form.html', {
        'form': form,
        'novel': chapter.novel,
        'chapter': chapter
    })

@login_required
def scene_editor_view(request, novel_pk, chapter_pk, scene_pk):
    scene = get_object_or_404(Scene, pk=scene_pk, chapter__pk=chapter_pk, chapter__part__novel__pk=novel_pk, chapter__part__novel__user=request.user, archived=False)
    active_scenes = list(scene.chapter.scenes.filter(archived=False).order_by('order'))
    current_index = next((i for i, s in enumerate(active_scenes) if s.pk == scene.pk), None)
    prev_scene = active_scenes[current_index - 1] if current_index and current_index > 0 else None
    next_scene = active_scenes[current_index + 1] if current_index is not None and current_index < len(active_scenes) - 1 else None
    return render(request, 'novels/scene_editor.html', {
        'novel': scene.chapter.novel,
        'chapter': scene.chapter,
        'scene': scene,
        'prev_scene': prev_scene,
        'next_scene': next_scene,
    })

@login_required
def scene_edit_view(request, novel_pk, chapter_pk, scene_pk):
    scene = get_object_or_404(Scene, pk=scene_pk, chapter__pk=chapter_pk, chapter__part__novel__pk=novel_pk, chapter__part__novel__user=request.user, archived=False)
    if request.method == 'POST':
        form = SceneForm(request.POST, instance=scene)
        if form.is_valid():
            form.save()
            messages.success(request, f"Scene '{scene.title}' updated successfully.")
            return redirect('chapter_detail', novel_pk=novel_pk, chapter_pk=chapter_pk)
    else:
        form = SceneForm(instance=scene)
    return render(request, 'novels/scene_form.html', {
        'form': form,
        'novel': scene.chapter.novel,
        'chapter': scene.chapter,
        'scene': scene,
    })


@login_required
def scene_archive_view(request, novel_pk, chapter_pk, scene_pk):
    scene = get_object_or_404(Scene, pk=scene_pk, chapter__pk=chapter_pk, chapter__part__novel__pk=novel_pk, chapter__part__novel__user=request.user, archived=False)
    if request.method == 'POST':
        scene.archived = True
        scene.save()
        messages.success(request, f"Scene '{scene.title}' archived successfully.")
        return redirect('chapter_detail', novel_pk=novel_pk, chapter_pk=chapter_pk)
    return render(request, 'novels/scene_confirm_archive.html', {
        'scene': scene,
        'novel': scene.chapter.novel,
        'chapter': scene.chapter,
    })


@login_required
def scene_restore_view(request, novel_pk, chapter_pk, scene_pk):
    scene = get_object_or_404(Scene, pk=scene_pk, chapter__pk=chapter_pk, chapter__part__novel__pk=novel_pk, chapter__part__novel__user=request.user, archived=True)
    if request.method == 'POST':
        scene.archived = False
        scene.save()
        messages.success(request, f"Scene '{scene.title}' restored successfully.")
        return redirect('chapter_detail', novel_pk=novel_pk, chapter_pk=chapter_pk)
    return render(request, 'novels/scene_confirm_restore.html', {
        'scene': scene,
        'novel': scene.chapter.novel,
        'chapter': scene.chapter,
    })


@login_required
def scene_delete_view(request, novel_pk, chapter_pk, scene_pk):
    scene = get_object_or_404(Scene, pk=scene_pk, chapter__pk=chapter_pk, chapter__part__novel__pk=novel_pk, chapter__part__novel__user=request.user)
    if request.method == 'POST':
        title = scene.title
        scene.delete()
        messages.success(request, f"Scene '{title}' deleted permanently.")
        return redirect('chapter_detail', novel_pk=novel_pk, chapter_pk=chapter_pk)
    return render(request, 'novels/scene_confirm_delete.html', {
        'scene': scene,
        'novel': scene.chapter.novel,
        'chapter': scene.chapter,
    })


@login_required
def archived_scene_list_view(request, novel_pk, chapter_pk):
    chapter = get_object_or_404(Chapter, pk=chapter_pk, part__novel__pk=novel_pk, part__novel__user=request.user)
    scenes = chapter.scenes.filter(archived=True)
    return render(request, 'novels/archived_scene_list.html', {
        'novel': chapter.novel,
        'chapter': chapter,
        'scenes': scenes,
    })


@login_required
def scene_reorder_view(request, novel_pk, chapter_pk):
    chapter = get_object_or_404(Chapter, pk=chapter_pk, part__novel__pk=novel_pk, part__novel__user=request.user)
    if request.method == 'POST':
        try:
            from django.db import transaction
            data = json.loads(request.body)
            scene_ids = data.get('scene_ids', [])
            active_pks = set(chapter.scenes.filter(archived=False).values_list('pk', flat=True))
            valid_ids = [int(sid) for sid in scene_ids if int(sid) in active_pks]
            if valid_ids:
                with transaction.atomic():
                    # Step 1: Move to unique negative temp values to avoid unique_together conflicts
                    for index, sid in enumerate(valid_ids):
                        chapter.scenes.filter(pk=sid).update(order=-(index + 1))
                    # Step 2: Assign final positive orders
                    for index, sid in enumerate(valid_ids):
                        chapter.scenes.filter(pk=sid).update(order=index + 1)
            return JsonResponse({'status': 'success'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return redirect('chapter_detail', novel_pk=novel_pk, chapter_pk=chapter_pk)


@login_required
def novel_archive_view(request, pk):
    novel = get_object_or_404(Novel, pk=pk, user=request.user, archived=False)
    if request.method == 'POST':
        novel.archived = True
        novel.save()
        messages.success(request, f"Novel '{novel.title}' archived successfully.")
        return redirect('novel_list')
    return render(request, 'novels/novel_confirm_archive.html', {'novel': novel})

@login_required
def novel_unarchive_view(request, pk):
    novel = get_object_or_404(Novel, pk=pk, user=request.user, archived=True)
    if request.method == 'POST':
        novel.archived = False
        novel.save()
        messages.success(request, f"Novel '{novel.title}' unarchived successfully.")
        return redirect('novel_list')
    return render(request, 'novels/novel_confirm_unarchive.html', {'novel': novel})

@login_required
def archived_novel_list_view(request):
    novels = Novel.objects.filter(user=request.user, archived=True)
    return render(request, 'novels/archived_novel_list.html', {'novels': novels})

@login_required
def chapter_edit_view(request, novel_pk, chapter_pk):
    chapter = get_object_or_404(Chapter, pk=chapter_pk, part__novel__pk=novel_pk, part__novel__user=request.user, archived=False)
    if request.method == 'POST':
        form = ChapterForm(request.POST, instance=chapter)
        if form.is_valid():
            form.save()
            messages.success(request, f"Chapter '{chapter.title}' updated successfully.")
            return redirect('chapter_detail', novel_pk=novel_pk, chapter_pk=chapter.pk)
    else:
        form = ChapterForm(instance=chapter)
    return render(request, 'novels/chapter_form.html', {'form': form, 'novel': chapter.novel, 'chapter': chapter, 'title': 'Edit Chapter'})

@login_required
def chapter_archive_view(request, novel_pk, chapter_pk):
    chapter = get_object_or_404(Chapter, pk=chapter_pk, part__novel__pk=novel_pk, part__novel__user=request.user, archived=False)
    if request.method == 'POST':
        chapter.archived = True
        chapter.save()
        messages.success(request, f"Chapter '{chapter.title}' archived successfully.")
        if chapter.novel.parts_enabled:
            return redirect('part_detail', novel_pk=novel_pk, part_pk=chapter.part.pk)
        return redirect('novel_detail', pk=novel_pk)
    return render(request, 'novels/chapter_confirm_archive.html', {'chapter': chapter, 'novel': chapter.novel})


@login_required
def scene_move_view(request, novel_pk, scene_pk):
    """
    Move a scene from one chapter to another within the same novel.
    Accepts POST with JSON body: {"target_chapter_id": N}
    - Preserves all scene metadata (R-FUNC-00311)
    - Recalculates word counts on both source and destination chapters (R-FUNC-00312)
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

    scene = get_object_or_404(
        Scene,
        pk=scene_pk,
        chapter__part__novel__pk=novel_pk,
        chapter__part__novel__user=request.user,
        archived=False
    )

    try:
        data = json.loads(request.body)
        target_chapter_id = int(data['target_chapter_id'])
        target_chapter = get_object_or_404(
            Chapter, pk=target_chapter_id, part__novel__pk=novel_pk, archived=False
        )

        # No-op if dropped back onto the same chapter
        if target_chapter.pk == scene.chapter.pk:
            return JsonResponse({'status': 'success'})

        with transaction.atomic():
            source_chapter = scene.chapter
            part_pk = source_chapter.part.pk
            novel = source_chapter.novel
            old_order = scene.order

            # Append to end of destination chapter
            max_order = target_chapter.scenes.filter(archived=False).aggregate(
                Max('order'))['order__max'] or 0

            # Use update_fields to bypass Scene.save() cascade — we trigger
            # word count recalculation manually on both chapters below
            scene.chapter = target_chapter
            scene.order = max_order + 1
            scene.save(update_fields=['chapter', 'order'])

            # Close the gap left in the source chapter
            # (avoids sparse order values and keeps unique_together clean)
            source_chapter.scenes.filter(
                archived=False, order__gt=old_order
            ).update(order=F('order') - 1)

            # Recalculate word counts on both chapters (each also updates novel)
            source_chapter.update_word_count()
            target_chapter.update_word_count()

        # Refresh from DB to get accurate post-move counts
        source_chapter.refresh_from_db()
        target_chapter.refresh_from_db()

        return JsonResponse({
            'status': 'success',
            'scene_id': scene.pk,
            'source_chapter_id': source_chapter.pk,
            'source_word_count': source_chapter.word_count,
            'source_scene_count': source_chapter.scenes.filter(archived=False).count(),
            'target_chapter_id': target_chapter.pk,
            'target_word_count': target_chapter.word_count,
            'target_scene_count': target_chapter.scenes.filter(archived=False).count(),
        })

    except (KeyError, ValueError, TypeError):
        return JsonResponse({'status': 'error', 'message': 'Invalid data'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
def scene_save_view(request, novel_pk, chapter_pk, scene_pk):
    """
    API endpoint to save scene content from the editor.
    Accepts POST with JSON body: {"content": "..."}
    Returns JSON: {"status": "success", "word_count": N} or error.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

    scene = get_object_or_404(
        Scene,
        pk=scene_pk,
        chapter__pk=chapter_pk,
        chapter__part__novel__pk=novel_pk,
        chapter__part__novel__user=request.user,
        archived=False
    )

    try:
        data = json.loads(request.body)
        content = data.get('content', '')
        scene.content = content
        scene.save()  # triggers word count recalculation via Scene.save()

        # Scan for entity mentions and update SceneEntity records
        from planning.scan import scan_scene_entities
        try:
            scan_scene_entities(scene)
        except Exception as scan_err:
            import logging
            logging.getLogger(__name__).error('scan_scene_entities failed: %s', scan_err, exc_info=True)

        return JsonResponse({'status': 'success', 'word_count': scene.word_count})
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def chapter_restore_view(request, novel_pk, chapter_pk):
    chapter = get_object_or_404(Chapter, pk=chapter_pk, part__novel__pk=novel_pk, part__novel__user=request.user, archived=True)
    if request.method == 'POST':
        chapter.archived = False
        chapter.save()
        messages.success(request, f"Chapter '{chapter.title}' restored successfully.")
        if chapter.novel.parts_enabled:
            return redirect('part_detail', novel_pk=novel_pk, part_pk=chapter.part.pk)
        return redirect('novel_detail', pk=novel_pk)
    return render(request, 'novels/chapter_confirm_restore.html', {'chapter': chapter, 'novel': chapter.novel})

@login_required
def chapter_delete_view(request, novel_pk, chapter_pk):
    chapter = get_object_or_404(Chapter, pk=chapter_pk, part__novel__pk=novel_pk, part__novel__user=request.user)
    if request.method == 'POST':
        title = chapter.title
        part_pk = chapter.part.pk
        parts_enabled = chapter.novel.parts_enabled
        chapter.delete()
        messages.success(request, f"Chapter '{title}' deleted permanently.")
        if parts_enabled:
            return redirect('part_detail', novel_pk=novel_pk, part_pk=part_pk)
        return redirect('novel_detail', pk=novel_pk)
    return render(request, 'novels/chapter_confirm_delete.html', {'chapter': chapter, 'novel': chapter.novel})

@login_required
def archived_chapter_list_view(request, novel_pk):
    novel = get_object_or_404(Novel, pk=novel_pk, user=request.user)
    chapters = Chapter.objects.filter(part__novel=novel, archived=True)
    return render(request, 'novels/archived_chapter_list.html', {'novel': novel, 'chapters': chapters})

@login_required
def chapter_reorder_view(request, novel_pk):
    novel = get_object_or_404(Novel, pk=novel_pk, user=request.user)
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            chapter_ids = data.get('chapter_ids', [])

            # Fetch all chapters for this novel to batch update or verify
            chapters = {str(c.pk): c for c in Chapter.objects.filter(part__novel=novel, archived=False)}

            valid_ids = [cid for cid in chapter_ids if str(cid) in chapters]
            
            # Update order
            for index, cid in enumerate(valid_ids):
                chapter = chapters[str(cid)]
                chapter.order = index + 1
                chapter.save()
                
            return JsonResponse({'status': 'success'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return redirect('novel_detail', pk=novel_pk)



