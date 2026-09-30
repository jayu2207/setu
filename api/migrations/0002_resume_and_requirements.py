from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(model_name='studentprofile', name='cgpa',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
        migrations.AddField(model_name='studentprofile', name='resume',
            field=models.FileField(blank=True, default='', upload_to='resumes/')),
        migrations.AddField(model_name='studentprofile', name='resume_name',
            field=models.CharField(blank=True, default='', max_length=255)),
        migrations.AddField(model_name='studentprofile', name='resume_text',
            field=models.TextField(blank=True, default='')),
        migrations.AddField(model_name='studentprofile', name='resume_uploaded_at',
            field=models.DateTimeField(blank=True, null=True)),
        migrations.AddField(model_name='opportunity', name='required_skills',
            field=models.TextField(blank=True, default='')),
        migrations.AddField(model_name='opportunity', name='required_branch',
            field=models.CharField(blank=True, default='', max_length=255)),
        migrations.AddField(model_name='opportunity', name='min_cgpa',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
    ]
