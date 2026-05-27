from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/organizations/search/', views.search_organizations_api, name='organization_search_api'),
    path('organizations/<slug:organization_slug>/', views.organization_detail, name='organization_detail'),
    path('submit/', views.submit, name='submit'),
    path('submit/success/', views.submit_success, name='submit_success'),
]
