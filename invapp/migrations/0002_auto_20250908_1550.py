from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invapp', '0001_initial'),  # 👈 yaha aapke last migration ka naam hoga
    ]

    operations = [
        migrations.CreateModel(
            name='HeadCompany',
            fields=[
                ('company', models.CharField(max_length=100, primary_key=True, serialize=False)),
            ],
        ),
    ]
