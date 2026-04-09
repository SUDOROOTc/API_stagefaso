import requests
from bs4 import BeautifulSoup
import re


# definition du header
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Connection": "keep-alive"
}

# Extraire email avec regex
def extract_email(text):
    match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    return match.group(0) if match else None

# Extraire compagnie
def extract_company(text):
    keywords = ["Entreprise", "Société", "Company"]
    for line in text.split("\n"):
        for word in keywords:
            if word.lower() in line.lower():
                return line.strip()
    return None

# Extraire adresse
def extract_address(text):
    cities = ["Ouagadougou", "Bobo", "Burkina Faso"]
    for city in cities:
        if city.lower() in text.lower():
            return city
    return None


BASE_URL = "https://digitalmagazine.bf"

def get_article_links(search_term="stage"):
    url = f"https://digitalmagazine.bf/?s={search_term}"

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Erreur {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "lxml")
    links = []

    articles = soup.find_all("article")

    for article in articles:
        a_tag = article.find("a")
        if a_tag and a_tag.get("href"):
            links.append(a_tag["href"])

    return links


def scrape_article(url):
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Erreur {response.status_code} sur {url}")
        return None

    soup = BeautifulSoup(response.text, "lxml")

    h1_tag = soup.find("h1")
    title = h1_tag.get_text(strip=True) if h1_tag else "Titre manquant"

    content_div = soup.find("div", class_="entry-content")
    description = content_div.get_text(separator="\n", strip=True) if content_div else ""

    email = extract_email(description)
    company = extract_company(description)
    address = extract_address(description)

    return {
        "title": title,
        "description": description,
        "link": url,
        "company": company,
        "email": email,
        "address": address,
        "category": "stage"
    }


def scrapper():
    results = []
    links = get_article_links()

    print(f"{len(links)} articles trouvés")

    for link in links:
        try:
            data = scrape_article(link)
            if data:
                results.append(data)
        except Exception as e:
            print(f"Erreur sur {link}: {e}")

    return results


if __name__ == "__main__":
    data = scrapper()
    
    for item in data:
        print(item)
        print("-" * 50)