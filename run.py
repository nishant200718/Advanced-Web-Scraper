#!/usr/bin/env python3
# ==============================================================================
#  run.py -- Advanced Web Scraper -- Entry Point
# ==============================================================================
#
#  Usage:
#    python run.py                       # Scrape all targets in config.yaml
#    python run.py --url https://example.com --name example
#    python run.py --target deloitte     # Scrape only one target from config
#    python run.py --help
#
# ==============================================================================

import argparse
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Force UTF-8 stdout on Windows to avoid encoding errors
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import yaml
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.table import Table

# Ensure the project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from scraper.engine import ScraperEngine
from scraper.reporter import Reporter

console = Console()


# ── Logging Setup ────────────────────────────────────────────────────────────

def setup_logging(verbose: bool = False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        handlers=[
            RichHandler(
                console=console,
                show_time=True,
                show_path=False,
                rich_tracebacks=True,
            )
        ],
    )


# ── Config Loading ───────────────────────────────────────────────────────────

def load_config(config_path: str) -> dict:
    path = Path(config_path)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    if not path.exists():
        console.print(f"[red]Error:[/red] Config file not found: {path}")
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ── Banner ───────────────────────────────────────────────────────────────────

BANNER = r"""
     _    ______     ___    _   _  ____ _____ ____
    / \  |  _ \ \   / / \  | \ | |/ ___| ____|  _ \
   / _ \ | | | \ \ / / _ \ |  \| | |   |  _| | | | |
  / ___ \| |_| |\ V / ___ \| |\  | |___| |___| |_| |
 /_/   \_\____/  \_/_/   \_\_| \_|\____|_____|____/

 __        _______ ____    ____   ____ ____      _    ____  _____ ____
 \ \      / / ____| __ )  / ___| / ___|  _ \    / \  |  _ \| ____|  _ \
  \ \ /\ / /|  _| |  _ \  \___ \| |   | |_) |  / _ \ | |_) |  _| | |_) |
   \ V  V / | |___| |_) |  ___) | |___|  _ <  / ___ \|  __/| |___|  _ <
    \_/\_/  |_____|____/  |____/ \____|_| \_\/_/   \_\_|   |_____|_| \_\
"""


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Advanced Web Scraper — Retrieve all data from any website",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--config", "-c", default="config.yaml",
        help="Path to YAML config file (default: config.yaml)",
    )
    parser.add_argument(
        "--url", "-u",
        help="Scrape a single URL (overrides config targets)",
    )
    parser.add_argument(
        "--name", "-n", default="custom",
        help="Site name for single-URL mode (default: custom)",
    )
    parser.add_argument(
        "--target", "-t",
        help="Scrape only this named target from config",
    )
    parser.add_argument(
        "--max-pages", "-m", type=int,
        help="Override max pages per site",
    )
    parser.add_argument(
        "--depth", "-d", type=int,
        help="Override max crawl depth",
    )
    parser.add_argument(
        "--output", "-o",
        help="Override output directory",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Enable debug logging",
    )
    args = parser.parse_args()

    setup_logging(args.verbose)
    console.print(Panel(BANNER, style="bold cyan", border_style="cyan"))
    console.print(f"[dim]Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]\n")

    # Load config
    config = load_config(args.config)

    # Apply CLI overrides
    if args.max_pages:
        config.setdefault("crawl", {})["max_pages_per_site"] = args.max_pages
        for target in config.get("targets", []):
            target["max_pages"] = args.max_pages
    if args.depth is not None:
        config.setdefault("crawl", {})["max_depth"] = args.depth

    # Determine output dir
    output_cfg = config.get("output", {})
    output_dir = args.output or output_cfg.get("directory", "output")
    output_dir = os.path.join(str(PROJECT_ROOT), output_dir)
    os.makedirs(output_dir, exist_ok=True)

    formats = output_cfg.get("formats", ["html", "json", "csv"])

    # Handle single-URL mode
    if args.url:
        config["targets"] = [{"name": args.name, "url": args.url}]
    elif args.target:
        # Filter to just one target
        targets = config.get("targets", [])
        matched = [t for t in targets if t.get("name", "").lower() == args.target.lower()]
        if not matched:
            console.print(f"[red]Error:[/red] Target '{args.target}' not found in config.")
            available = [t.get("name") for t in targets]
            console.print(f"Available targets: {', '.join(available)}")
            sys.exit(1)
        config["targets"] = matched

    # Show target summary
    targets = config.get("targets", [])
    table = Table(title="Targets", show_header=True, header_style="bold cyan")
    table.add_column("Name", style="white")
    table.add_column("URL", style="cyan")
    table.add_column("Max Pages", justify="center", style="yellow")
    for t in targets:
        table.add_row(
            t.get("name", "?"),
            t.get("url", "?"),
            str(t.get("max_pages", config.get("crawl", {}).get("max_pages_per_site", 30))),
        )
    console.print(table)
    console.print()

    # Run scraper
    engine = ScraperEngine(config)
    reporter = Reporter(output_dir, formats)

    start = time.time()
    results = engine.scrape_all()
    total_time = time.time() - start

    # Generate reports
    console.print(f"\n[bold yellow]{'='*60}")
    console.print("[bold yellow]  [*] Generating Reports")
    console.print(f"[bold yellow]{'='*60}\n")

    report_paths = []
    for result in results:
        path = reporter.generate(result)
        report_paths.append(path)
        console.print(f"  [green][+][/green] {result.name}: [cyan]{path}[/cyan]")

    # Final summary
    console.print(f"\n[bold green]{'='*60}")
    console.print("[bold green]  [+] ALL DONE!")
    console.print(f"[bold green]{'='*60}")

    summary = Table(show_header=True, header_style="bold green")
    summary.add_column("Site", style="white")
    summary.add_column("Pages", justify="center", style="cyan")
    summary.add_column("Links Found", justify="center", style="yellow")
    summary.add_column("Duration", justify="center", style="magenta")
    summary.add_column("Output", style="dim")

    for result, path in zip(results, report_paths):
        ok = sum(1 for p in result.pages if p.status == "ok")
        summary.add_row(
            result.name,
            str(ok),
            str(result.total_links_found),
            f"{result.duration:.1f}s",
            path,
        )
    console.print(summary)
    console.print(f"\n[dim]Total time: {total_time:.1f}s[/dim]")
    console.print(f"[dim]Output directory: {output_dir}[/dim]\n")

    # Print report locations
    console.print("[bold]Output Structure:[/bold]")
    for path in report_paths:
        name = os.path.basename(path)
        console.print(f"  [dir] {path}/")
        for fmt in formats:
            if fmt == "html":
                console.print(f"     [file] report.html       [dim]<- Open in browser for interactive report[/dim]")
            elif fmt == "json":
                console.print(f"     [file] full_data.json    [dim]<- Complete machine-readable data[/dim]")
            elif fmt == "csv":
                console.print(f"     [dir]  csv/              [dim]<- Tabular exports[/dim]")
                console.print(f"        [file] metadata.csv")
                console.print(f"        [file] links.csv")
                console.print(f"        [file] images.csv")
                console.print(f"        [file] contacts.csv")
                console.print(f"        [file] social_media.csv")
    console.print()


if __name__ == "__main__":
    main()
