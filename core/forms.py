from django import forms
from .models import StatementFile, Project

# For project naming
class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., December 2025 Audit'})
        }

# For file uploading
class UploadFileForm(forms.ModelForm):
    class Meta:
        model = StatementFile
        fields = ['file', 'file_type']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'file_type': forms.Select(attrs={'class': 'form-select'}),
        }