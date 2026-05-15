import shutil
import tempfile

from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.utils import override_settings
from django.conf import settings
from .models import Category, Service, Organization

TEST_MEDIA_ROOT = tempfile.mkdtemp()


def tearDownModule():
    shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)


class ModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Health')
        self.service = Service.objects.create(name='Mental Health', category=self.category)
        self.org = Organization.objects.create(
            name='Test Org',
            address='123 Main St',
            phone='555-1234',
            email='test@example.com',
            website='https://example.com',
            hours_of_operation='Mon-Fri 9am-5pm',
        )
        self.org.services.add(self.service)

    def test_category_str(self):
        self.assertEqual(str(self.category), 'Health')

    def test_service_str(self):
        self.assertEqual(str(self.service), 'Mental Health (Health)')

    def test_organization_str(self):
        self.assertEqual(str(self.org), 'Test Org')

    def test_organization_not_approved_by_default(self):
        self.assertFalse(self.org.approved)

    def test_organization_slug_is_generated_from_name(self):
        self.assertEqual(self.org.slug, 'test-org')

    def test_organization_slug_falls_back_for_non_slugifiable_name(self):
        org = Organization.objects.create(name='!!!')
        self.assertEqual(org.slug, 'organization')

    def test_service_links_to_category(self):
        self.assertEqual(self.service.category, self.category)

    def test_organization_services_m2m(self):
        self.assertIn(self.service, self.org.services.all())


class IndexViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Food')
        self.service = Service.objects.create(name='Food Pantry', category=self.category)

    def test_index_loads(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_index_shows_only_approved_orgs(self):
        unapproved = Organization.objects.create(name='Unapproved Org', approved=False)
        unapproved.services.add(self.service)
        approved = Organization.objects.create(name='Approved Org', approved=True)
        approved.services.add(self.service)

        response = self.client.get(reverse('index'))
        content = response.content.decode()
        self.assertIn('Approved Org', content)
        self.assertNotIn('Unapproved Org', content)

    def test_index_uses_constance_community_name(self):
        response = self.client.get(reverse('index'))
        self.assertContains(response, 'Community Resource Directory')

    def test_index_links_to_organization_slug_detail(self):
        approved = Organization.objects.create(name='Sluggy Org', approved=True)
        approved.services.add(self.service)
        response = self.client.get(reverse('index'))
        self.assertContains(response, reverse('organization_detail', args=[approved.slug]))


class SubmitViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Housing')
        self.service = Service.objects.create(name='Shelter', category=self.category)

    def test_submit_page_loads(self):
        response = self.client.get(reverse('submit'))
        self.assertEqual(response.status_code, 200)

    def test_submit_form_creates_unapproved_org(self):
        response = self.client.post(reverse('submit'), {
            'name': 'New Housing Org',
            'address': '456 Oak Ave',
            'phone': '555-5678',
            'email': 'housing@example.com',
            'website': 'https://housing.example.com',
            'hours_of_operation': 'Mon-Sun 24/7',
            'services': [self.service.pk],
        })
        self.assertRedirects(response, reverse('submit_success'))
        org = Organization.objects.get(name='New Housing Org')
        self.assertFalse(org.approved)
        self.assertIn(self.service, org.services.all())

    def test_submit_success_page_loads(self):
        response = self.client.get(reverse('submit_success'))
        self.assertEqual(response.status_code, 200)

    def test_submit_invalid_form(self):
        response = self.client.post(reverse('submit'), {'name': ''})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Organization.objects.filter(name='').exists())

    @override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
    def test_submit_form_allows_optional_image_upload(self):
        image = SimpleUploadedFile(
            'org-image.gif',
            b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;',
            content_type='image/gif',
        )
        response = self.client.post(reverse('submit'), {
            'name': 'Image Org',
            'services': [self.service.pk],
            'image': image,
        })
        self.assertRedirects(response, reverse('submit_success'))
        org = Organization.objects.get(name='Image Org')
        self.assertTrue(org.image.name.endswith('org-image.gif'))


class OrganizationDetailViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Health')
        self.service = Service.objects.create(name='Clinic', category=self.category)
        self.approved_org = Organization.objects.create(
            name='Approved Clinic',
            address='123 Main St',
            phone='555-1234',
            email='approved@example.com',
            website='https://approved.example.com',
            hours_of_operation='Mon-Fri 9am-5pm',
            approved=True,
        )
        self.approved_org.services.add(self.service)
        self.unapproved_org = Organization.objects.create(name='Pending Org', approved=False)

    def test_approved_organization_detail_loads(self):
        response = self.client.get(reverse('organization_detail', args=[self.approved_org.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Approved Clinic')
        self.assertContains(response, '123 Main St')
        self.assertContains(response, 'Clinic')

    def test_unapproved_organization_detail_returns_404(self):
        response = self.client.get(reverse('organization_detail', args=[self.unapproved_org.slug]))
        self.assertEqual(response.status_code, 404)

    def test_organization_slug_collision_gets_suffix(self):
        first = Organization.objects.create(name='Duplicate Name')
        second = Organization.objects.create(name='Duplicate Name')
        self.assertEqual(first.slug, 'duplicate-name')
        self.assertEqual(second.slug, 'duplicate-name-2')


class StaticFilesConfigTests(TestCase):
    def test_whitenoise_middleware_is_enabled_after_security_middleware(self):
        security_index = settings.MIDDLEWARE.index('django.middleware.security.SecurityMiddleware')
        self.assertEqual(
            settings.MIDDLEWARE[security_index + 1],
            'whitenoise.middleware.WhiteNoiseMiddleware',
        )

    def test_staticfiles_storage_uses_whitenoise_manifest_storage(self):
        self.assertEqual(
            settings.STORAGES['staticfiles']['BACKEND'],
            'whitenoise.storage.CompressedManifestStaticFilesStorage',
        )
