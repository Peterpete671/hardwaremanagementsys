from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='description',
            field=models.TextField(blank=True, default='', help_text='Optional product description')
        ),
        migrations.AddField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, help_text='Product image', null=True, upload_to='products/images/'),
        ),
        migrations.AddField(
            model_name='product',
            name='barcode',
            field=models.CharField(
                blank=True, db_index=True,
                help_text='Barcode value (EAN-13, Code128, etc.). Leave blank to use SKU.',
                max_length=100, null=True, unique=True
            ),
        ),
    ]