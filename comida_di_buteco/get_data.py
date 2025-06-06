import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd

BASE_URL = "https://comidadibuteco.com.br/butecos/belo-horizonte/"
SITE_ROOT = "https://comidadibuteco.com.br"

def fetch_page(page_num: int) -> str:
    url = BASE_URL if page_num == 1 else f"{BASE_URL}page/{page_num}/"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.text

def parse_restaurants(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    scraped = []
    for item in soup.find_all("div", class_="item"):
        name = item.find("h2").get_text(strip=True)
        address = item.find("p").get_text(strip=True)

        details_link = item.find("a", string="Detalhes")
        details_url = urljoin(SITE_ROOT, details_link["href"]) if details_link else None
        img = item.find("img")
        image_url = urljoin(SITE_ROOT, img["src"]) if img and img.get("src") else None

        scraped.append({
            "name": name,
            "address": address,
            "details_url": details_url,
            "image_url": image_url,
        })
    return scraped

def main():
    scraped = []
    for page in range(1, 12):
        print(f"Scraping page {page}…")
        html = fetch_page(page)
        scraped.extend(parse_restaurants(html))

    df = pd.DataFrame(scraped, columns=["name", "address", "details_url", "image_url"])

    out_path = "data/butecos.csv"
    df.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"Saved {len(df)} records (with image URLs) to {out_path}")

if __name__ == "__main__":
    main()

