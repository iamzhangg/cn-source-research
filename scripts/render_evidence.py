#!/usr/bin/env python3
"""Validate and render a Chinese-web evidence pack without dependencies."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from urllib.parse import urlparse


def _date(value: str, field: str) -> None:
    try:
        date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must use YYYY-MM-DD") from exc


def validate(pack: dict) -> None:
    for field in ("question", "as_of", "items"):
        if field not in pack:
            raise ValueError(f"missing root field: {field}")
    _date(pack["as_of"], "as_of")
    if not isinstance(pack["items"], list) or not pack["items"]:
        raise ValueError("items must be a non-empty list")
    required = ("claim", "url", "title", "publisher", "accessed_at", "tier", "support", "status")
    for index, item in enumerate(pack["items"], start=1):
        for field in required:
            if not item.get(field):
                raise ValueError(f"item {index}: missing {field}")
        parsed = urlparse(item["url"])
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError(f"item {index}: url must be HTTP(S)")
        if item["tier"] not in {"A", "B", "C", "D"}:
            raise ValueError(f"item {index}: invalid tier")
        if item["status"] not in {"supports", "contradicts", "context"}:
            raise ValueError(f"item {index}: invalid status")
        if item.get("published_at") is not None:
            _date(item["published_at"], f"item {index}.published_at")
        _date(item["accessed_at"], f"item {index}.accessed_at")


def render(pack: dict) -> str:
    validate(pack)
    lines = [f"# Evidence: {pack['question']}", "", f"As of: {pack['as_of']}", ""]
    for index, item in enumerate(pack["items"], start=1):
        lines.extend([
            f"## {index}. {item['claim']}", "",
            f"- Source: [{item['title']}]({item['url']}) - {item['publisher']}",
            f"- Published / accessed: {item.get('published_at') or 'unknown'} / {item['accessed_at']}",
            f"- Grade / stance: {item['tier']} / {item['status']}",
            f"- Support: {item['support']}",
        ])
        if item.get("limitations"):
            lines.append(f"- Limitations: {item['limitations']}")
        if item.get("quote"):
            lines.append(f"> {item['quote']}")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = render(json.loads(args.input.read_text(encoding="utf-8")))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
