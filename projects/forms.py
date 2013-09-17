from pymongo import DESCENDING
from django import forms
from tasks.models import Tasks
from tasks.exceptions import TaskDoesNotExists
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


class FindTaskForBadgeForm(forms.Form):
    """Find task for badge form"""
    project = forms.ModelChoiceField(
        Project.objects.all(), required=True, to_field_name='name',
    )
    commit = forms.CharField(required=False)
    branch = forms.CharField(required=False)

    def get_task(self):
        """Get task"""
        filter_spec = {
            'project': self.cleaned_data['project'].name,
        }
        if self.cleaned_data.get('commit'):
            filter_spec['commit.hash'] = self.cleaned_data['commit']
        if self.cleaned_data.get('branch'):
            filter_spec['commit.branch'] = self.cleaned_data['branch']
        task = Tasks.find_one(
            filter_spec, sort=[('created', DESCENDING)], fields={
                'status': True,
            },
        )
        if task:
            return task
        else:
            raise TaskDoesNotExists(filter_spec)
