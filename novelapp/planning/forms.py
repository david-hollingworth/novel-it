from django import forms
from .models import Character, CharacterRole, Location, LocationType, Item, ItemType

class CharacterForm(forms.ModelForm):
    class Meta:
        model = Character
        fields = [
            'fullname', 'nickname', 'first_name', 'last_name', 
            'aliases', 'gender', 'age', 'role', 
            'description', 'notes', 'personality', 'relationships', 'image'
        ]
        widgets = {
            'fullname': forms.TextInput(attrs={'class': 'mt-1 block w-full border-slate-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'nickname': forms.TextInput(attrs={'class': 'mt-1 block w-full border-slate-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'first_name': forms.TextInput(attrs={'class': 'mt-1 block w-full border-slate-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'last_name': forms.TextInput(attrs={'class': 'mt-1 block w-full border-slate-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'aliases': forms.TextInput(attrs={'class': 'mt-1 block w-full border-slate-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'gender': forms.TextInput(attrs={'class': 'mt-1 block w-full border-slate-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'age': forms.NumberInput(attrs={'class': 'mt-1 block w-full border-slate-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'role': forms.Select(attrs={'class': 'mt-1 block w-full border-slate-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'mt-1 block w-full border-slate-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'notes': forms.Textarea(attrs={'rows': 4, 'class': 'mt-1 block w-full border-slate-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'personality': forms.Textarea(attrs={'rows': 4, 'class': 'mt-1 block w-full border-slate-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'relationships': forms.Textarea(attrs={'rows': 4, 'class': 'mt-1 block w-full border-slate-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'image': forms.FileInput(attrs={'class': 'mt-1 block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'}),
        }

    def __init__(self, *args, **kwargs):
        novel = kwargs.pop('novel', None)
        super().__init__(*args, **kwargs)
        if novel:
            self.fields['role'].queryset = CharacterRole.objects.filter(novel=novel)

class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['name', 'type', 'description', 'notes', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'mt-1 block w-full border-slate-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'type': forms.Select(attrs={'class': 'mt-1 block w-full border-slate-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'mt-1 block w-full border-slate-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'notes': forms.Textarea(attrs={'rows': 4, 'class': 'mt-1 block w-full border-slate-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'image': forms.FileInput(attrs={'class': 'mt-1 block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'}),
        }

    def __init__(self, *args, **kwargs):
        novel = kwargs.pop('novel', None)
        super().__init__(*args, **kwargs)
        if novel:
            self.fields['type'].queryset = LocationType.objects.filter(novel=novel)

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'type', 'description', 'notes', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'mt-1 block w-full border-slate-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'type': forms.Select(attrs={'class': 'mt-1 block w-full border-slate-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'mt-1 block w-full border-slate-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'notes': forms.Textarea(attrs={'rows': 4, 'class': 'mt-1 block w-full border-slate-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'image': forms.FileInput(attrs={'class': 'mt-1 block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'}),
        }

    def __init__(self, *args, **kwargs):
        novel = kwargs.pop('novel', None)
        super().__init__(*args, **kwargs)
        if novel:
            self.fields['type'].queryset = ItemType.objects.filter(novel=novel)
