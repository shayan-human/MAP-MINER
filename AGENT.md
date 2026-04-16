# Map Miner - Agent Context

## Project Overview

Map Miner is a Google Maps lead extraction tool that scrapes business data (name, phone, address, website) from Google Maps, then enriches each lead by scraping their website to find emails and social links. It provides a web dashboard (FastAPI) for managing scrape jobs and viewing results.

## File Structure

```
turbo/
├── app.py          # CLI entry point for headless scraping
├── search.py       # Google Maps scraper (Playwright)
├── enrich.py       # Email extraction from business websites
├── db.py           # SQLite database for lead storage/deduplication
├── server.py       # FastAPI web server & all API endpoints
├── static/         # Frontend (HTML/CSS/JS)
└── outputs/        # Generated CSV files & database (created at runtime)

run.py              # Alternative entry point (runs server.py)
docker-compose.yml  # Docker setup for easy deployment
Dockerfile          # Container definition
```

## How to Run

### Development (local)
```bash
cd turbo
pip install -r requirements.txt
python server.py
# Or: uvicorn server:app --reload
```
Server runs at `http://localhost:8000`

### Docker
```bash
docker-compose up --build
```

### CLI (headless)
```bash
python turbo/app.py --niche "restaurants" --location "Miami" --max-results 20
```

## Key Patterns

- **Async**: All I/O is async (`asyncio`, `async/await`, `asyncio.gather`)
- **Proxies**: Proxy string is comma-separated; parsed in `parse_proxies()` in search.py and server.py
- **Strict Mode**: If enabled, requires proxy; fails without one to protect user IP
- **Concurrency**: Uses `asyncio.Semaphore` to limit parallel enrichment tasks
- **Database**: SQLite at `turbo/outputs/leads.db` - tracks all leads with deduplication

## Common Tasks

| Task | File to Modify |
|------|----------------|
| Add new API endpoint | `server.py` |
| Change scraper logic | `search.py` |
| Add email extraction method | `enrich.py` |
| Modify database schema | `db.py` |
| Update frontend | `turbo/static/` |

## Questions?

If anything is unclear, ask before making assumptions.