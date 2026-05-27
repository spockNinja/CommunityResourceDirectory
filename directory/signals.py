from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver

from .models import Organization
from .search import index_organization, remove_organization


@receiver(post_save, sender=Organization)
def sync_organization_to_index(sender, instance, **kwargs):
    index_organization(instance)


@receiver(post_delete, sender=Organization)
def remove_organization_from_index(sender, instance, **kwargs):
    remove_organization(instance.pk)


@receiver(m2m_changed, sender=Organization.services.through)
def sync_organization_services_to_index(sender, instance, action, **kwargs):
    if action in {'post_add', 'post_remove', 'post_clear'}:
        index_organization(instance)
