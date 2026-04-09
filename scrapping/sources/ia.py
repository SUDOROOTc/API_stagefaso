# ia_pipeline.py

from scrapper1 import scrapper
from dotenv import load_dotenv
import os
import requests
import re
import json
from datetime import datetime

# Charger la clé API
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("Clé OpenRouter manquante ! Vérifie ton fichier .env")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Liste des catégories mémorisées
categories_list = [
    "Informatique",
    "Marketing",
    "Finance",
    "Ressources Humaines",
    "Communication",
    "Design",
    "Logistique"
]

# -----------------------------
# Fonctions utilitaires
# -----------------------------

def clean_text(text):
    """Nettoie le texte : supprime HTML, normalise espaces et retours ligne"""
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\n+", "\n", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def call_ia(description):
    if not description:
        return ""

    prompt = (
         "Tu es un assistant qui extrait les informations d'une offre de stage.\n\n"
    
    "Tu dois répondre STRICTEMENT avec ce format (une ligne par champ) :\n\n"
    "Title: ...\n"
    "Company: ...\n"
    "Location: ...\n"
    "Contact_email: ...\n"
    "Skills: ...\n"
    "Deadline: ...\n"
    "Link: ...\n"
    "Category: ...\n"
    "Description: ...\n\n"

    "Catégories autorisées (choisir UNE seule) :\n"
    "- Informatique\n"
    "- Marketing\n"
    "- Finance\n"
    "- Ressources Humaines\n"
    "- Communication\n"
    "- Design\n"
    "- Logistique\n\n"

    "Règles importantes :\n"
    "- Tu dois analyser le contenu du stage pour choisir la catégorie la plus pertinente\n"
    "- Tu dois choisir UNE SEULE catégorie dans la liste\n"
    "- Ne jamais inventer une nouvelle catégorie\n"
    "- Ne pas ajouter de texte avant ou après\n"
    "- Ne pas utiliser de markdown (** ou - ou *)\n"
    "- Si une information est absente, écrire: N/A\n\n"

    f"Texte : {description}"
    )

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistralai/mistral-small-3.2-24b-instruct",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500
    }

    try:
        response = requests.post(OPENROUTER_URL, json=data, headers=headers)
        response.raise_for_status()

        ia_text = response.json()["choices"][0]["message"]["content"]

   
        return ia_text

    except Exception as e:
        print(f"⚠️ Erreur OpenRouter : {e}")
        return ""


VALID_CATEGORIES = [
    "Informatique",
    "Marketing",
    "Finance",
    "Ressources Humaines",
    "Communication",
    "Design",
    "Logistique"
]

FIELD_MAP = {
    "title": "title",
    "company": "company",
    "location": "location",
    "email": "contact_email",
    "contact_email": "contact_email",
    "skills": "skills",
    "compétences": "skills",
    "deadline": "deadline",
    "link": "link",
    "category": "category",
    "description": "description"
}


def parse_ia_output(text):
    # Structure de base
    data = {field: "" for field in FIELD_MAP.values()}
    data["deadline"] = None

    # Nettoyage markdown
    text = re.sub(r"\*\*", "", text)

    lines = [line.strip() for line in text.splitlines() if line.strip()]

    for line in lines:
        parts = re.split(r":|-", line, maxsplit=1)
        if len(parts) != 2:
            continue

        key, value = parts[0].lower().strip(), parts[1].strip()

        if value == "N/A":
            value = ""

        # Trouver le champ correspondant
        for k in FIELD_MAP:
            if k in key:
                field = FIELD_MAP[k]

                if field == "deadline":
                    try:
                        data["deadline"] = datetime.strptime(value, "%Y-%m-%d").date()
                    except:
                        data["deadline"] = None

                elif field == "category":
                    if value in VALID_CATEGORIES:
                        data["category"] = value
                    else:
                        print(f"⚠️ Catégorie invalide: {value}")
                        data["category"] = "Informatique"

                else:
                    data[field] = value

                break  # important pour éviter conflits

    return data

# -----------------------------
# Traitement principal
# -----------------------------

def process_item(raw_item):
    description_raw = raw_item.get("description", "")

    ia_output = call_ia(description_raw)

  

    ia_data = parse_ia_output(ia_output)



    return {
        "title": ia_data.get("title", ""),
        "description": ia_data.get("description", ""),
        "company": ia_data.get("company", ""),
        "location": ia_data.get("location", ""),
        "contact_email": ia_data.get("contact_email", ""),
        "skills": ia_data.get("skills", ""),
        "deadline": ia_data.get("deadline", None),
        "link": ia_data.get("link", ""),
        "category": ia_data.get("category", "")
    }

def process_all(raw_list):
    processed_list = []
    for item in raw_list:
        try:
            processed_item = process_item(item)
            processed_list.append(processed_item)
        except Exception as e:
            print(f"⚠️ Erreur traitement item : {e}")
    return processed_list

# -----------------------------
# Exécution
# -----------------------------

if __name__ == "__main__":
    raw_data = scrapper()
    print(f"\n✅ {len(raw_data)} articles bruts récupérés\n")

    clean_data = process_all(raw_data)

    # Sauvegarde JSON
    with open("stages_clean.json", "w", encoding="utf-8") as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=4)

    print("✅ Les données nettoyées ont été sauvegardées dans stages_clean.json")