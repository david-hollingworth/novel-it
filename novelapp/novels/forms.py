from django import forms
from .models import Novel, Part, Chapter, Scene, MANUSCRIPT_STATUS_DEFAULT

CSS_INPUT = 'mt-1 block w-full border-slate-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'
CSS_TEXTAREA = 'mt-1 block w-full border-slate-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'
CSS_SELECT = 'mt-1 block w-full border-slate-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'


class NovelForm(forms.ModelForm):
    class Meta:
        model = Novel
        fields = [
            'title',
            'subtitle',
            'author_name',
            'genre',
            'target_word_count',
            'status',
            'description',
            'premise',
            'pitch',
            'parts_enabled',
        ]
        labels = {
            'description': 'Synopsis',
            'author_name': 'Author Name',
            'target_word_count': 'Target Word Count',
            'parts_enabled': 'Enable Parts',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': CSS_INPUT}),
            'subtitle': forms.TextInput(attrs={'class': CSS_INPUT}),
            'author_name': forms.TextInput(attrs={'class': CSS_INPUT}),
            'genre': forms.TextInput(attrs={'class': CSS_INPUT}),
            'target_word_count': forms.NumberInput(attrs={'class': CSS_INPUT, 'min': 0}),
            'status': forms.Select(attrs={'class': CSS_SELECT}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': CSS_TEXTAREA}),
            'premise': forms.Textarea(attrs={'rows': 3, 'class': CSS_TEXTAREA}),
            'pitch': forms.Textarea(attrs={'rows': 3, 'class': CSS_TEXTAREA}),
            'parts_enabled': forms.RadioSelect(choices=[(True, 'Yes'), (False, 'No')]),
        }
        error_messages = {
            'title': {
                'required': "Title is required",
            },
        }


class PartForm(forms.ModelForm):
    class Meta:
        model = Part
        fields = ['title', 'summary', 'notes', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': CSS_INPUT}),
            'summary': forms.Textarea(attrs={'rows': 3, 'class': CSS_TEXTAREA}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': CSS_TEXTAREA}),
            'status': forms.Select(attrs={'class': CSS_SELECT}),
        }
        error_messages = {
            'title': {'required': 'Title is required'},
        }


class ChapterForm(forms.ModelForm):
    class Meta:
        model = Chapter
        fields = ['title', 'summary']
        widgets = {
            'title': forms.TextInput(attrs={'class': CSS_INPUT}),
            'summary': forms.Textarea(attrs={'rows': 3, 'class': CSS_TEXTAREA}),
        }


class SceneForm(forms.ModelForm):
    class Meta:
        model = Scene
        fields = ['title', 'notes', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': CSS_INPUT}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': CSS_TEXTAREA}),
            'status': forms.Select(attrs={'class': CSS_SELECT}),
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
