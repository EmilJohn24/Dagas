# Generated by Django 3.2.10 on 2022-10-01 00:10

import datetime
from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_google_maps.fields
import relief.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('role', models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Resident'), (2, 'Donor'), (3, 'Barangay'), (4, 'Admin')], null=True)),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to=relief.models.user_profile_picture_path)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='BarangayProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='BarangayRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expected_date', models.DateTimeField(default=datetime.datetime.now, null=True)),
                ('barangay', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='relief.barangayprofile')),
            ],
        ),
        migrations.CreateModel(
            name='Disaster',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('ongoing', models.BooleanField(default=True)),
                ('date_started', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_ended', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Donation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime_added', models.DateTimeField(verbose_name='Date added')),
            ],
        ),
        migrations.CreateModel(
            name='DonorProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current_disaster', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='donors', to='relief.disaster')),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='donor_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='EvacuationCenter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('address', django_google_maps.fields.AddressField(max_length=200, null=True)),
                ('geolocation', django_google_maps.fields.GeoLocationField(max_length=100, null=True)),
                ('barangays', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='centers', to='relief.barangayprofile')),
            ],
        ),
        migrations.CreateModel(
            name='ItemType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='ResidentProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gov_id', models.ImageField(null=True, upload_to=relief.models.resident_id_path)),
                ('barangay', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='barangay', to='relief.barangayprofile')),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='resident_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Supply',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('quantity', models.IntegerField()),
                ('pax', models.IntegerField()),
                ('picture', models.ImageField(blank=True, null=True, upload_to=relief.models.supply_image_path)),
                ('datetime_added', models.DateTimeField(default=datetime.datetime.now, null=True, verbose_name='Date added')),
                ('donation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='supplies', to='relief.donation')),
                ('donor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='donor_supplies', to='relief.donorprofile')),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('qr_code', models.ImageField(blank=True, null=True, upload_to='transaction_QRs')),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('received', models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Packaging'), (2, 'Incoming'), (3, 'Received')], null=True)),
                ('received_date', models.DateTimeField(null=True)),
                ('barangay_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='relief.barangayrequest')),
                ('donor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='relief.donorprofile')),
            ],
        ),
        migrations.CreateModel(
            name='VictimRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('resident', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='resident_requests', to='relief.residentprofile')),
            ],
        ),
        migrations.CreateModel(
            name='UserLocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('geolocation', django_google_maps.fields.GeoLocationField(max_length=100, null=True)),
                ('time', models.DateTimeField(verbose_name='Date and time')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_location', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TransactionStub',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('qr_code', models.ImageField(blank=True, null=True, upload_to='resident_stub_QRs')),
                ('received', models.BooleanField(default=False)),
                ('created_on', models.DateTimeField(blank=True, default=datetime.datetime.now, null=True)),
                ('request', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='relief.barangayrequest')),
                ('resident', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='relief.residentprofile')),
            ],
        ),
        migrations.CreateModel(
            name='TransactionOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pax', models.IntegerField()),
                ('supply', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='relief.supply')),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='relief.transaction')),
            ],
        ),
        migrations.CreateModel(
            name='TransactionImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(null=True, upload_to=relief.models.transaction_img_path)),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transaction_image', to='relief.transaction')),
            ],
        ),
        migrations.AddField(
            model_name='supply',
            name='transaction',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transaction_supply', to='relief.transaction'),
        ),
        migrations.AddField(
            model_name='supply',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='supplies', to='relief.itemtype'),
        ),
        migrations.CreateModel(
            name='RouteSuggestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accepted', models.BooleanField(default=False)),
                ('expiration_time', models.DateTimeField(blank=True, editable=False, null=True)),
                ('donor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='route_donor', to='relief.donorprofile')),
            ],
        ),
        migrations.CreateModel(
            name='RouteNode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('distance_from_prev', models.FloatField(null=True)),
                ('request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='request', to='relief.barangayrequest')),
                ('suggestion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='nodes', to='relief.routesuggestion')),
            ],
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.IntegerField(default=5, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('barangay', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='relief.barangayprofile')),
                ('disaster', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='relief.disaster')),
                ('resident', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='relief.residentprofile')),
            ],
        ),
        migrations.CreateModel(
            name='ItemRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_added', models.DateTimeField()),
                ('pax', models.IntegerField()),
                ('barangay_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='item_request', to='relief.barangayrequest')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='relief.itemtype')),
                ('victim_request', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='relief.victimrequest')),
            ],
        ),
        migrations.CreateModel(
            name='GovAdminProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='gov_admin_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Fulfillment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pax', models.IntegerField()),
                ('node', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='relief.routenode')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='relief.itemtype')),
            ],
        ),
        migrations.CreateModel(
            name='EvacuationDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_evacuated', models.DateTimeField()),
                ('barangay', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='relief.barangayprofile')),
                ('evacuation_center', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='relief.evacuationcenter')),
            ],
        ),
        migrations.AddField(
            model_name='donation',
            name='donor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='donations', to='relief.donorprofile'),
        ),
        migrations.AddField(
            model_name='barangayrequest',
            name='details',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='relief.evacuationdetails'),
        ),
        migrations.AddField(
            model_name='barangayrequest',
            name='evacuation_center',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='relief.evacuationcenter'),
        ),
        migrations.AddField(
            model_name='barangayprofile',
            name='current_disaster',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='barangays', to='relief.disaster'),
        ),
        migrations.AddField(
            model_name='barangayprofile',
            name='user',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='barangay_profile', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='AlgorithmExecution',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_started', models.DateTimeField(auto_now_add=True)),
                ('time_modified', models.DateTimeField(auto_now=True)),
                ('donor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requesting_donor', to='relief.donorprofile')),
                ('result', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='suggestion', to='relief.routesuggestion')),
            ],
        ),
    ]
