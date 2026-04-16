# Map Miner - Codebase Reference

Detailed documentation for agents working on this codebase.

---

## Core Files

### `turbo/server.py` - Web Server & API
**Purpose**: FastAPI application serving the web dashboard and all REST API endpoints.

**Key Functions**:
- `parse_proxies(proxy_string)` - Parses comma-separated proxy string into list
- `check_and_update()` - Auto-updates from git on startup (currently disabled)
- `load_history()` / `save_history()` - Manages job history JSON

**API Endpoints**:
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serve frontend |
| `/api/scrape` | POST | Start a new scrape job |
| `/api/jobs/{job_id}` | GET | Get job status |
| `/api/download/{filename}` | GET | Download CSV file |
| `/api/history` | GET | List all past jobs |
| `/api/history/{job_id}` | DELETE | Delete a history item |
| `/api/datasets` | GET | List all CSV files in outputs |
| `/api/datasets/{filename}` | DELETE | Delete a CSV file |
| `/api/proxies` | GET/POST | Save/retrieve proxies |
| `/api/test-proxy` | POST | Test if a proxy works |
| `/api/enrich-csv` | POST | Enrich uploaded CSV with emails |
| `/api/refine` | POST | Filter CSV against database |

**Key Classes/Objects**:
- `LeadDB` - Imported from `turbo.db`
- `jobs` - Dict mapping job_id to job status
- `OUTPUT_DIR` - `./outputs/`

---

### `turbo/search.py` - Google Maps Scraper
**Purpose**: Scrapes Google Maps for business data using Playwright.

**Key Functions**:
- `parse_proxies(proxy_string)` - Proxy parsing
- `handle_consent(page)` - Handles Google consent dialogs
- `extract_details(context, lead, idx, total, results_list, lock)` - Worker to extract single business details in new tab
- `get_random_ua()` - Returns random User-Agent
- `ProxyManager` class - Rotates through proxy list
- `scrape_gmaps(query, depth, max_results, proxy_string, is_subsearch, strict_mode)` - Main scraping function

**Key Constants**:
- `USER_AGENTS` - List of browser User-Agent strings

**Returns**: Tuple of `(list of business dicts, failure_screenshot_path or None)`

---

### `turbo/enrich.py` - Email Extraction
**Purpose**: Scrapes business websites to find contact emails and social links.

**Key Functions**:
- `_deobfuscate_text(text)` - Replaces [at], {dot} patterns with @ and .
- `extract_emails_from_text(text)` - Regex-based email extraction
- `extract_mailto_emails(html)` - Extracts from `mailto:` links
- `extract_emails_from_attributes(html)` - Extracts from HTML attributes
- `get_page_content(client, url)` - Fetches page content
- `find_contact_links(html, base_url)` - Finds contact/about pages
- `enrich_business(business_data, proxies, limit, strict_mode)` - Main enrichment function

**Returns**: Updated business dict with `emails` and `socials` fields.

---

### `turbo/db.py` - SQLite Database
**Purpose**: Stores leads and handles deduplication.

**Key Classes**:
- `LeadDB(db_path)` - Database wrapper

**Key Methods**:
- `is_duplicate(name, phone, address, email)` - Checks if lead already exists
- `add_leads(leads)` - Inserts new leads, updates existing on conflict
- `get_stats()` - Returns total lead count

**Schema**:
```sql
leads (
    id, name, phone, normalized_phone, website, address, 
    zip_code, ip_address, emails, normalized_email, socials, created_at
)
```

---

### `turbo/app.py` - CLI Entry Point
**Purpose**: Headless command-line interface for scraping.

**Usage**:
```bash
python turbo/app.py --niche "restaurants" --location "Miami" --max-results 20
```

**Arguments**:
- `--niche` (required) - Business type to search
- `--location` (required) - Target location
- `--depth` - Scroll depth (default: 2)
- `--max-results` - Max results (default: 20)
- `--concurrency` - Parallel enrichment count (default: 5)
- `--output` - Output CSV filename (default: leads.csv)

---

## Frontend Files

### `turbo/static/`
- `index.html` - Main dashboard UI
- `app.js` - Frontend JavaScript (API calls, job polling)
- `style.css` - Glassmorphic dark theme styles
- `sw.js` - Service worker for PWA support

---

## Data Flow

1. **Scrape**: `server.py` → `search.py` → Returns list of businesses
2. **Enrich**: `server.py` → `enrich.py` → Scrapes websites for emails (parallel)
3. **Store**: `server.py` → `db.py` → Saves to SQLite
4. **Serve**: `server.py` → Returns CSV/JSON to frontend

---

## Common Patterns

- **Async/Await**: All I/O is async, use `asyncio.gather` for parallelism
- **Semaphore**: Limit concurrency with `asyncio.Semaphore(n)`
- **Locks**: Use `asyncio.Lock()` when appending to shared lists
- **Proxies**: Passed as strings, parsed at multiple levels
- **Error Handling**: Try/except with fallbacks (e.g., proxy failure → local IP)

---

## Configuration

- Port: `8000` (change in `docker-compose.yml` or `server.py`)
- Output directory: `turbo/outputs/`
- Database: `turbo/outputs/leads.db`
- History: `turbo/outputs/history.json`