from django import forms
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'novelapp.settings')
django.setup()

f = forms.EmailField()
try:
    f.clean('invalid')
    print('clean success')
except forms.ValidationError as e:
    print(e.messages)
