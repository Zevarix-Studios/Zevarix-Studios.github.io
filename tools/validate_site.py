#!/usr/bin/env python3
"""Deterministic source validation for the Zevarix Studios public site."""

from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_ORIGIN = "https://zevarix.com/"
REQUIRED_FILES = {
    "index.html", "site.css", "site-accessibility.css",
    "site-brand-controls.css", "site-planet.css",
    "site-public-brand.css", "site-easter-egg.css",
    "site.js", "CNAME", "robots.txt", "sitemap.xml", ".nojekyll",
}


class ReferenceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[str] = []
        self.canonicals: list[str] = []
        self.meta: dict[tuple[str, str], str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value for key, value in attrs if value is not None}
        for key in ("href", "src"):
            value = values.get(key)
            if value:
                self.refs.append(value)

        if tag == "link" and values.get("rel") == "canonical":
            href = values.get("href")
            if href:
                self.canonicals.append(href)

        if tag == "meta" and "content" in values:
            if "name" in values:
                self.meta[("name", values["name"])] = values["content"]
            if "property" in values:
                self.meta[("property", values["property"])] = values["content"]


def _local_path(root: Path, value: str) -> Path | None:
    if value.startswith(("#", "mailto:", "tel:", "data:")):
        return None
    parsed = urlparse(value)
    if parsed.scheme or parsed.netloc:
        return None
    clean = value.split("?", 1)[0].split("#", 1)[0].lstrip("/")
    return root / clean if clean else None


def validate_site(root: Path) -> list[str]:
    errors: list[str] = []
    for relative in sorted(REQUIRED_FILES):
        if not (root / relative).is_file():
            errors.append(f"missing required file: {relative}")

    index = root / "index.html"
    if not index.is_file():
        return errors

    parser = ReferenceParser()
    parser.feed(index.read_text(encoding="utf-8"))

    if parser.canonicals != [CANONICAL_ORIGIN]:
        errors.append("index.html must contain exactly one canonical zevarix.com URL")

    required_meta = {
        ("name", "description"),
        ("name", "twitter:card"),
        ("property", "og:title"),
        ("property", "og:description"),
        ("property", "og:url"),
        ("property", "og:image"),
    }
    for key in sorted(required_meta):
        if not parser.meta.get(key):
            errors.append(f"missing metadata: {key[1]}")

    if parser.meta.get(("property", "og:url")) != CANONICAL_ORIGIN:
        errors.append("og:url must match the canonical origin")

    for value in parser.refs:
        local = _local_path(root, value)
        if local is not None and not local.exists():
            errors.append(f"missing local HTML reference: {value}")

    if (root / "CNAME").is_file():
        if (root / "CNAME").read_text(encoding="utf-8").strip() != "zevarix.com":
            errors.append("CNAME must contain zevarix.com")

    robots = root / "robots.txt"
    if robots.is_file() and "Sitemap: https://zevarix.com/sitemap.xml" not in robots.read_text(encoding="utf-8"):
        errors.append("robots.txt must point at the canonical sitemap")

    sitemap = root / "sitemap.xml"
    if sitemap.is_file():
        try:
            tree = ET.parse(sitemap)
            locations = [element.text for element in tree.findall("{*}url/{*}loc")]
            if locations != [CANONICAL_ORIGIN]:
                errors.append("sitemap.xml must contain only the canonical root URL")
        except ET.ParseError as exc:
            errors.append(f"sitemap.xml is invalid XML: {exc}")

    key_files = [
        path for path in root.glob("*.txt")
        if re.fullmatch(r"[0-9a-f]{32}\.txt", path.name)
    ]
    if len(key_files) != 1:
        errors.append("expected exactly one 32-hex IndexNow key file")
    else:
        key = key_files[0].stem
        if key_files[0].read_text(encoding="utf-8").strip() != key:
            errors.append("IndexNow key file content must match its filename")
        workflow = root / ".github" / "workflows" / "indexnow.yml"
        if workflow.is_file():
            text = workflow.read_text(encoding="utf-8")
            if f"INDEXNOW_KEY: {key}" not in text:
                errors.append("IndexNow workflow key does not match the published key file")

    for workflow in sorted((root / ".github" / "workflows").glob("*.yml")):
        for line_number, line in enumerate(workflow.read_text(encoding="utf-8").splitlines(), 1):
            match = re.search(r"\buses:\s*[^@\s]+@([^\s#]+)", line)
            if match and not re.fullmatch(r"[0-9a-f]{40}", match.group(1)):
                errors.append(f"{workflow.relative_to(root)}:{line_number}: action is not pinned to a full SHA")

    return errors


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT
    errors = validate_site(root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Public site source validation PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
