import feedparser
import requests
import sqlite3
from datetime import datetime
from bs4 import BeautifulSoup

# ------------------------------------------------------
# CONFIGURATION DES SOURCES
# ------------------------------------------------------

RSS_FEEDS = [
    "https://www.libretro.com/index.php/feed/",
    "https://www.mamedev.org/?feed=news",
    "https://www.emucr.com/feeds/posts/default",
]

GITHUB_REPOS = [
    "libretro/retroarch",
    "PCSX2/pcsx2",
    "rpcs3/rpcs3",
    "duckstation/duckstation",
    "citra-emu/citra",
]

SCRAPING_SOURCES = [
    "https://www.emufrance.com/news/",
]


# ------------------------------------------------------
# BASE DE DONNÉES
# ------------------------------------------------------

DB_NAME = "emulation_news.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            summary TEXT,
            url TEXT UNIQUE,
            source TEXT,
            published_date TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_news(title, summary, url, source, published_date):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    try:
        c.execute("""
            INSERT INTO news (title, summary, url, source, published_date)
            VALUES (?, ?, ?, ?, ?)
        """, (title, summary, url, source, published_date))
        conn.commit()
    except sqlite3.IntegrityError:
        # URL déjà enregistrée → on ignore
        pass  

    conn.close()


# ------------------------------------------------------
# 1. RÉCUPÉRATION VIA RSS
# ------------------------------------------------------

def fetch_rss():
    print("📡 Récupération RSS…")

    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries:
            title = entry.get("title", "Sans titre")
            summary = entry.get("summary", "")
            link = entry.get("link", "")
            date = entry.get("published", datetime.utcnow().isoformat())

            save_news(title, summary, link, feed_url, date)


# ------------------------------------------------------
# 2. RÉCUPÉRATION DES RELEASES GITHUB
# ------------------------------------------------------

def fetch_github():
    print("🐙 Récupération GitHub…")

    for repo in GITHUB_REPOS:
        url = f"https://api.github.com/repos/{repo}/releases"

        try:
            res = requests.get(url, timeout=10)
            releases = res.json()

            if isinstance(releases, dict) and "message" in releases:
                print(f"⚠️ API GitHub limitée pour {repo}")
                continue

            for rel in releases:
                title = f"{repo} - {rel['tag_name']}"
                summary = rel.get("body", "")[:300]
                link = rel["html_url"]
                date = rel.get("published_at", datetime.utcnow().isoformat())

                save_news(title, summary, link, repo, date)

        except Exception as e:
            print("Erreur GitHub :", e)


# ------------------------------------------------------
# 3. SCRAPING SIMPLE (EXEMPLE)
# ------------------------------------------------------

def fetch_scraping():
    print("🕷 Scraping… (simple)")

    for site in SCRAPING_SOURCES:
        try:
            res = requests.get(site, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")

            for article in soup.select(".news-item, article, .post"):
                title = article.find(["h2", "h3"])
                if not title:
                    continue

                title = title.get_text(strip=True)
                link = article.find("a")["href"] if article.find("a") else site
                summary = article.get_text(strip=True)[:300]

                save_news(title, summary, link, site, datetime.utcnow().isoformat())

        except Exception as e:
            print("Erreur scraping :", e)


# ------------------------------------------------------
# MAIN
# ------------------------------------------------------

if __name__ == "__main__":
    print("=== DÉBUT DE LA COLLECTE ===")

    init_db()
    fetch_rss()
    fetch_github()
    fetch_scraping()

    print("=== FIN DE LA COLLECTE ===")

