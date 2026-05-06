from django import forms
from .models import Organization, Service

TAILWIND_INPUT = 'w-full rounded-md border border-gray-300 px-3 py-2 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'


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
            'name': forms.TextInput(attrs={'class': TAILWIND_INPUT}),
            'address': forms.TextInput(attrs={'class': TAILWIND_INPUT}),
            'phone': forms.TextInput(attrs={'class': TAILWIND_INPUT}),
            'email': forms.EmailInput(attrs={'class': TAILWIND_INPUT}),
            'website': forms.URLInput(attrs={'class': TAILWIND_INPUT}),
            'hours_of_operation': forms.TextInput(attrs={'class': TAILWIND_INPUT}),
        }
