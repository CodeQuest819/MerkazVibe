from django.db import migrations, models
import django.contrib.auth.models
import uuid

def create_initial_data(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Category = apps.get_model('store', 'Category')
    Product = apps.get_model('store', 'Product')
    
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123'
    )
    
    categories = [
        ('Blue Apparel', 'blue-apparel'),
        ('Azure Accessories', 'azure-accessories'),
        ('Indigo Decor', 'indigo-decor'),
        ('Sky Blue Tech', 'sky-blue-tech'),
    ]
    
    for name, slug in categories:
        Category.objects.create(name=name, slug=slug)
    
    widget_category = Category.objects.get(slug='blue-apparel')
    Product.objects.create(
        name='Blue Widget 1',
        description='A high-quality blue widget.',
        price=19.99,
        quantity=100,
        category=widget_category
    )
    Product.objects.create(
        name='Blue Widget 2',
        description='Another great blue widget.',
        price=24.50,
        quantity=50,
        category=widget_category
    )

class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', models.CharField(max_length=100, blank=True)),
                ('language', models.CharField(max_length=100, blank=True)),
                ('phone', models.CharField(max_length=20, blank=True)),
                ('address', models.TextField(blank=True)),
                ('user', models.OneToOneField(on_delete=models.CASCADE, to='auth.User')),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('quantity', models.PositiveIntegerField()),
                ('image', models.ImageField(blank=True, null=True, upload_to='products/')),
                ('zip_file', models.FileField(blank=True, null=True, upload_to='product_zips/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('category', models.ForeignKey(on_delete=models.CASCADE, to='store.category')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_id', models.CharField(max_length=50, unique=True)),
                ('order_date', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('shipped', 'Shipped'), ('delivered', 'Delivered'), ('cancelled', 'Cancelled')], default='pending', max_length=20)),
                ('total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('user', models.ForeignKey(on_delete=models.CASCADE, to='auth.user')),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('order', models.ForeignKey(on_delete=models.CASCADE, to='store.order')),
                ('product', models.ForeignKey(on_delete=models.CASCADE, to='store.product')),
            ],
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=models.CASCADE, to='auth.user')),
            ],
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('cart', models.ForeignKey(on_delete=models.CASCADE, to='store.cart')),
                ('product', models.ForeignKey(on_delete=models.CASCADE, to='store.product')),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('read', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=models.CASCADE, to='auth.user')),
            ],
        ),
        migrations.RunPython(create_initial_data),
    ]