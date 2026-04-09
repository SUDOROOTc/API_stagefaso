from rest_framework import serializers
from .models import Stage, Category

# Serializer pour la catégorie
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']  # On ne renvoie que l'id et le nom


# Serializer pour le stage
class StageSerializer(serializers.ModelSerializer):
    # On inclut la catégorie mais en lecture seule pour éviter toute modification via le stage
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Stage
        fields = [
            'id',          # ID du stage
            'title',       # Titre du stage
            'description', # Description complète
            'company',     # Nom de l'entreprise
            'location',    # Localisation
            'contact_email', # Email de contact
            'skills',      # Compétences requises
            'deadline',    # Date limite
            'link',        # Lien de l'offre
            'category',    # Catégorie du stage
            'created_at'   # Date de création dans la base
        ]