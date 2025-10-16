from django.db import models
from django.contrib.auth.models import User

# Cada usuario tendrá un perfil con datos adicionales
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # relación 1 a 1
    bio = models.TextField(blank=True)  # breve descripción
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"
