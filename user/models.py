from django.contrib.auth.models import AbstractUser
from django.db import models
from core.fields import LowercaseEmailField


class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser
    to include additional profile information
    """
    email = LowercaseEmailField(unique=True, primary_key=True)
    # Profile fields
    bio = models.TextField(max_length=500, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        null=True,
        blank=True
    )

    # Address fields
    address_line1 = models.CharField(max_length=100, blank=True)
    address_line2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)

    # Preferences
    email_notifications = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username
