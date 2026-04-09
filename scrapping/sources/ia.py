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
    """
    Appelle OpenRouter pour résumer et structurer la description.
    L'IA peut répondre librement mais doit rester structurée.
    """
    if not description:
        return ""

    prompt = (
        "Tu es un assistant qui prend une description d'offre de stage et qui doit :\n"
        "- Fournir toutes les informations importantes (titre, compagnie, lieu, email, compétences, deadline, lien, catégorie)\n"
        "- Répondre de façon structurée mais libre, par exemple avec des lignes du type 'Title: ...', 'Description: ...'\n"
        "- Ne pas inventer de données\n"
        f"Texte de l’offre : {description}"
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
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"⚠️ Erreur OpenRouter : {e}")
        return ""

def parse_ia_output(text):
    """
    Transforme la sortie libre de l'IA en dict structuré pour Stage.
    """
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

    lines = [line.strip() for line in text.splitlines() if line.strip()]

    for line in lines:
        if re.match(r"(?i)^title\s*[:\-]\s*(.+)", line):
            stage_data["title"] = re.match(r"(?i)^title\s*[:\-]\s*(.+)", line).group(1).strip()
        elif re.match(r"(?i)^description\s*[:\-]\s*(.+)", line):
            stage_data["description"] = re.match(r"(?i)^description\s*[:\-]\s*(.+)", line).group(1).strip()
        elif re.match(r"(?i)^company\s*[:\-]\s*(.+)", line):
            stage_data["company"] = re.match(r"(?i)^company\s*[:\-]\s*(.+)", line).group(1).strip()
        elif re.match(r"(?i)^location\s*[:\-]\s*(.+)", line):
            stage_data["location"] = re.match(r"(?i)^location\s*[:\-]\s*(.+)", line).group(1).strip()
        elif re.match(r"(?i)^contact_email\s*[:\-]\s*(.+)", line):
            stage_data["contact_email"] = re.match(r"(?i)^contact_email\s*[:\-]\s*(.+)", line).group(1).strip()
        elif re.match(r"(?i)^skills\s*[:\-]\s*(.+)", line):
            stage_data["skills"] = re.match(r"(?i)^skills\s*[:\-]\s*(.+)", line).group(1).strip()
        elif re.match(r"(?i)^deadline\s*[:\-]\s*(.+)", line):
            date_str = re.match(r"(?i)^deadline\s*[:\-]\s*(.+)", line).group(1).strip()
            try:
                stage_data["deadline"] = datetime.strptime(date_str, "%Y-%m-%d").date()
            except:
                stage_data["deadline"] = None
        elif re.match(r"(?i)^link\s*[:\-]\s*(.+)", line):
            stage_data["link"] = re.match(r"(?i)^link\s*[:\-]\s*(.+)", line).group(1).strip()
        elif re.match(r"(?i)^category\s*[:\-]\s*(.+)", line):
            stage_data["category"] = re.match(r"(?i)^category\s*[:\-]\s*(.+)", line).group(1).strip()

    return stage_data

# -----------------------------
# Traitement principal
# -----------------------------

def process_item(raw_item):
    """
    Transforme un dict brut en dict prêt pour Django Stage
    """
    description_raw = raw_item.get("description", "")
    ia_output = call_ia(description_raw)
    ia_data = parse_ia_output(ia_output)

    return {
        "title": ia_data.get("title", clean_text(raw_item.get("title", ""))),
        "description": ia_data.get("description", clean_text(description_raw)),
        "company": ia_data.get("company", clean_text(raw_item.get("company", ""))),
        "location": ia_data.get("location", clean_text(raw_item.get("address", ""))),
        "contact_email": ia_data.get("contact_email", clean_text(raw_item.get("email", ""))),
        "skills": ia_data.get("skills", clean_text(raw_item.get("skills", ""))),
        "deadline": ia_data.get("deadline", None),
        "link": ia_data.get("link", raw_item.get("link", "")),
        "category": ia_data.get("category", clean_text(raw_item.get("category", "")) or "Informatique")
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