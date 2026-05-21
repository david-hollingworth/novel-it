from django import forms
from .models import Character, CharacterRole, Location, LocationType, Item, ItemType

ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png']
ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png']


def validate_image(image):
    """Raise ValidationError if the uploaded image is not a .jpg/.jpeg or .png."""
    if image:
        import os
        ext = os.path.splitext(image.name)[1].lower()
        if ext not in ALLOWED_IMAGE_EXTENSIONS:
            raise forms.ValidationError(
                'Only .jpg, .jpeg, and .png images are allowed.'
            )
        if hasattr(image, 'content_type') and image.content_type not in ALLOWED_IMAGE_TYPES:
            raise forms.ValidationError(
                'Only .jpg, .jpeg, and .png images are allowed.'
            )
    return image

class CharacterForm(forms.ModelForm):
    class Meta:
        model = Character
        fields = [
            'fullname', 'first_name', 'middle_name', 'last_name',
            'nickname', 'aliases', 'gender', 'age', 'role',
            'physical_description', 'interview', 'the_lie_they_believe',
            'goals_and_motivations', 'fears_and_weaknesses', 'arc_in_story',
            'image', 'description', 'notes',
        ]
        labels = {
            'fullname': 'Full Name',
            'first_name': 'First Name',
            'middle_name': 'Middle Name',
            'last_name': 'Last Name',
            'nickname': 'Nickname',
            'aliases': 'Aliases',
            'gender': 'Gender',
            'age': 'Age',
            'role': 'Role in Story',
            'physical_description': 'Physical Description',
            'interview': 'Interview',
            'the_lie_they_believe': 'The Lie They Believe',
            'goals_and_motivations': 'Goals / Motivations',
            'fears_and_weaknesses': 'Fears / Weaknesses',
            'arc_in_story': 'Arc in Story',
            'image': 'Character Image',
            'description': 'Description',
            'notes': 'Notes',
        }
        widgets = {
            'fullname': forms.TextInput(attrs={'class': 'mt-1 block w-full border-slate-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'first_name': forms.TextInput(attrs={'class': 'mt-1 block w-full border-slate-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'middle_name': forms.TextInput(attrs={'class': 'mt-1 block w-full border-slate-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'last_name': forms.TextInput(attrs={'class': 'mt-1 block w-full border-slate-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'nickname': forms.TextInput(attrs={'class': 'mt-1 block w-full border-slate-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'aliases': forms.TextInput(attrs={'class': 'mt-1 block w-full border-slate-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'gender': forms.TextInput(attrs={'class': 'mt-1 block w-full border-slate-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'age': forms.NumberInput(attrs={'class': 'mt-1 block w-full border-slate-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'role': forms.Select(attrs={'class': 'mt-1 block w-full border-slate-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'physical_description': forms.Textarea(attrs={'rows': 4, 'class': 'mt-1 block w-full border-slate-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'interview': forms.Textarea(attrs={'rows': 4, 'class': 'mt-1 block w-full border-slate-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'the_lie_they_believe': forms.Textarea(attrs={'rows': 4, 'class': 'mt-1 block w-full border-slate-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'goals_and_motivations': forms.Textarea(attrs={'rows': 4, 'class': 'mt-1 block w-full border-slate-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'fears_and_weaknesses': forms.Textarea(attrs={'rows': 4, 'class': 'mt-1 block w-full border-slate-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'arc_in_story': forms.Textarea(attrs={'rows': 4, 'class': 'mt-1 block w-full border-slate-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'image': forms.FileInput(attrs={'class': 'mt-1 block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'mt-1 block w-full border-slate-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'notes': forms.Textarea(attrs={'rows': 4, 'class': 'mt-1 block w-full border-slate-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
        }
        error_messages = {
            'fullname': {'required': 'Full name is required'},
        }

    def __init__(self, *args, **kwargs):
        novel = kwargs.pop('novel', None)
        super().__init__(*args, **kwargs)
        if novel:
            self.fields['role'].queryset = CharacterRole.objects.filter(novel=novel)

    def clean_image(self):
        return validate_image(self.cleaned_data.get('image'))


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

    def clean_image(self):
        return validate_image(self.cleaned_data.get('image'))


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'type', 'history', 'properties_and_abilities', 'description', 'notes', 'image']
        labels = {
            'name': 'Item Name',
            'type': 'Item Type',
            'history': 'History',
            'properties_and_abilities': 'Properties and Abilities',
            'description': 'Description',
            'notes': 'Notes',
            'image': 'Image',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'mt-1 block w-full border-slate-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'type': forms.Select(attrs={'class': 'mt-1 block w-full border-slate-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'history': forms.Textarea(attrs={'rows': 4, 'class': 'mt-1 block w-full border-slate-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'properties_and_abilities': forms.Textarea(attrs={'rows': 4, 'class': 'mt-1 block w-full border-slate-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'mt-1 block w-full border-slate-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'notes': forms.Textarea(attrs={'rows': 4, 'class': 'mt-1 block w-full border-slate-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500'}),
            'image': forms.FileInput(attrs={'class': 'mt-1 block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'}),
        }
        error_messages = {
            'name': {'required': 'Item name is required'},
        }

    def __init__(self, *args, **kwargs):
        novel = kwargs.pop('novel', None)
        super().__init__(*args, **kwargs)
        if novel:
            self.fields['type'].queryset = ItemType.objects.filter(novel=novel)

    def clean_image(self):
        return validate_image(self.cleaned_data.get('image'))
