from django import forms
from .models import Novel, Part, Chapter, Scene, MANUSCRIPT_STATUS_DEFAULT


class PartForm(forms.ModelForm):
    class Meta:
        model = Part
        fields = ['title', 'summary', 'notes', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'mt-1 block w-full border-slate-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            'summary': forms.Textarea(attrs={'rows': 3, 'class': 'mt-1 block w-full border-slate-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'mt-1 block w-full border-slate-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            'status': forms.Select(attrs={'class': 'mt-1 block w-full border-slate-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
        }
        error_messages = {
            'title': {'required': 'Title is required'},
        }


class NovelForm(forms.ModelForm):
    class Meta:
        model = Novel
        fields = ['title', 'description', 'premise', 'genre', 'parts_enabled']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'mt-1 block w-full border-slate-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'mt-1 block w-full border-slate-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            'premise': forms.Textarea(attrs={'rows': 3, 'class': 'mt-1 block w-full border-slate-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            'genre': forms.TextInput(attrs={'class': 'mt-1 block w-full border-slate-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'}),
            'parts_enabled': forms.RadioSelect(choices=[(True, 'Yes'), (False, 'No')]),
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
            return MANUSCRIPT_STATUS_DEFAULT
        return status
