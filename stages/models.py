# stages/models.py
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    

# stages/models.py
from django.db import models




class Stage(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True, null=True)
    contact_email = models.EmailField()
    skills = models.TextField(blank=True)  # compétences requises
    deadline = models.DateField(blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    category = models.ForeignKey(
        'Category',
        on_delete=models.CASCADE,
        related_name='stages'
    )

    def __str__(self):
        return f"{self.title} - {self.company}"




