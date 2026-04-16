# 🗺️ Map Miner - Lead Extraction from Google Maps

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-%E2%9C%94-blue.svg)](https://www.docker.com/)

**Map Miner** is a high-accuracy business lead generation tool. It automated the process of extracting data from Google Maps and enriches those leads with contact emails and social links harvested directly from business websites.

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)
The easiest way to run Map Miner with zero configuration.
```bash
git clone https://github.com/shayan-human/MAP-MINER.git
cd MAP-MINER
docker-compose up --build
```
Access the dashboard at: **http://localhost:8000**

### Option 2: Local Setup (One Command)
Use our automation script to handle virtual environment and Playwright setup.
```bash
python3 run.py --setup
```
*Note: This will create a `venv`, install dependencies, and download the Chromium browser automatically.*

---

## ✨ Features

- **Nuclear Scraper V2.1** - High-robustness Google Maps harvesting with smart scrolling and stealth integration.
- **Smart Enrichment** - Crawls business websites to find contact emails, including detection of obfuscated patterns (e.g., `info [at] domain [dot] com`).
- **Master Lead DB** - Integrated SQLite database automatically deduplicates leads across different searches.
- **Proxy Rotation** - Supports HTTP/Socks proxies with built-in rotation and a "Strict Mode" for IP protection.
- **Glassmorphic UI** - Modern web dashboard for managing jobs, monitoring progress, and downloading datasets.
- **CSV Refinement** - Upload external CSV files to enrich or filter them against your local database.

---

## ⚙️ Configuration

| Environment Variable | Description | Default |
|----------------------|-------------|---------|
| `MAPMINER_OUTPUT_DIR` | Path to store CSVs and Database | `turbo/outputs/` |
| `MAPMINER_STATIC_DIR` | Path to frontend assets | `turbo/static/` |
| `PYTHONPATH` | Python module path | `.` |

### Proxy Format
Provide a comma-separated list or a file link: `http://user:pass@host:port,http://user2:pass2@host2:port2`

---

## 🛠 Project Structure

```text
.
├── run.py              # Main automation & setup script
├── Dockerfile          # Production Docker image
├── docker-compose.yml  # Multi-container orchestration
├── turbo/
│   ├── server.py       # FastAPI Web Server
│   ├── search.py       # Nuclear Maps Scraper
│   ├── enrich.py       # Smart Email Extraction
│   ├── db.py           # SQLite Deduplication Engine
│   └── static/         # Glassmorphic UI Assets
└── outputs/            # Persistent Data (Leads, CSVs)
```

---

## 🛡 License
MIT - Created by [Shayan Alam](https://github.com/shayan-human)