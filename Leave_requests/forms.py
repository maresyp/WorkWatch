from django import forms
from .models import Leave_request

class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = Leave_request
        fields = ['start_date', 'end_date', 'leave_type']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({'class': 'input'})
