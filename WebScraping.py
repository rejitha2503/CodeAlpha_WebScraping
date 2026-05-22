import requests
from bs4 import BeautifulSoup
import time

BASE_URL = "https://books.toscrape.com/catalogue/"

RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}

def scrape_page(url):
    response = requests.get(url)
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")

    books = []
    articles = soup.select("article.product_pod")

    for article in articles:
        title = article.h3.a["title"]

        price = article.select_one("p.price_color").text.strip()
        price = price.encode("ascii", "ignore").decode().replace("£", "").strip()

        rating_word = article.p["class"][1]
        rating = RATING_MAP.get(rating_word, 0)

        availability = article.select_one("p.availability").text.strip()

        relative_url = article.h3.a["href"].replace("../", "")
        book_url = BASE_URL + relative_url

        books.append({
            "title": title,
            "price_gbp": price,
            "rating": rating,
            "availability": availability,
            "url": book_url
        })

    return books, soup


def get_next_page(soup):
    next_btn = soup.select_one("li.next a")
    if next_btn:
        href = next_btn["href"]
        # Fix: page-2.html direct use pannanum
        if "/" not in href:
            return BASE_URL + href
        return BASE_URL + href
    return None


def scrape_all_books(max_pages=None):
    all_books = []
    url = BASE_URL + "page-1.html"
    page_num = 1

    while url:
        print(f"Page {page_num} scraping... ({url})")
        books, soup = scrape_page(url)
        all_books.extend(books)
        print(f"  -> {len(books)} books found (Total: {len(all_books)})")

        if max_pages and page_num >= max_pages:
            break

        url = get_next_page(soup)
        page_num += 1
        time.sleep(0.3)

    return all_books


def save_to_csv(books, filename="books_data.csv"):
    import csv
    headers = ["Title", "Price (£)", "Rating (1-5)", "Availability", "URL"]

    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for book in books:
            writer.writerow({
                "Title": book["title"],
                "Price (£)": float(book["price_gbp"]) if book["price_gbp"] else 0,
                "Rating (1-5)": book["rating"],
                "Availability": book["availability"],
                "URL": book["url"]
            })

    print(f"\n✅ {len(books)} books saved to '{filename}'")


if __name__ == "__main__":
    print("=" * 50)
    print("  Books to Scrape - Web Scraper")
    print("=" * 50)

    # 1000 books all pages - max_pages=None
    books = scrape_all_books(max_pages=None)

    save_to_csv(books, "books_data.csv")

    print("\n📊 Summary:")
    print(f"   Total Books     : {len(books)}")
    prices = [float(b['price_gbp']) for b in books if b['price_gbp']]
    if prices:
        print(f"   Avg Price       : £{sum(prices)/len(prices):.2f}")
        print(f"   Cheapest        : £{min(prices):.2f}")
        print(f"   Most Expensive  : £{max(prices):.2f}")