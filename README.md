# Singapore Travel Assistant

A chat app for planning a Singapore trip. It answers destination questions from pages I crawled (RAG), and calls MCP tools for live weather and currency conversion. Built with LangChain, Gemini, ChromaDB and Gradio.

## Setup

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

To rebuild the index anyway, run the command below. It takes about 6 minutes and replaces the existing index. Don't change `GEMINI_EMBEDDING_MODEL`, the saved index was built with it.

```powershell
python helpers\ingest.py
```

## How the RAG part works

1. Ten crawled pages are saved as markdown in `data\raw\`, each with its title and URL.
2. `ingest.py` splits them into ~1000 character chunks and embeds them with Gemini.
3. The embeddings are stored in ChromaDB (`vectorstore\`).
4. For a destination question, the agent pulls the 5 closest chunks, each tagged with its page title and URL.
5. It answers from those chunks and lists the sources.

If nothing relevant turns up, it says the guide doesn't cover it.

## MCP tools

Two small MCP servers in `mcp_servers\`, started automatically by the app. Neither needs an API key.

- Weather (Open-Meteo): `get_current_weather`, `get_weather_forecast`
- Currency (Frankfurter): `convert_currency`

The agent picks the tool that fits the question. If a tool fails, it says the live data isn't available instead of guessing.

## Prompt and context strategy

The prompt is in `agent\prompts.py`. It tells the model to:

- Take destination facts from the guide only, and weather and rates from the tools only. No guessing.
- Label its answers ("From the guide", "Live weather (MCP)", "My suggestion") so fact and advice stay separate.
- List sources whenever it used the guide.
- For weather-dependent plans, check the guide and the forecast, then plan day by day with indoor options for rainy days.

There's no separate memory. Gradio sends the whole chat on every turn and the app passes it all to the agent, so a follow-up like "now show that budget in SGD" just works. The catch is that very long chats get slower.

## Sources

Ten pages, saved as markdown in `data\raw\` with their title and URL at the top:

- Wikivoyage: [Singapore](https://en.wikivoyage.org/wiki/Singapore), [Sentosa](https://en.wikivoyage.org/wiki/Singapore/Sentosa), [Orchard](https://en.wikivoyage.org/wiki/Singapore/Orchard), [Chinatown](https://en.wikivoyage.org/wiki/Singapore/Chinatown), [Little India](https://en.wikivoyage.org/wiki/Singapore/Little_India), [Marina Bay](https://en.wikivoyage.org/wiki/Singapore/Marina_Bay), [Bugis](https://en.wikivoyage.org/wiki/Singapore/Bugis)
- Visit Singapore: [Essential info](https://www.visitsingapore.com/travel-guide-tips/essential-info/), [Itineraries](https://www.visitsingapore.com/travel-tips/travelling-to-singapore/itineraries/), [Things to do](https://www.visitsingapore.com/things-to-do/top-things-to-do/)

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
