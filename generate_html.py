import sqlite3
from pathlib import Path
from html import escape

DB = "emulation_news.db"
OUTPUT_DIR = Path("docs")
OUTPUT_FILE = OUTPUT_DIR / "index.html"

OUTPUT_DIR.mkdir(exist_ok=True)

conn = sqlite3.connect(DB)
c = conn.cursor()

c.execute("""
    SELECT title, summary, url, source, published_date
    FROM news
    ORDER BY published_date DESC
""")

rows = c.fetchall()
conn.close()

html = """
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>Actualités Émulation</title>
<style>
body { font-family: Arial, sans-serif; background:#111; color:#eee; max-width:1000px; margin:auto; }
h1 { text-align:center; }
.article { background:#1e1e1e; padding:15px; margin:15px 0; border-radius:8px; }
a { color:#4da6ff; text-decoration:none; }
.date { font-size:0.9em; color:#aaa; }
.source { font-size:0.9em; color:#888; }
</style>
</head>
<body>
<h1>🕹️ Actualités de l’Émulation</h1>
"""

for title, summary, url, source, date in rows:
    html += f"""
    <div class="article">
        <h2><a href="{escape(url)}" target="_blank">{escape(title)}</a></h2>
        <div class="date">{escape(date)}</div>
        <div class="source">{escape(source)}</div>
        <p>{escape(summary)}</p>
    </div>
    """

html += "</body></html>"

OUTPUT_FILE.write_text(html, encoding="utf-8")
print("✅ Page HTML générée :", OUTPUT_FILE)
