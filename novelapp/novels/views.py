from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Novel, Chapter, Scene
from .forms import NovelForm, ChapterForm, SceneForm
from django.contrib import messages

@login_required
def novel_list_view(request):
    novels = Novel.objects.filter(user=request.user, archived=False)
    return render(request, 'novels/novel_list.html', {'novels': novels})

@login_required
def novel_detail_view(request, pk):
    novel = get_object_or_404(Novel, pk=pk, user=request.user, archived=False)
    chapters = novel.chapters.filter(archived=False).order_by('order')
    return render(request, 'novels/novel_detail.html', {'novel': novel, 'chapters': chapters})

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
    return render(request, 'novels/novel_form.html', {'form': form})

@login_required
def chapter_detail_view(request, novel_pk, chapter_pk):
    novel = get_object_or_404(Novel, pk=novel_pk, user=request.user, archived=False)
    chapter = get_object_or_404(Chapter, pk=chapter_pk, novel=novel, archived=False)
    scenes = chapter.scenes.filter(archived=False).order_by('order')
    return render(request, 'novels/chapter_detail.html', {'novel': novel, 'chapter': chapter, 'scenes': scenes})

@login_required
def scene_view(request, novel_pk, chapter_pk, scene_pk):
    novel = get_object_or_404(Novel, pk=novel_pk, user=request.user, archived=False)
    chapter = get_object_or_404(Chapter, pk=chapter_pk, novel=novel, archived=False)
    scene = get_object_or_404(Scene, pk=scene_pk, chapter=chapter, archived=False)
    return render(request, 'novels/scene_editor.html', {'novel': novel, 'chapter': chapter, 'scene': scene})
@login_required
def chapter_create_view(request, novel_pk):
    novel = get_object_or_404(Novel, pk=novel_pk, user=request.user, archived=False)
    if request.method == 'POST':
        form = ChapterForm(request.POST)
        if form.is_valid():
            chapter = form.save(commit=False)
            chapter.novel = novel
            if not chapter.order:
                chapter.order = novel.chapters.count() + 1
            chapter.save()
            messages.success(request, f"Chapter '{chapter.title}' created.")
            return redirect('novel_detail', pk=novel.pk)
    else:
        form = ChapterForm(initial={'order': novel.chapters.count() + 1})
    return render(request, 'novels/chapter_form.html', {'novel': novel, 'form': form})

@login_required
def scene_create_view(request, novel_pk, chapter_pk):
    novel = get_object_or_404(Novel, pk=novel_pk, user=request.user, archived=False)
    chapter = get_object_or_404(Chapter, pk=chapter_pk, novel=novel, archived=False)
    if request.method == 'POST':
        form = SceneForm(request.POST)
        if form.is_valid():
            scene = form.save(commit=False)
            scene.chapter = chapter
            if not scene.order:
                scene.order = chapter.scenes.count() + 1
            scene.save()
            messages.success(request, f"Scene '{scene.title}' created.")
            return redirect('chapter_detail', novel_pk=novel.pk, chapter_pk=chapter.pk)
    else:
        form = SceneForm(initial={'order': chapter.scenes.count() + 1})
    return render(request, 'novels/scene_form.html', {'novel': novel, 'chapter': chapter, 'form': form})
