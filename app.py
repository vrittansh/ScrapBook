import os
import json
import uuid
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "dev-secret-key-change-this-later"  # required for flash messages

DATA_FILE = os.path.join("data", "articles.json")



def load_articles():
    """Read all saved articles from disk. Returns an empty list if none yet."""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_articles(articles):
    """Write the full articles list back to disk as JSON."""
    os.makedirs("data", exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)


# ----------------------------------------------------------------------------
# SCRAPING
# This is the core of the app: fetch a page, strip out the junk, and pull
# out just the headline, main image, and body paragraphs.
# ----------------------------------------------------------------------------

def scrape_article(url):
    """
    Downloads the page at `url` and extracts title, image, and body text.
    Returns a dict ready to be saved. Raises ValueError / requests errors
    on failure so the route can show a friendly message.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
        )
    }
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()  # raises an exception on 404 / 500 / etc.

    soup = BeautifulSoup(response.text, "lxml")

  for tag in soup(["script", "style", "nav", "header", "footer", "aside", "form", "iframe", "noscript"]):
        tag.decompose()
  title = None
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        title = og_title["content"].strip()
    elif soup.find("h1"):
        title = soup.find("h1").get_text(strip=True)
    elif soup.title:
        title = soup.title.get_text(strip=True)
    else:
        title = "Untitled Article"

  image_url = None
    og_image = soup.find("meta", property="og:image")
    if og_image and og_image.get("content"):
        image_url = og_image["content"].strip()

 article_tag = soup.find("article")
    paragraphs_source = article_tag if article_tag else soup

    raw_paragraphs = paragraphs_source.find_all("p")

body_paragraphs = [
        p.get_text(strip=True) for p in raw_paragraphs if len(p.get_text(strip=True)) > 40
    ]

    if not body_paragraphs:
        raise ValueError("Couldn't find readable article text on that page.")

    return {
        "id": uuid.uuid4().hex[:10],
        "url": url,
        "title": title,
        "image": image_url,
        "paragraphs": body_paragraphs,
        "saved_at": datetime.now().strftime("%b %d, %Y - %I:%M %p"),
    }

@app.route("/")
def dashboard():
    """The main page: URL submission form + grid of saved articles."""
    articles = load_articles()
    articles.reverse() 
    return render_template("index.html", articles=articles)


@app.route("/save", methods=["POST"])
def save():
    """Handles the form submission from the dashboard."""
    url = request.form.get("url", "").strip()

    if not url.startswith(("http://", "https://")):
        flash("Please enter a valid URL starting with http:// or https://")
        return redirect(url_for("dashboard"))

    try:
        article = scrape_article(url)
    except requests.exceptions.RequestException:
        flash("Couldn't reach that URL. Double check it and try again.")
        return redirect(url_for("dashboard"))
    except ValueError as e:
        flash(str(e))
        return redirect(url_for("dashboard"))

    articles = load_articles()
    articles.append(article)
    save_articles(articles)

    # Take the user straight to the clean reading view of what they just saved
    return redirect(url_for("read_article", article_id=article["id"]))


@app.route("/read/<article_id>")
def read_article(article_id):
    """The distraction-free reader page for one saved article."""
    articles = load_articles()
    article = next((a for a in articles if a["id"] == article_id), None)

    if article is None:
        flash("Article not found.")
        return redirect(url_for("dashboard"))

    return render_template("reader.html", article=article)


@app.route("/delete/<article_id>", methods=["POST"])
def delete_article(article_id):
    """Removes a saved article from the JSON file."""
    articles = load_articles()
    articles = [a for a in articles if a["id"] != article_id]
    save_articles(articles)
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(debug=True)