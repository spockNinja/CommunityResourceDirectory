from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=200)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Service(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='services')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.category})'


class Organization(models.Model):
    name = models.CharField(max_length=300)
    slug = models.SlugField(max_length=320, unique=True)
    address = models.CharField(max_length=500, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    image = models.FileField(upload_to='organization_images/', blank=True)
    hours_of_operation = models.CharField(max_length=300, blank=True)
    services = models.ManyToManyField(Service, blank=True, related_name='organizations')
    approved = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)[:300] or 'organization'
            slug = base_slug
            suffix = 2
            while Organization.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                suffix_text = f'-{suffix}'
                slug = f'{base_slug[:300 - len(suffix_text)]}{suffix_text}'
                suffix += 1
            self.slug = slug
        super().save(*args, **kwargs)
