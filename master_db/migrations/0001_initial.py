# Generated by Django 3.2.5 on 2021-07-14 18:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
import taggit.managers
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0001_initial'),
        ('taggit', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('uuid', models.UUIDField(blank=True, default=uuid.uuid4, editable=False)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('birth_date', models.DateField(blank=True, null=True)),
                ('mobile', models.CharField(max_length=15, unique=True)),
                ('male', models.BooleanField(blank=True, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='images/profile/%Y/%m/%d/')),
                ('date_joined', models.DateTimeField(auto_now_add=True, verbose_name='date joined')),
                ('date_updated', models.DateTimeField(auto_now=True, verbose_name='date updated')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
        ),
        migrations.CreateModel(
            name='Branch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('uuid', models.UUIDField(blank=True, default=uuid.uuid4, editable=False)),
                ('desc', models.TextField(blank=True, null=True)),
                ('addr', models.TextField()),
                ('short_adr', models.TextField()),
                ('phone', models.TextField()),
            ],
            options={
                'verbose_name': 'branch',
                'verbose_name_plural': 'branches',
            },
        ),
        migrations.CreateModel(
            name='ClassMetadata',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('uuid', models.UUIDField(blank=True, default=uuid.uuid4, editable=False)),
                ('desc', models.TextField(blank=True, null=True)),
                ('name', models.TextField()),
                ('status', models.TextField()),
            ],
            options={
                'verbose_name': 'class',
                'verbose_name_plural': 'classes',
            },
        ),
        migrations.CreateModel(
            name='Metatable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('uuid', models.UUIDField(blank=True, default=uuid.uuid4, editable=False)),
                ('desc', models.TextField(blank=True, null=True)),
                ('name', models.TextField(unique=True)),
            ],
            options={
                'verbose_name': 'table',
                'verbose_name_plural': 'tables',
            },
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('uuid', models.UUIDField(blank=True, default=uuid.uuid4, editable=False)),
                ('desc', models.TextField(blank=True, null=True)),
                ('time_start', models.IntegerField()),
                ('time_end', models.IntegerField()),
                ('classroom', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='master_db.classmetadata')),
            ],
            options={
                'verbose_name': 'schedule',
                'verbose_name_plural': 'schedules',
            },
        ),
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('uuid', models.UUIDField(blank=True, default=uuid.uuid4, editable=False)),
                ('desc', models.TextField(blank=True, null=True)),
                ('name', models.TextField()),
                ('value', models.TextField()),
            ],
            options={
                'verbose_name': 'setting',
                'verbose_name_plural': 'settings',
            },
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('uuid', models.UUIDField(blank=True, default=uuid.uuid4, editable=False)),
                ('desc', models.TextField(blank=True, null=True)),
                ('homework', models.SmallIntegerField(blank=True, null=True)),
                ('status', models.BooleanField(blank=True, null=True)),
                ('schedule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='master_db.schedule')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'session',
                'verbose_name_plural': 'sessions',
            },
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('uuid', models.UUIDField(blank=True, default=uuid.uuid4, editable=False)),
                ('desc', models.TextField(blank=True, null=True)),
                ('table', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='master_db.metatable')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('uuid', models.UUIDField(blank=True, default=uuid.uuid4, editable=False)),
                ('desc', models.TextField(blank=True, null=True)),
                ('name', models.TextField(unique=True)),
                ('duration', models.SmallIntegerField()),
                ('tags', taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags')),
            ],
            options={
                'verbose_name': 'course',
                'verbose_name_plural': 'courses',
            },
        ),
        migrations.CreateModel(
            name='ClassStudent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('uuid', models.UUIDField(blank=True, default=uuid.uuid4, editable=False)),
                ('desc', models.TextField(blank=True, null=True)),
                ('classroom', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='master_db.classmetadata')),
                ('student', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'class student',
                'verbose_name_plural': 'class students',
            },
        ),
        migrations.AddField(
            model_name='classmetadata',
            name='course',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='master_db.course'),
        ),
        migrations.AddField(
            model_name='classmetadata',
            name='teacher',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Calendar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('uuid', models.UUIDField(blank=True, default=uuid.uuid4, editable=False)),
                ('desc', models.TextField(blank=True, null=True)),
                ('name', models.TextField()),
                ('time_start', models.FloatField()),
                ('time_end', models.FloatField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddIndex(
            model_name='session',
            index=models.Index(fields=['student', 'status'], name='master_db_s_student_f72458_idx'),
        ),
        migrations.AddIndex(
            model_name='session',
            index=models.Index(fields=['schedule'], name='master_db_s_schedul_38b7a6_idx'),
        ),
        migrations.AddConstraint(
            model_name='session',
            constraint=models.UniqueConstraint(fields=('student', 'schedule'), name='unique_session'),
        ),
        migrations.AddIndex(
            model_name='schedule',
            index=models.Index(fields=['time_start', 'time_end'], name='master_db_s_time_st_3687ab_idx'),
        ),
        migrations.AddIndex(
            model_name='course',
            index=models.Index(fields=['duration'], name='master_db_c_duratio_7c3de7_idx'),
        ),
        migrations.AddIndex(
            model_name='classmetadata',
            index=models.Index(fields=['course'], name='master_db_c_course__cd1b38_idx'),
        ),
        migrations.AddIndex(
            model_name='classmetadata',
            index=models.Index(fields=['status'], name='master_db_c_status_0e5524_idx'),
        ),
        migrations.AddIndex(
            model_name='calendar',
            index=models.Index(fields=['time_start', 'time_end'], name='master_db_c_time_st_aa0106_idx'),
        ),
        migrations.AddIndex(
            model_name='customuser',
            index=models.Index(fields=['first_name'], name='master_db_c_first_n_87b10f_idx'),
        ),
        migrations.AddIndex(
            model_name='customuser',
            index=models.Index(fields=['male'], name='master_db_c_male_e11d83_idx'),
        ),
    ]
