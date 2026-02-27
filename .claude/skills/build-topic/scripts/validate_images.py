#!/usr/bin/env python3
"""
Validate image URLs in a LessonLines event data JSON file.

Usage:
    python scripts/validate_images.py event-data/french_revolution.json
    python scripts/validate_images.py event-data/  # validate all files in dir

For each event, checks that image_url:
  - Is a valid Wikimedia Commons URL
  - Actually exists (HTTP 200)
  - Uses the 300px thumbnail format

Exits with code 1 if any images are broken.
"""

import json
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path


HEADERS = {"User-Agent": "LessonLinesBot/1.0 (educational app; image validation)"}
BATCH_SIZE = 20


def wikimedia_filename_from_url(url: str) -> str | None:
    """Extract the Wikimedia Commons filename from a thumbnail or full URL."""
    # e.g. https://upload.wikimedia.org/wikipedia/commons/thumb/a/aa/Foo.jpg/300px-Foo.jpg
    # e.g. https://upload.wikimedia.org/wikipedia/commons/a/aa/Foo.jpg
    if "upload.wikimedia.org" not in url:
        return None
    parts = url.rstrip("/").split("/")
    filename = urllib.parse.unquote(parts[-1])
    # Thumb URLs end with "300px-Foo.jpg" — strip the size prefix
    if filename.startswith(("300px-", "200px-", "400px-", "500px-")):
        filename = filename.split("-", 1)[1]
    return filename


def check_urls_via_api(filenames: list[str]) -> dict[str, str | None]:
    """
    Use Wikimedia Commons API to get thumbnail URLs for a batch of filenames.
    Returns {filename: thumb_url_or_None}.
    """
    titles = "|".join(f"File:{f}" for f in filenames)
    params = urllib.parse.urlencode({
        "action": "query",
        "titles": titles,
        "prop": "imageinfo",
        "iiprop": "url",
        "iiurlwidth": "300",
        "format": "json",
    })
    api_url = f"https://commons.wikimedia.org/w/api.php?{params}"
    req = urllib.request.Request(api_url, headers=HEADERS)

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        print(f"  [API error] {e}", file=sys.stderr)
        return {f: None for f in filenames}

    results = {}
    for page in data.get("query", {}).get("pages", {}).values():
        title = page.get("title", "")
        # Wikimedia API normalizes spaces; convert back to underscores to match URL-extracted filenames
        filename = title.removeprefix("File:").replace(" ", "_")
        imageinfo = page.get("imageinfo")
        if imageinfo:
            # Prefer thumburl, fall back to url
            thumb = imageinfo[0].get("thumburl") or imageinfo[0].get("url")
            results[filename] = thumb
        else:
            results[filename] = None

    # Any filename not in results is also missing
    for f in filenames:
        if f not in results:
            results[f] = None

    return results


def validate_file(path: Path) -> list[dict]:
    """
    Validate all image_urls in a JSON event file.
    Returns a list of issues: [{event_id, title, url, issue}]
    """
    with open(path) as f:
        data = json.load(f)

    events = data.get("events", [])
    if not events:
        print(f"  No events found in {path.name}")
        return []

    # Collect events with image URLs
    events_with_images = [(e["id"], e["title"], e.get("image_url", "")) for e in events]
    events_no_image = [(eid, title) for eid, title, url in events_with_images if not url]
    events_with_url = [(eid, title, url) for eid, title, url in events_with_images if url]

    issues = []

    # Warn about missing image_url fields
    for eid, title in events_no_image:
        issues.append({"event_id": eid, "title": title, "url": "", "issue": "No image_url set"})

    # Extract filenames and batch-check via Wikimedia API
    filename_map = {}  # filename -> [(event_id, title, url)]
    non_wikimedia = []

    for eid, title, url in events_with_url:
        filename = wikimedia_filename_from_url(url)
        if filename:
            filename_map.setdefault(filename, []).append((eid, title, url))
        else:
            non_wikimedia.append((eid, title, url))

    if non_wikimedia:
        for eid, title, url in non_wikimedia:
            issues.append({"event_id": eid, "title": title, "url": url,
                           "issue": "Not a Wikimedia Commons URL"})

    # Batch-check filenames via API
    filenames = list(filename_map.keys())
    for i in range(0, len(filenames), BATCH_SIZE):
        batch = filenames[i:i + BATCH_SIZE]
        results = check_urls_via_api(batch)
        time.sleep(0.3)  # be polite

        for filename, thumb_url in results.items():
            events_using = filename_map.get(filename, [])
            if thumb_url is None:
                for eid, title, url in events_using:
                    issues.append({"event_id": eid, "title": title, "url": url,
                                   "issue": f"File not found on Wikimedia Commons: {filename}"})
            else:
                # Check the URL in the file uses thumb format
                for eid, title, url in events_using:
                    if "/thumb/" not in url:
                        issues.append({"event_id": eid, "title": title, "url": url,
                                       "issue": f"Full-size URL used; use thumbnail instead: {thumb_url}"})

    return issues


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/validate_images.py <file.json|directory>")
        sys.exit(1)

    target = Path(sys.argv[1])
    if target.is_dir():
        files = sorted(target.glob("*.json"))
    elif target.is_file():
        files = [target]
    else:
        print(f"Error: {target} not found")
        sys.exit(1)

    total_issues = 0

    for path in files:
        print(f"\nValidating {path.name} ...", flush=True)
        issues = validate_file(path)
        if not issues:
            print("  All images OK")
        else:
            for issue in issues:
                print(f"  FAIL [{issue['event_id']}] {issue['title']}")
                print(f"       {issue['issue']}")
                if issue['url']:
                    print(f"       URL: {issue['url']}")
            total_issues += len(issues)

    print()
    if total_issues:
        print(f"Found {total_issues} issue(s).")
        sys.exit(1)
    else:
        print("All files valid.")
        sys.exit(0)


if __name__ == "__main__":
    main()
