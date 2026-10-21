# 🌐 Advanced Web Scraper

A powerful, configurable Python web scraper that extracts **all types of data** from any website and produces beautifully formatted, interactive HTML reports along with JSON and CSV exports.

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Multi-page BFS Crawling** | Crawls websites breadth-first with configurable depth & page limits |
| **Metadata Extraction** | Title, description, keywords, Open Graph, Twitter Cards, canonical URLs |
| **Content Extraction** | Headings (h1–h6), paragraphs, lists, navigation structure |
| **Link Analysis** | Internal vs. external links with anchor text |
| **Image Cataloging** | All images with src, alt text, dimensions |
| **Table Parsing** | HTML tables → structured headers + rows |
| **Form Detection** | Form actions, methods, input fields |
| **Contact Info** | Emails and phone numbers via regex extraction |
| **Social Media** | Detects links to Twitter/X, LinkedIn, Facebook, Instagram, YouTube, GitHub |
| **Structured Data** | JSON-LD / Schema.org extraction |
| **robots.txt** | Respects `robots.txt` directives |
| **Rate Limiting** | Configurable delays + jitter to be polite |
| **User-Agent Rotation** | Rotates through realistic browser UAs |
| **Retry Logic** | Automatic retries with backoff on failures |
| **Beautiful Reports** | Dark-themed interactive HTML with search, collapsible sections |
| **JSON Export** | Complete machine-readable data dump |
| **CSV Export** | Tabular files for metadata, links, images, contacts, social |

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Scrape all configured targets
python run.py

# 3. Scrape a single URL
python run.py --url https://about.google --name google

# 4. Scrape one target from config
python run.py --target microsoft

# 5. Custom depth and page limit
python run.py --url https://example.com --name example --depth 3 --max-pages 50
```

## 📁 Output Structure

```
output/
├── deloitte/
│   ├── report.html          ← Interactive HTML report (open in browser)
│   ├── full_data.json       ← Complete JSON data
│   └── csv/
│       ├── metadata.csv     ← Page titles, descriptions, URLs
│       ├── links.csv        ← All internal + external links
│       ├── images.csv       ← Image sources and alt text
│       ├── contacts.csv     ← Emails and phone numbers
│       └── social_media.csv ← Social media profile links
├── google/
│   └── ...
├── microsoft/
│   └── ...
└── goldman_sachs/
    └── ...
```

## ⚙️ Configuration

Edit `config.yaml` to customize behavior:

```yaml
targets:
  - name: my_site
    url: https://example.com
    max_pages: 50

crawl:
  max_depth: 3          # How deep to follow links
  max_pages_per_site: 30
  request_delay: 1.5    # Seconds between requests
  respect_robots_txt: true

extract:
  metadata: true
  headings: true
  links: true
  images: true
  tables: true
  contact_info: true
  social_media: true
  structured_data: true
```

## 🖥️ CLI Options

| Flag | Description |
|------|-------------|
| `--url`, `-u` | Scrape a single URL |
| `--name`, `-n` | Site name for single-URL mode |
| `--target`, `-t` | Scrape one target from config |
| `--config`, `-c` | Path to config file (default: config.yaml) |
| `--max-pages`, `-m` | Override max pages |
| `--depth`, `-d` | Override max crawl depth |
| `--output`, `-o` | Override output directory |
| `--verbose`, `-v` | Enable debug logging |

## 📊 HTML Report Features

- **Dark theme** with modern design
- **Collapsible sections** for each data type
- **Global search** across all extracted data
- **Statistics dashboard** with page/link/image/table counts
- **Clickable links** to original pages
- **Responsive** — works on mobile

## ⚠️ Legal & Ethical Notes

- Always check a website's **Terms of Service** before scraping
- This scraper **respects robots.txt** by default
- Built-in **rate limiting** to avoid overloading servers
- Use responsibly and for legitimate purposes only
