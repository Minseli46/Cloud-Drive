# forms.py
from django import forms
from .models import File, Folder
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class FileUploadForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['file']

    def clean_file(self):
        uploaded_file = self.cleaned_data['file']
        if uploaded_file.size > 40 * 1024 * 1024:  # 40 Mo
            raise forms.ValidationError("La taille du fichier ne doit pas dépasser 40 Mo.")
        return uploaded_file

class FolderCreationForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ['name', 'parent_folder']  # Inclut le nom et éventuellement le dossier parent

    def clean_name(self):
        name = self.cleaned_data['name']
        if not name:
            raise forms.ValidationError("Le nom du dossier ne peut pas être vide.")
        return name


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
