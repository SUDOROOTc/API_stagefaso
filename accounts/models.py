# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    User personnalisé (hérite de AbstractUser)
    Pour l’instant pas de champ supplémentaire.
    """
    pass

# stages/models.py
from django.db import models

