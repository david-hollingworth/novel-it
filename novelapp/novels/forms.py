from django import forms
from .models import Novel, Chapter, Scene

class NovelForm(forms.ModelForm):
    class Meta:
        model = Novel
        fields = ['title', 'description', 'premise', 'genre']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'mt-1 block w-full border-slate-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'mt-1 block w-full border-slate-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            'premise': forms.Textarea(attrs={'rows': 3, 'class': 'mt-1 block w-full border-slate-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            'genre': forms.TextInput(attrs={'class': 'mt-1 block w-full border-slate-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
        }
        error_messages = {
            'title': {
                'required': "Title is required",
            },
        }

class ChapterForm(forms.ModelForm):
    class Meta:
        model = Chapter
        fields = ['title', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'mt-1 block w-full border-slate-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            'order': forms.NumberInput(attrs={'class': 'mt-1 block w-full border-slate-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
        }

class SceneForm(forms.ModelForm):
    class Meta:
        model = Scene
        fields = ['title', 'content', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'mt-1 block w-full border-slate-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            'content': forms.Textarea(attrs={'rows': 5, 'class': 'mt-1 block w-full border-slate-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            'order': forms.NumberInput(attrs={'class': 'mt-1 block w-full border-slate-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
        }
