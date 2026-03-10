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
        fields = ['title', 'summary']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'mt-1 block w-full border-slate-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            'summary': forms.Textarea(attrs={'rows': 3, 'class': 'mt-1 block w-full border-slate-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
        }

class SceneForm(forms.ModelForm):
    class Meta:
        model = Scene
        fields = ['title', 'notes', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'mt-1 block w-full border-slate-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'mt-1 block w-full border-slate-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            'status': forms.Select(attrs={'class': 'mt-1 block w-full border-slate-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
        }
        error_messages = {
            'title': {
                'required': 'Title is required',
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].required = False

    def clean_status(self):
        status = self.cleaned_data.get('status')
        if not status:
            return Scene.STATUS_NOT_STARTED
        return status
