# ScrapBook — Read Later Dashboard


> No ads. No pop-ups. Just a quiet corner of the web to read your articles.

ScrapBook is a minimalist "read later" web app. Paste in the URL of any article or blog post, and it scrapes the headline, main image, and body text — stripping out ads, navbars, and clutter — then saves it into a clean, Kindle-style distraction-free reading view.

**🔗 Live demo:** [scrap-book-zeta.vercel.app](https://scrap-book-zeta.vercel.app)

---

## Features

- Paste any article URL and save it with one click
- Automatically extracts the title, main image, and body text
- Strips out scripts, navbars, footers, ads, and other page clutter
- Kindle-style distraction-free reading view
- Light / dark mode toggle (remembers your preference)
- Built with plain HTML, vanilla CSS, and vanilla JS — no frontend frameworks

## Tech Stack

| Layer      | Tech                                |
|------------|--------------------------------------|
| Backend    | Python, Flask                       |
| Scraping   | BeautifulSoup4, Requests            |
| Frontend   | HTML, vanilla CSS, vanilla JavaScript |
| Hosting    | Vercel                              |

## Project Structure

```
ScrapBook/
├── app.py
├── requirements.txt
├── static/
│   ├── style.css
│   └── script.js
└── templates/
    ├── index.html
    └── reader.html
```

## Getting Started Locally

### 1. Clone the repo

```bash
git clone https://github.com/<your-username>/ScrapBook.git
cd ScrapBook
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the project root:

```
UPSTASH_REDIS_REST_URL=your-upstash-url
UPSTASH_REDIS_REST_TOKEN=your-upstash-token
```

Get these values from your [Upstash](https://upstash.com) console, or from the **Storage** tab of your project on Vercel if you've linked a database there.

### 5. Run the app

```bash
python app.py
```

Visit **http://127.0.0.1:5000** in your browser.

## Deployment

This project is deployed on [Vercel](https://vercel.com), using Upstash Redis for persistent storage (Vercel's own filesystem is read-only/ephemeral, so article data can't be saved to a local file in production).

To deploy your own copy:

1. Push this repo to your own GitHub account
2. Import it into Vercel ([New Project → Import Git Repository](https://vercel.com/new))
3. Add an Upstash Redis database via the project's **Storage** tab
4. Deploy

## Known Limitations

- Sites that render content with heavy JavaScript (many single-page apps) may not scrape well, since the backend only fetches static HTML
- Some sites block non-browser traffic outright
- Article extraction uses simple heuristics, so it can occasionally miss a short paragraph or grab a stray caption/ad line

## Roadmap

- [ ] Delete / archive saved articles
- [ ] Tags and search
- [ ] Smarter content-extraction algorithm
- [ ] Reading progress tracking

## License

MIT — feel free to fork and build on this.