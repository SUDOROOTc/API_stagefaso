import os
import django

# 1. Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stagefaso.settings')
django.setup()

# 2. Import du modèle
from stages.models import Category

# 3. Fonction principale
def run():
    categories = [
        "Informatique",
        "Marketing",
        "Finance",
        "Ressources Humaines",
        "Communication",
        "Design",
        "Logistique"
    ]

    for name in categories:
        obj, created = Category.objects.get_or_create(name=name)

        if created:
            print(f"✅ Ajouté : {name}")
        else:
            print(f"⚠️ Existe déjà : {name}")

# 4. Execution
if __name__ == "__main__":
    run()