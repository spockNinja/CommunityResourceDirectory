from django.shortcuts import render, redirect
from .models import Category, Organization
from .forms import OrganizationSubmitForm


def index(request):
    categories = Category.objects.prefetch_related(
        'services__organizations'
    ).order_by('name')

    category_data = []
    for category in categories:
        services_with_orgs = []
        for service in category.services.all():
            orgs = service.organizations.filter(approved=True)
            if orgs.exists():
                services_with_orgs.append({'service': service, 'organizations': orgs})
        if services_with_orgs:
            category_data.append({'category': category, 'services': services_with_orgs})

    # Also collect approved orgs not linked to any service
    uncategorized = Organization.objects.filter(approved=True, services__isnull=True)

    return render(request, 'directory/index.html', {
        'category_data': category_data,
        'uncategorized': uncategorized,
    })


def submit(request):
    if request.method == 'POST':
        form = OrganizationSubmitForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('submit_success')
    else:
        form = OrganizationSubmitForm()

    return render(request, 'directory/submit.html', {'form': form})


def submit_success(request):
    return render(request, 'directory/submit_success.html')
