import os
import json
import uuid
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
app.secret_key = "dev-secret-key"  
DATA_FILE = os.path.join("data", "articles.json")
def load_articles():
    """Read all saved articles from our JSON 'database' file."""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
def save_articles(articles):
    """Write the full articles list back to disk."""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)
def scrape_article(url):
    """
    Download a web page and pull out the headline, main image, and
    body paragraphs, while stripping out nav bars, scripts, ads, etc.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"
        )
    }
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        title = og_title["content"]
    elif soup.title:
        title = soup.title.get_text(strip=True)
    else:
        title = "Untitled Article"
    image = None
    og_image = soup.find("meta", property="og:image")
    if og_image and og_image.get("content"):
        image = og_image["content"]
    for tag in soup(["script", "style", "nav", "header", "footer", "form", "aside", "noscript"]):
        tag.decompose()
    paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
    paragraphs = [p for p in paragraphs if len(p.split()) > 5]
    body_text = "\n\n".join(paragraphs)
    return {
        "title": title.strip(),
        "image": image,
        "text": body_text,
        "url": url,
    }
@app.route("/")
def dashboard():
    articles = load_articles()
    articles.sort(key=lambda a: a["date_added"], reverse=True)
    return render_template("index.html", articles=articles)
@app.route("/add", methods=["POST"])
def add_article():
    url = request.form.get("url", "").strip()
    if not url:
        flash("Please paste a URL first.")
        return redirect(url_for("dashboard"))
    try:
        scraped = scrape_article(url)
    except requests.exceptions.RequestException:
        flash("Couldn't load that page. Check the URL and try again.")
        return redirect(url_for("dashboard"))
    if not scraped["text"]:
        flash("Couldn't find readable article text on that page.")
        return redirect(url_for("dashboard"))
    article = {
        "id": uuid.uuid4().hex[:8],
        "title": scraped["title"],
        "image": scraped["image"],
        "text": scraped["text"],
        "url": scraped["url"],
        "date_added": datetime.now().isoformat(),
    }
    articles = load_articles()
    articles.append(article)
    save_articles(articles)
    return redirect(url_for("read_article", article_id=article["id"]))
@app.route("/read/<article_id>")
def read_article(article_id):
    articles = load_articles()
    article = next((a for a in articles if a["id"] == article_id), None)
    if article is None:
        flash("Article not found.")
        return redirect(url_for("dashboard"))
    return render_template("reader.html", article=article)
if __name__ == "__main__":
    app.run(debug=True)