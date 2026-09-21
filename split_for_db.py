#!/usr/bin/env python3
"""Split feed.json into the per-document files the Scrolling page reads from its database.

Usage: python3 split_for_db.py [feed.json] [out_dir]
Writes out_dir/meta.json, football.json, news.json, medical.json, growth.json (+ barcelona.json if present).
Database collection: "brief", one document per file (doc id = file name without .json).
"""
import json, sys
from pathlib import Path

src = Path(sys.argv[1] if len(sys.argv) > 1 else "feed.json")
out = Path(sys.argv[2] if len(sys.argv) > 2 else "db_docs")
out.mkdir(parents=True, exist_ok=True)
feed = json.loads(src.read_text())
meta = {"generatedAt": feed["generatedAt"], "windowsDays": feed.get("windowsDays", {}), "sample": bool(feed.get("sample"))}
(out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False))
for cat, stories in feed["tabs"].items():
    doc = {"updatedAt": feed["generatedAt"], "stories": stories}
    size = len(json.dumps(doc, ensure_ascii=False).encode())
    if size > 250_000:
        raise SystemExit(f"{cat}: {size} bytes exceeds the 256 KiB document limit; lower CATEGORY_CAP or shorten summaries")
    (out / f"{cat}.json").write_text(json.dumps(doc, ensure_ascii=False))
if feed.get("barcelona"):
    (out / "barcelona.json").write_text(json.dumps(feed["barcelona"], ensure_ascii=False))
print("wrote", sorted(p.name for p in out.iterdir()))
