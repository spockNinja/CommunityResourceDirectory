from django.contrib import admin
from .models import Category, Service, Organization


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']
    list_filter = ['category']
    search_fields = ['name']


def approve_organizations(modeladmin, request, queryset):
    queryset.update(approved=True)

approve_organizations.short_description = 'Approve selected organizations'


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email', 'approved', 'submitted_at']
    list_filter = ['approved', 'services__category']
    search_fields = ['name', 'address', 'email']
    filter_horizontal = ['services']
    actions = [approve_organizations]
    readonly_fields = ['submitted_at']
