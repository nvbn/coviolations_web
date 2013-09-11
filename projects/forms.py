from django import forms
from .models import Project


class RegenerateTokenForm(forms.Form):
    """Regenerate token form"""
    project = forms.ModelChoiceField(
        queryset=Project.objects.none(), required=True,
    )

    def __init__(self, user, *args, **kwargs):
        """Init form"""
        super(RegenerateTokenForm, self).__init__(*args, **kwargs)
        self.fields['project'].queryset = Project.objects.filter(
            owner=user,
        )

    def save(self):
        """Regenerate token and save"""
        project = self.cleaned_data['project']
        project.token = None
        project.save()
        return project
