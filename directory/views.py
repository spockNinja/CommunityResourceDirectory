from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from .models import Category, Organization
from .forms import OrganizationSubmitForm
from .search import search_organizations


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

    return render(request, 'directory/index.html', {
        'category_data': category_data,
    })


def submit(request):
    if request.method == 'POST':
        form = OrganizationSubmitForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('submit_success')
    else:
        form = OrganizationSubmitForm()

    return render(request, 'directory/submit.html', {'form': form})


def submit_success(request):
    return render(request, 'directory/submit_success.html')


def organization_detail(request, organization_slug):
    organization = get_object_or_404(
        Organization.objects.prefetch_related('services__category'),
        slug=organization_slug,
        approved=True,
    )
    return render(request, 'directory/organization_detail.html', {'organization': organization})


def search_organizations_api(request):
    query = request.GET.get('q', '').strip()
    organizations = search_organizations(query)
    return JsonResponse({
        'results': [
            {
                'name': organization.name,
                'slug': organization.slug,
                'address': organization.address,
                'phone': organization.phone,
                'email': organization.email,
                'website': organization.website,
                'hours_of_operation': organization.hours_of_operation,
                'services': list(organization.services.values_list('name', flat=True)),
            }
            for organization in organizations
        ]
    })
