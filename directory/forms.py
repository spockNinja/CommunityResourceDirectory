from django import forms
from .models import Organization, Service


class OrganizationSubmitForm(forms.ModelForm):
    services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.select_related('category').order_by('category__name', 'name'),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Services Provided',
    )

    class Meta:
        model = Organization
        fields = ['name', 'address', 'phone', 'email', 'website', 'hours_of_operation', 'services']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'hours_of_operation': forms.TextInput(attrs={'class': 'form-control'}),
        }
