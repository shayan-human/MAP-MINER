# MAP-MINER

**Google Maps Scraper with Web Dashboard**

---

## Quick Start (All OS)

```bash
# Clone & Run
git clone https://github.com/shayan-human/MAP-MINER.git
cd MAP-MINER

# Run (auto-creates venv & installs deps)
python run.py
```

Then open **http://localhost:8000**

---

## Manual Install

```bash
git clone https://github.com/shayan-human/MAP-MINER.git
cd MAP-MINER

# Create venv
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install deps
pip install -r turbo/requirements.txt
pip install playwright
python -m playwright install chromium

# Run
python run.py
```

---

## Alternative: Shell Script (Linux/Mac only)

```bash
chmod +x mapminer
./mapminer
```

---

## License

MIT - © 2026 Shayan Alam
