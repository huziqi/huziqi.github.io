#!/usr/bin/env python3
"""
fetch_scholar.py
================
Auto-sync publications from Google Scholar to the Jekyll _publications/ directory.

Usage:
    python fetch_scholar.py [--dry-run] [--scholar-id SCHOLAR_ID]

Dependencies:
    pip install scholarly python-slugify

Features:
    - Fetches all publications from Google Scholar profile
    - Creates new .md files for papers not yet in _publications/
    - Skips papers already present (matched by title similarity)
    - Preserves all manually set fields (author_position, corresponding, etc.)
    - Provides a summary of added/skipped papers
"""

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# ── Configuration ──────────────────────────────────────────────────────────────

SCHOLAR_ID = "yBC3H5MAAAAJ"          # Google Scholar user ID from _config.yml
PUBLICATIONS_DIR = Path(__file__).parent / "_publications"
AUTHOR_NAME_VARIANTS = ["Ziqi Hu", "Z. Hu", "Hu, Z.", "Hu, Ziqi"]

# ── Helpers ────────────────────────────────────────────────────────────────────

def normalize_title(title: str) -> str:
    """Lowercase, strip punctuation for fuzzy comparison."""
    return re.sub(r"[^a-z0-9 ]", "", title.lower()).strip()


def title_to_slug(title: str) -> str:
    """Convert a title to a safe filename slug."""
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug[:80]


def existing_titles() -> dict:
    """Return {normalized_title: Path} for all existing publication files."""
    result = {}
    for f in PUBLICATIONS_DIR.glob("*.md"):
        content = f.read_text(encoding="utf-8")
        m = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', content, re.MULTILINE)
        if m:
            result[normalize_title(m.group(1))] = f
    return result


def get_author_position(authors_str: str) -> int:
    """Return 1-based position of Ziqi Hu in the author list (0 if not found)."""
    # scholarly returns authors as a list or comma-separated string
    if isinstance(authors_str, list):
        authors = authors_str
    else:
        authors = [a.strip() for a in re.split(r",\s*(?:and\s+)?", authors_str)]

    for i, author in enumerate(authors, start=1):
        for variant in AUTHOR_NAME_VARIANTS:
            if variant.lower() in author.lower():
                return i
    return 0


def format_authors_html(authors_str: str) -> str:
    """Bold 'Ziqi Hu' in the author string."""
    if isinstance(authors_str, list):
        parts = authors_str
    else:
        parts = [a.strip() for a in re.split(r",\s*(?:and\s+)?", authors_str)]

    formatted = []
    for part in parts:
        is_ziqi = any(v.lower() in part.lower() for v in AUTHOR_NAME_VARIANTS)
        formatted.append(f"<strong>{part}</strong>" if is_ziqi else part)

    if len(formatted) > 1:
        return ", ".join(formatted[:-1]) + ", and " + formatted[-1]
    return formatted[0] if formatted else ""


def build_citation(pub: dict) -> str:
    """Build a formatted citation string from scholarly pub dict."""
    bib = pub.get("bib", {})
    authors = bib.get("author", "")
    title  = bib.get("title", "Unknown Title")
    venue  = bib.get("venue", bib.get("journal", bib.get("booktitle", "")))
    year   = bib.get("pub_year", "")
    volume = bib.get("volume", "")
    pages  = bib.get("pages", "")
    number = bib.get("number", "")

    authors_html = format_authors_html(authors)
    venue_part = f"<i>{venue}</i>" if venue else ""

    details = []
    if volume:
        details.append(volume)
    if number:
        details.append(f"({number})")
    if pages:
        details.append(pages)

    detail_str = ", ".join(filter(None, details))
    citation = f'{authors_html}. ({year}). "{title}." {venue_part}'
    if detail_str:
        citation += f", {detail_str}."
    else:
        citation += "."
    return citation


def build_md_content(pub: dict, author_pos: int, pub_date: str) -> str:
    """Generate front-matter markdown content for a new publication."""
    bib   = pub.get("bib", {})
    title = bib.get("title", "Unknown Title")
    venue = bib.get("venue", bib.get("journal", bib.get("booktitle", "")))
    url   = pub.get("pub_url", "") or ""
    slug  = title_to_slug(title)
    citation = build_citation(pub)
    year  = bib.get("pub_year", datetime.now().year)

    return f"""---
title: "{title}"
collection: publications
permalink: /publication/{pub_date}-{slug}
excerpt: ''
date: {pub_date}
venue: '{venue}'
paperurl: ''
venue_url: '{url}'
author_position: {author_pos}
corresponding: false
citation: '{citation}'
---
"""


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Sync publications from Google Scholar.")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be added without writing files.")
    parser.add_argument("--scholar-id", default=SCHOLAR_ID, help="Google Scholar user ID.")
    args = parser.parse_args()

    try:
        from scholarly import scholarly, ProxyGenerator
    except ImportError:
        print("ERROR: Please install 'scholarly': pip install scholarly")
        sys.exit(1)

    print(f"Fetching publications for Scholar ID: {args.scholar_id} ...")

    # Optional: set up a proxy to avoid rate limiting
    # pg = ProxyGenerator()
    # pg.FreeProxies()
    # scholarly.use_proxy(pg)

    try:
        author = scholarly.search_author_id(args.scholar_id)
        author = scholarly.fill(author, sections=["publications"])
    except Exception as e:
        print(f"ERROR: Failed to fetch Scholar profile: {e}")
        sys.exit(1)

    existing = existing_titles()
    added = []
    skipped = []

    pubs = author.get("publications", [])
    print(f"Found {len(pubs)} publications on Google Scholar.\n")

    for pub in pubs:
        try:
            pub_filled = scholarly.fill(pub)
        except Exception:
            pub_filled = pub

        bib   = pub_filled.get("bib", {})
        title = bib.get("title", "")
        if not title:
            continue

        norm_title = normalize_title(title)

        # Skip if already exists
        if norm_title in existing:
            skipped.append(title)
            continue

        # Determine author position
        authors_str = bib.get("author", "")
        author_pos  = get_author_position(authors_str)

        # Determine publication date
        year = bib.get("pub_year", "")
        if year:
            pub_date = f"{year}-01-01"
        else:
            pub_date = datetime.now().strftime("%Y-%m-%d")

        slug     = title_to_slug(title)
        filename = f"{pub_date}-{slug}.md"
        filepath = PUBLICATIONS_DIR / filename

        md_content = build_md_content(pub_filled, author_pos, pub_date)

        if args.dry_run:
            print(f"[DRY RUN] Would create: {filename}")
            print(f"          Title: {title}")
            print(f"          Author position: {author_pos}")
            print()
        else:
            filepath.write_text(md_content, encoding="utf-8")
            print(f"[ADDED] {filename}")
            added.append(title)

    # ── Summary ────────────────────────────────────────────────────────────────
    print("\n" + "="*60)
    print(f"Summary:")
    print(f"  Fetched from Google Scholar : {len(pubs)}")
    print(f"  Already in _publications/   : {len(skipped)}")
    print(f"  {'Would add' if args.dry_run else 'Added'}               : {len(added)}")

    if skipped:
        print(f"\nSkipped (already present):")
        for t in skipped:
            print(f"  - {t}")

    if added:
        print(f"\n{'Would add' if args.dry_run else 'Added'}:")
        for t in added:
            print(f"  + {t}")

    print("\nDone. Remember to review and update the 'author_position' and 'corresponding'")
    print("fields in any newly created files, then rebuild your Jekyll site.")


if __name__ == "__main__":
    main()
