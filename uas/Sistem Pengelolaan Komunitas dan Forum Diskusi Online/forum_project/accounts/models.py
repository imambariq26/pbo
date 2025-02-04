# accounts/models.py
from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    # Tambahkan field lain seperti badge, tanggal bergabung, dsb.

    def __str__(self):
        return f'Profil {self.user.username}'
