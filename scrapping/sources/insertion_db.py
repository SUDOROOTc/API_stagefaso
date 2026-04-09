# insert_db.py

import os
import django
import json

# Initialiser Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stagefaso.settings')  # <-- ton projet
django.setup()

from stages.models import Category, Stage

# Charger les données nettoyées
with open("stages_clean.json", "r", encoding="utf-8") as f:
    stages_data = json.load(f)

# Ajouter les catégories si elles n’existent pas
categories_list = [
    "Informatique",
    "Marketing",
    "Finance",
    "Ressources Humaines",
    "Communication",
    "Design",
    "Logistique"
]

for name in categories_list:
    Category.objects.get_or_create(name=name)

# Insérer les stages en base
for data in stages_data:
    try:
        cat_obj, _ = Category.objects.get_or_create(name=data["category"])
        stage_obj, created = Stage.objects.get_or_create(
            title=data["title"],
            company=data["company"],
            defaults={
                "description": data["description"],
                "location": data["location"],
                "contact_email": data["contact_email"],
                "skills": data["skills"],
                "deadline": data["deadline"],
                "link": data["link"],
                "category": cat_obj
            }
        )
        if created:
            print(f"✅ Stage ajouté : {data['title']}")
        else:
            print(f"⚠️ Stage déjà existant : {data['title']}")
    except Exception as e:
        print(f"⚠️ Erreur insertion : {e}")

print("✅ Tous les stages ont été insérés ou mis à jour en base")