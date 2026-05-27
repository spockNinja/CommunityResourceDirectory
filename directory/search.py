import logging

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ApiError, TransportError
from django.conf import settings
from django.db.models import Q

from .models import Organization

logger = logging.getLogger(__name__)
NAME_FIELD_BOOST = 3
SEARCH_FIELDS = [f'name^{NAME_FIELD_BOOST}', 'address', 'services', 'hours_of_operation']


def _client():
    if not settings.ELASTICSEARCH_URL:
        return None
    return Elasticsearch(settings.ELASTICSEARCH_URL)


def _ensure_index(client):
    if client.indices.exists(index=settings.ELASTICSEARCH_INDEX):
        return

    client.indices.create(
        index=settings.ELASTICSEARCH_INDEX,
        mappings={
            'properties': {
                'name': {'type': 'text'},
                'slug': {'type': 'keyword'},
                'address': {'type': 'text'},
                'phone': {'type': 'keyword'},
                'email': {'type': 'keyword'},
                'website': {'type': 'keyword'},
                'hours_of_operation': {'type': 'text'},
                'approved': {'type': 'boolean'},
                'services': {'type': 'text'},
            }
        },
    )


def _document_for_organization(organization):
    return {
        'name': organization.name,
        'slug': organization.slug,
        'address': organization.address,
        'phone': organization.phone,
        'email': organization.email,
        'website': organization.website,
        'hours_of_operation': organization.hours_of_operation,
        'approved': organization.approved,
        'services': list(organization.services.values_list('name', flat=True)),
    }


def index_organization(organization, refresh=True):
    client = _client()
    if client is None:
        return

    try:
        _ensure_index(client)
        client.index(
            index=settings.ELASTICSEARCH_INDEX,
            id=organization.pk,
            document=_document_for_organization(organization),
            refresh=refresh,
        )
    except (ApiError, TransportError):
        logger.warning('Failed to index organization %s in Elasticsearch.', organization.pk, exc_info=True)
        return


def remove_organization(organization_id):
    client = _client()
    if client is None:
        return

    try:
        if client.indices.exists(index=settings.ELASTICSEARCH_INDEX):
            client.delete(index=settings.ELASTICSEARCH_INDEX, id=organization_id, ignore=[404], refresh=True)
    except (ApiError, TransportError):
        logger.warning('Failed to remove organization %s from Elasticsearch.', organization_id, exc_info=True)
        return


def refresh_organization_index():
    client = _client()
    if client is None:
        return

    try:
        if client.indices.exists(index=settings.ELASTICSEARCH_INDEX):
            client.indices.refresh(index=settings.ELASTICSEARCH_INDEX)
    except (ApiError, TransportError):
        logger.warning('Failed to refresh Elasticsearch organization index.', exc_info=True)
        return


def _database_search(query):
    organizations = Organization.objects.filter(approved=True)
    if query:
        organizations = organizations.filter(
            Q(name__icontains=query)
            | Q(address__icontains=query)
            | Q(services__name__icontains=query)
        )
    return organizations.distinct().prefetch_related('services').order_by('slug')[:50]


def search_organizations(query):
    client = _client()
    if client is None:
        return list(_database_search(query))

    try:
        _ensure_index(client)
        if not query:
            response = client.search(
                index=settings.ELASTICSEARCH_INDEX,
                query={'term': {'approved': True}},
                sort=[{'slug': {'order': 'asc'}}],
                size=50,
            )
        else:
            response = client.search(
                index=settings.ELASTICSEARCH_INDEX,
                query={
                    'bool': {
                        'must': [
                            {
                                'multi_match': {
                                    'query': query,
                                'fields': SEARCH_FIELDS,
                                }
                            }
                        ],
                        'filter': [{'term': {'approved': True}}],
                    }
                },
                size=50,
            )

        ids = [int(hit['_id']) for hit in response['hits']['hits']]
        organizations = Organization.objects.filter(pk__in=ids, approved=True).prefetch_related('services')
        organizations_by_id = {organization.pk: organization for organization in organizations}
        return [organizations_by_id[org_id] for org_id in ids if org_id in organizations_by_id]
    except (ApiError, TransportError):
        logger.warning('Elasticsearch search failed. Falling back to database search.', exc_info=True)
        return list(_database_search(query))
