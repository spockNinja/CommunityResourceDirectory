from django.db import migrations, models
from django.utils.text import slugify


def populate_organization_slugs(apps, schema_editor):
    Organization = apps.get_model('directory', 'Organization')

    for organization in Organization.objects.order_by('id'):
        base_slug = slugify(organization.name)[:300] or 'organization'
        slug = base_slug
        suffix = 2
        while Organization.objects.filter(slug=slug).exclude(pk=organization.pk).exists():
            suffix_text = f'-{suffix}'
            slug = f'{base_slug[:300 - len(suffix_text)]}{suffix_text}'
            suffix += 1
        organization.slug = slug
        organization.save(update_fields=['slug'])


class Migration(migrations.Migration):

    dependencies = [
        ('directory', '0002_organization_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='slug',
            field=models.SlugField(max_length=320, null=True, unique=True),
        ),
        migrations.RunPython(populate_organization_slugs, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='organization',
            name='slug',
            field=models.SlugField(max_length=320, unique=True),
        ),
    ]
