from django.apps import AppConfig
from django.db.models.signals import post_migrate


def seed_admin(sender, **kwargs):
    """Equivalent of the admin-seeding block at the bottom of db.js —
    runs after migrations and creates the default admin if one doesn't exist yet."""
    from django.conf import settings
    from django.contrib.auth.hashers import make_password
    from .models import User

    if not User.objects.filter(email=settings.ADMIN_EMAIL).exists():
        User.objects.create(
            name='Platform Admin',
            email=settings.ADMIN_EMAIL,
            password=make_password(settings.ADMIN_PASSWORD),
            role='admin',
            status='active',
        )
        print(f"\u2714 Default admin created -> email: {settings.ADMIN_EMAIL}  password: {settings.ADMIN_PASSWORD}")


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        post_migrate.connect(seed_admin, sender=self)
