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
        "Règles importantes :\n"
        "- Ne pas ajouter de texte avant ou après\n"
        "- Ne pas utiliser de markdown (** ou - ou *)\n"
        "- Si une information est absente, écrire: N/A\n"
        "- Ne pas inventer d'informations\n\n"
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

        # 🔥 DEBUG ICI
        print("\n================ IA RAW OUTPUT ================\n")
        print(ia_text)
        print("\n==============================================\n")

        return ia_text

    except Exception as e:
        print(f"⚠️ Erreur OpenRouter : {e}")
        return ""
def parse_ia_output(text):
    stage_data = {
        "title": "",
        "description": "",
        "company": "",
        "location": "",
        "contact_email": "",
        "skills": "",
        "deadline": None,
        "link": "",
        "category": ""
    }

    # Nettoyer markdown (** etc)
    text = re.sub(r"\*\*", "", text)

    lines = [line.strip() for line in text.splitlines() if line.strip()]

    for line in lines:
        key_value = re.split(r":|-", line, maxsplit=1)
        if len(key_value) != 2:
            continue

        key = key_value[0].strip().lower()
        value = key_value[1].strip()

        if value == "N/A":
            value = ""

        if "title" in key:
            stage_data["title"] = value
        elif "company" in key:
            stage_data["company"] = value
        elif "location" in key:
            stage_data["location"] = value
        elif "email" in key:
            stage_data["contact_email"] = value
        elif "skills" in key or "compétences" in key:
            stage_data["skills"] = value
        elif "deadline" in key:
            try:
                stage_data["deadline"] = datetime.strptime(value, "%Y-%m-%d").date()
            except:
                stage_data["deadline"] = None
        elif "link" in key:
            stage_data["link"] = value
        elif "category" in key:
            stage_data["category"] = value
        elif "description" in key:
            stage_data["description"] = value

    return stage_data

# -----------------------------
# Traitement principal
# -----------------------------

def process_item(raw_item):
    description_raw = raw_item.get("description", "")

    ia_output = call_ia(description_raw)

    # 🔥 DEBUG
    print(">>> TEXTE IA AVANT PARSE:", ia_output)

    ia_data = parse_ia_output(ia_output)

    # 🔥 DEBUG
    print(">>> RESULTAT PARSE:", ia_data)

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