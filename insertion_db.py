# insert_db.py

import os
import django
import json
from datetime import datetime

# 1️⃣ Ajouter le projet Django à sys.path pour être sûr que Python trouve l'app
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 2️⃣ Configurer Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stagefaso.settings")
django.setup()

# 3️⃣ Importer les modèles
try:
    from stages.models import Stage, Category  # stages = nom de ton app
except ModuleNotFoundError:
    print("Erreur : Python ne trouve pas l'application 'stages'. Vérifie le nom de l'app et la structure du projet.")
    raise


# Charger le fichier JSON depuis le dossier scrapping
json_path = os.path.join(os.path.dirname(__file__), "scrapping","sources", "stages_clean.json")
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# 5️⃣ Fonctions utiles
def get_or_create_category(name):
    if not name:
        name = "Informatique"
    category, created = Category.objects.get_or_create(name=name)
    if created:
        print(f"Nouvelle catégorie créée: {name}")
    return category

def stage_exists(title, company):
    return Stage.objects.filter(title=title, company=company).exists()

# 6️⃣ Insertion
for item in data:
    try:
        title = item.get("title", "").strip()
        company = item.get("company", "").strip()

        if not title or not company:
            continue

        if stage_exists(title, company):
            continue

        category_obj = get_or_create_category(item.get("category"))

        # Convertir la deadline
        deadline = item.get("deadline")
        if deadline:
            try:
                deadline = datetime.strptime(deadline, "%Y-%m-%d").date()
            except:
                deadline = None

        Stage.objects.create(
            title=title,
            description=item.get("description", ""),
            company=company,
            location=item.get("location", ""),
            contact_email=item.get("contact_email", ""),
            skills=item.get("skills", ""),
            deadline=deadline,
            link=item.get("link", ""),
            category=category_obj
        )

        print(f"Stage ajouté: {title}")

    except Exception as e:
        print(f"Erreur insertion: {e}")

print("Import terminé")