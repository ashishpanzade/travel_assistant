import argparse
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agent import config

USER_AGENT = "Mozilla/5.0 (compatible; TravelAssistantBot/1.0)"
MIN_USEFUL_CHARS = 500


def slugify(text: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text[:80] or "page"


def extract_main_text(html: str) -> tuple[str, str]:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "header", "footer", "aside", "noscript"]):
        tag.decompose()

    title_tag = soup.find("title")
    page_title = title_tag.get_text(strip=True) if title_tag else ""

    text = soup.get_text("\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n\n".join(lines), page_title


def fetch(url: str) -> str:
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=20)
    resp.raise_for_status()
    if resp.encoding is None or resp.encoding.lower() == "iso-8859-1":
        resp.encoding = resp.apparent_encoding
    return resp.text


def fetch_rendered(url: str) -> str:
    # headless-browser fallback for JS-rendered pages a plain fetch can't read
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            page = browser.new_page(user_agent=USER_AGENT)
            page.goto(url, timeout=30000, wait_until="networkidle")
            return page.content()
        finally:
            browser.close()


def save_markdown(url: str, title: str, body: str) -> Path:
    config.RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    domain = urlparse(url).netloc
    filename = f"crawled_{slugify(domain)}_{slugify(title)}.md"
    path = config.RAW_DATA_DIR / filename

    frontmatter = (
        "---\n"
        f'title: "{title}"\n'
        f'source_url: "{url}"\n'
        f'crawled_at: "{date.today().isoformat()}"\n'
        "---\n\n"
    )
    path.write_text(frontmatter + body, encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="Page to crawl and add to the knowledge base")
    args = parser.parse_args()

    print(f"Fetching {args.url} ...")
    html = fetch(args.url)
    body, page_title = extract_main_text(html)

    if len(body) < MIN_USEFUL_CHARS:
        print("Page looks JS-rendered, retrying with a headless browser ...", file=sys.stderr)
        html = fetch_rendered(args.url)
        body, page_title = extract_main_text(html)

    title = page_title or args.url
    path = save_markdown(args.url, title, body)
    print(f"Saved {len(body)} characters to {path}")
    print("Check the source site's reuse/redistribution terms before using this content.")
    print("Run 'python helpers/ingest.py' to embed it into the knowledge base.")


if __name__ == "__main__":
    main()
