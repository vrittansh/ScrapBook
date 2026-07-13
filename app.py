from flask import Flask, render_template, request, redirect, url_for
try:
    import requests
except Exception as e:
    raise ImportError("The 'requests' package is required. Install with: pip install requests") from e
try:
    from bs4 import BeautifulSoup
except Exception as e:
    raise ImportError("The 'beautifulsoup4' package is required. Install with: pip install beautifulsoup4") from e
import json
import os
import uuid
from datetime import datetime
app = Flask(__name__)
if os.environ.get("VERCEL"):
    DATA_FILE = "/tmp/articles.json"
else:
    DATA_FILE = os.path.join(os.path.dirname(__file__), "articles.json")
def load_articles():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
def save_articles(articles):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)
def scrape_article(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "nav", "header", "footer", "aside", "form", "iframe", "noscript"]):
        tag.decompose()
    if soup.find("h1"):
        title = soup.find("h1").get_text(strip=True)
    elif soup.title:
        title = soup.title.get_text(strip=True)
    else:
        title = "Untitled Article"
    image = None
    og_image = soup.find("meta", property="og:image")
    if og_image and og_image.get("content"):
        image = og_image["content"]
    container = soup.find("article") or soup.find("body")
    paragraphs = []
    if container:
        for p in container.find_all("p"):
            text = p.get_text(strip=True)
            if len(text) > 40:
                paragraphs.append(text)
    body_text = "\n\n".join(paragraphs)
    return {
        "title": title,
        "url": url,
        "image": image,
        "text": body_text,
        "date_saved": datetime.now().strftime("%Y-%m-%d || %H:%M")
    }
@app.route("/")
def dashboard():
    articles = load_articles()
    sorted_articles = sorted(articles.items(), key=lambda x: x[1]["date_saved"], reverse=True)
    return render_template("index.html", articles=sorted_articles)
@app.route("/save", methods=["POST"])
def save():
    url = request.form.get("url", "").strip()
    if not url:
        return redirect(url_for("dashboard"))
    try:
        article_data = scrape_article(url)
    except Exception as e:
        return f"Something went wrong while scraping that URL: {e}", 400
    articles = load_articles()
    article_id = str(uuid.uuid4())[:8]
    articles[article_id] = article_data
    save_articles(articles)
    return redirect(url_for("dashboard"))
@app.route("/read/<article_id>")
def read(article_id):
    articles = load_articles()
    article = articles.get(article_id)
    if not article:
        return "Article not found", 404
    return render_template("reader.html", article=article)
if __name__ == "__main__":
    app.run(debug=True)