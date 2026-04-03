from django.test import TestCase, Client
from django.urls import reverse
from .models import Category, Service, Organization


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
