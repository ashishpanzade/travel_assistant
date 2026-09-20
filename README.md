# Singapore Travel Assistant

A chat app for planning a Singapore trip. It answers destination questions from pages I crawled (RAG), and calls MCP tools for live weather and currency conversion. Built with LangChain, Gemini, ChromaDB and Gradio.

## Run it

You need Python 3.10+ and a free Gemini API key from https://aistudio.google.com/apikey.

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and put your key in `GOOGLE_API_KEY`. Then start the app:

```powershell
python app.py
```

It prints a local link, open it in your browser.

## No crawling or ingesting needed

The crawled pages (`data\raw\`) and the ready-made ChromaDB index (`vectorstore\`) are already in this repo, so the app works straight after the steps above. You can skip the crawler and `ingest.py` completely.

If you do want to rebuild the index yourself, run the command below. It takes about 6 minutes (the free tier limits embeddings per minute, so it pauses between batches), and it replaces the existing index. Keep `GEMINI_EMBEDDING_MODEL` as it is in `.env.example`, since the saved index was built with it.

```powershell
python helpers\ingest.py
```

## Sources

Ten pages, saved as markdown in `data\raw\` with their title and URL at the top:

- Wikivoyage: [Singapore](https://en.wikivoyage.org/wiki/Singapore), [Sentosa](https://en.wikivoyage.org/wiki/Singapore/Sentosa), [Orchard](https://en.wikivoyage.org/wiki/Singapore/Orchard), [Chinatown](https://en.wikivoyage.org/wiki/Singapore/Chinatown), [Little India](https://en.wikivoyage.org/wiki/Singapore/Little_India), [Marina Bay](https://en.wikivoyage.org/wiki/Singapore/Marina_Bay), [Bugis](https://en.wikivoyage.org/wiki/Singapore/Bugis)
- Visit Singapore: [Essential info](https://www.visitsingapore.com/travel-guide-tips/essential-info/), [Itineraries](https://www.visitsingapore.com/travel-tips/travelling-to-singapore/itineraries/), [Things to do](https://www.visitsingapore.com/things-to-do/top-things-to-do/)

## MCP tools

- Weather (Open-Meteo): `get_current_weather`, `get_weather_forecast`
- Currency (Frankfurter): `convert_currency`

Neither needs an API key.

## Adding a page

Crawl it:

```powershell
python helpers\crawler.py "https://example.com/page"
```

Then rebuild the index:

```powershell
python helpers\ingest.py
```

If a page needs JavaScript to load, the crawler retries with a headless browser. Install it once with:

```powershell
python -m playwright install chromium
```
