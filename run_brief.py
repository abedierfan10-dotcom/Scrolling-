#!/usr/bin/env python3
"""Scrolling morning brief job.

Fetches RSS/Atom feeds (plus PubMed via E-utilities), applies per-category
freshness windows, deduplicates by URL and title similarity, ranks with
priority keywords + recency + cluster size + interest weights, tags subtopics,
tracks first-seen / NEW state, and writes feed.json for the app.

Stdlib only. Run daily at 10:00 Europe/Berlin.
"""
import concurrent.futures as cf
import hashlib
import html
import json
import math
import os
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

import rules

HERE = Path(__file__).parent
CONFIG = json.loads((HERE / "feeds.json").read_text())
STATE_PATH = HERE / "state.json"          # first-seen timestamps, developing-story memory
INTERESTS_PATH = HERE / "interests.json"  # exported from the app: {"Barcelona": 2, "Negotiation": -1}
OUT_PATH = HERE / "feed.json"
UA = "ScrollingBriefBot/1.0 (personal feed reader; polite, low volume)"
NOW = datetime.now(timezone.utc)
TIMEOUT = 15
PER_FEED_CAP = 40
CATEGORY_CAP = 35

NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "dc": "http://purl.org/dc/elements/1.1/",
    "content": "http://purl.org/rss/1.0/modules/content/",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rss1": "http://purl.org/rss/1.0/",
    "media": "http://search.yahoo.com/mrss/",
    "yt": "http://www.youtube.com/xml/schemas/2015",
}

STOP = set("""a an the and or of to in on for with at by from is are was were be been it its this that as
der die das und oder von zu im in auf für mit bei aus ist sind war wurde wird ein eine einen nach über
vs says said say new after before will could would""".split())


# ---------- helpers ----------
def strip_html(s: str) -> str:
    s = re.sub(r"<[^>]+>", " ", s or "")
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def parse_date(s):
    if not s:
        return None
    s = s.strip()
    try:
        d = parsedate_to_datetime(s)
    except (TypeError, ValueError):
        try:
            d = datetime.fromisoformat(s.replace("Z", "+00:00"))
        except ValueError:
            return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return d.astimezone(timezone.utc)


def canon_url(u: str) -> str:
    p = urllib.parse.urlsplit(u)
    q = [(k, v) for k, v in urllib.parse.parse_qsl(p.query) if not k.lower().startswith(("utm_", "at_", "ocid", "cmp"))]
    return urllib.parse.urlunsplit((p.scheme, p.netloc.lower().removeprefix("www."), p.path.rstrip("/"), urllib.parse.urlencode(q), ""))


def tokens(title: str):
    words = re.findall(r"[a-zA-ZäöüÄÖÜß0-9']{3,}", title.lower())
    return {w for w in words if w not in STOP}


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def http_get(url: str) -> bytes:
    fx = os.environ.get("SCROLLING_FIXTURES")  # offline test mode: fixtures/<host>.xml
    if fx:
        host = urllib.parse.urlsplit(url).netloc
        return (Path(fx) / f"{host}.xml").read_bytes()
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, */*"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return r.read()


# ---------- fetching ----------
def parse_feed(raw: bytes, feed: dict):
    items = []
    root = ET.fromstring(raw)
    tag = root.tag.lower()
    if tag.endswith("feed"):  # Atom
        for e in root.findall("atom:entry", NS):
            link = ""
            for l in e.findall("atom:link", NS):
                if l.get("rel", "alternate") == "alternate":
                    link = l.get("href", "")
                    break
            it = {
                "title": (e.findtext("atom:title", "", NS) or "").strip(),
                "url": link,
                "published": parse_date(e.findtext("atom:published", None, NS) or e.findtext("atom:updated", None, NS)),
                "summary": strip_html(e.findtext("atom:summary", "", NS) or e.findtext("atom:content", "", NS)),
            }
            vid = e.findtext("yt:videoId", None, NS)
            if vid:  # YouTube channel feed
                it["kind"] = "video"
                it["video_id"] = vid
                grp = e.find("media:group", NS)
                if grp is not None:
                    th = grp.find("media:thumbnail", NS)
                    it["thumb_url"] = th.get("url") if th is not None else f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"
                    it["summary"] = re.sub(r"https?://\S+", "", strip_html(grp.findtext("media:description", "", NS)))[:500].strip()
            items.append(it)
    else:  # RSS 2.0 / RSS 1.0 (RDF)
        nodes = root.findall(".//item") or root.findall(".//rss1:item", NS)
        for e in nodes:
            def g(name, ns=None):
                if ns:
                    return e.findtext(f"{{{NS[ns]}}}{name}", "") or ""
                return e.findtext(name, "") or e.findtext(f"{{{NS['rss1']}}}{name}", "") or ""
            items.append({
                "title": strip_html(g("title")),
                "url": (g("link") or g("guid")).strip(),
                "published": parse_date(g("pubDate") or g("date", "dc") or g("pubdate")),
                "summary": strip_html(g("description") or g("encoded", "content")),
            })
    return items


def fetch_pubmed(feed: dict):
    """PubMed via E-utilities (official, free). Newest matching papers in the window."""
    days = CONFIG["windows_days"][feed["category"]]
    q = urllib.parse.urlencode({"db": "pubmed", "term": feed["term"], "retmode": "json", "retmax": 25,
                                "datetype": "edat", "reldate": days, "sort": "date"})
    ids = json.loads(http_get(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?{q}"))["esearchresult"]["idlist"]
    if not ids:
        return []
    q = urllib.parse.urlencode({"db": "pubmed", "id": ",".join(ids), "retmode": "json"})
    res = json.loads(http_get(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?{q}"))["result"]
    items = []
    for pid in ids:
        r = res.get(pid)
        if not r:
            continue
        items.append({
            "title": strip_html(r.get("title", "")),
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pid}/",
            "published": parse_date(r.get("sortpubdate", "").replace(" ", "T").split("T")[0]) or NOW,
            "summary": f"{r.get('source', '')} ({r.get('pubdate', '')}). " + ", ".join(a["name"] for a in r.get("authors", [])[:3]),
        })
    return items


def fetch_ctgov(feed: dict):
    """ClinicalTrials.gov API v2: most recently updated studies for a search term."""
    q = urllib.parse.urlencode({"query.term": feed["term"], "sort": "LastUpdatePostDate:desc", "pageSize": 20})
    data = json.loads(http_get(f"https://clinicaltrials.gov/api/v2/studies?{q}"))
    items = []
    for st in data.get("studies", []):
        ps = st.get("protocolSection", {})
        ident = ps.get("identificationModule", {})
        nct = ident.get("nctId")
        upd = ps.get("statusModule", {}).get("lastUpdatePostDateStruct", {}).get("date")
        if not nct:
            continue
        brief = ps.get("descriptionModule", {}).get("briefSummary", "")
        items.append({
            "title": ident.get("briefTitle", nct),
            "url": f"https://clinicaltrials.gov/study/{nct}",
            "published": parse_date(upd) if upd else NOW,
            "summary": strip_html(brief),
        })
    return items


def youtube_durations(video_ids):
    """Optional: needs YOUTUBE_API_KEY (YouTube Data API v3). Returns {video_id: 'm:ss'}; empty when no key."""
    key = os.environ.get("YOUTUBE_API_KEY")
    out = {}
    if not key or not video_ids:
        return out
    for i in range(0, len(video_ids), 50):
        chunk = video_ids[i:i + 50]
        q = urllib.parse.urlencode({"part": "contentDetails", "id": ",".join(chunk), "key": key})
        try:
            data = json.loads(http_get(f"https://www.googleapis.com/youtube/v3/videos?{q}"))
        except Exception:
            continue
        for v in data.get("items", []):
            m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", v["contentDetails"]["duration"])
            h, mi, se = (int(x or 0) for x in m.groups())
            out[v["id"]] = f"{h}:{mi:02d}:{se:02d}" if h else f"{mi}:{se:02d}"
    return out


def fetch_one(feed: dict):
    try:
        items = (fetch_pubmed(feed) if feed.get("type") == "pubmed" else fetch_ctgov(feed) if feed.get("type") == "ctgov" else parse_feed(http_get(feed["url"]), feed))
        return feed, items[:PER_FEED_CAP], None
    except Exception as ex:  # one bad feed must never sink the brief
        return feed, [], f"{type(ex).__name__}: {ex}"


# ---------- pipeline ----------
def load_json(path, default):
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def first_sentences(text: str, n=2, max_chars=260):
    parts = re.split(r"(?<=[.!?])\s+", text)
    out = " ".join(parts[:n]).strip()
    return (out[: max_chars - 1].rsplit(" ", 1)[0] + "…") if len(out) > max_chars else out


def same_story(a, b):
    shared = len(a & b)
    if not shared:
        return False
    return jaccard(a, b) >= 0.5 or (shared >= 3 and shared / min(len(a), len(b)) >= 0.6)


def cluster(items):
    """Greedy title-similarity clustering. Same URL or Jaccard >= 0.55 => same story."""
    clusters = []
    for it in sorted(items, key=lambda x: x["published"], reverse=True):
        placed = False
        for c in clusters:
            if it["canon"] == c["lead"]["canon"] or same_story(it["tok"], c["lead"]["tok"]):
                c["members"].append(it)
                placed = True
                break
        if not placed:
            clusters.append({"lead": it, "members": [it]})
    return clusters


def evaluate(cat, members, known_comps):
    if cat == "football":
        return rules.eval_football(members)
    if cat == "news":
        return rules.eval_news(members)
    if cat == "medical":
        return rules.eval_medical(members, known_comps)
    return rules.eval_growth(members)


def main():
    state = load_json(STATE_PATH, {"seen": {}, "last_brief": None})
    state.setdefault("competitors", {})
    interests = load_json(INTERESTS_PATH, {})
    last_brief = parse_date(state.get("last_brief")) if state.get("last_brief") else None
    promote_after = rules.P["medical"]["promote_competitor_after"]
    known_comps = [n.lower() for n, c in state["competitors"].items() if c >= promote_after]

    feeds = CONFIG["feeds"]
    report = []
    by_cat = {c: [] for c in CONFIG["windows_days"]}
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        for feed, items, err in ex.map(fetch_one, feeds):
            report.append({"id": feed["id"], "ok": err is None, "items": len(items), "error": err})
            for it in items:
                if not it["title"] or not it["url"]:
                    continue
                pub = it["published"] or NOW
                if pub > NOW + timedelta(hours=2):
                    continue  # implausible future date: skip rather than give it max recency
                cat = feed["category"]
                if NOW - pub > timedelta(days=CONFIG["windows_days"][cat]):
                    continue
                it.update(published=pub, category=cat, lang=feed["lang"], source=feed["source"], tier=feed.get("tier", 4),
                          geo=feed.get("geo"), canon=canon_url(it["url"]), tok=tokens(it["title"]))
                if feed.get("kind"):
                    it["kind"] = feed["kind"]
                by_cat[cat].append(it)

    durations = youtube_durations([i["video_id"] for i in by_cat["growth"] if i.get("video_id")])

    feed_out, dropped = {}, {}
    for cat, items in by_cat.items():
        stories, dropped[cat] = [], 0
        for c in cluster(items):
            members = sorted(c["members"], key=lambda m: m["published"], reverse=True)
            lead = members[0]
            res = evaluate(cat, members, known_comps)
            if res is None:
                dropped[cat] += 1
                continue
            window = res.get("window_days", CONFIG["windows_days"][cat])
            if NOW - lead["published"] > timedelta(days=window):
                dropped[cat] += 1
                continue
            for name in res.get("discovered_competitors", []):
                state["competitors"][name] = state["competitors"].get(name, 0) + 1
            sources = sorted({m["source"] for m in members})
            best = max(members, key=lambda m: len(m["summary"]))
            sid = hashlib.sha1(lead["canon"].encode()).hexdigest()[:12]
            for m in members:  # stable id across days
                h = hashlib.sha1(m["canon"].encode()).hexdigest()[:12]
                if h in state["seen"]:
                    sid = h
                    break
            seen = state["seen"].get(sid)
            first_seen = parse_date(seen["first_seen"]) if seen else NOW
            hours = max((NOW - lead["published"]).total_seconds() / 3600, 0)
            recency = 3.0 * math.exp(-hours / (window * 24 / 2.5))
            if res.get("tags", {}).get("evergreen"):
                recency *= 0.3  # evergreen topics: quality over recency
            corroboration = min(len(sources) - 1, 3) * 0.8
            interest = sum(interests.get(t, 0) for t in res["subtopics"]) * 0.7
            score = round(recency + res["weight"] + corroboration + interest, 3)
            developing = len(members) >= 3 and (members[0]["published"] - members[-1]["published"]) >= timedelta(hours=6)
            story = {
                "id": sid, "category": cat, "lang": lead["lang"], "title": lead["title"],
                "summary": first_sentences(best["summary"]) or "",
                "needsSummary": True,          # the summary step (Claude) writes the polished summary + readMore
                "readMore": None,
                "url": lead["url"], "publishedAt": lead["published"].isoformat(),
                "subtopics": res["subtopics"],
                "sources": [{"name": m["source"], "url": m["url"], "publishedAt": m["published"].isoformat(), "tier": m["tier"]} for m in members],
                "developing": developing,
                "latestUpdate": members[0]["title"] if developing else None,
                "earlier": [{"title": m["title"], "source": m["source"], "publishedAt": m["published"].isoformat()} for m in members[1:6]] if developing else [],
                "isNew": last_brief is None or first_seen > last_brief,
                "score": score, "firstSeen": first_seen.isoformat(),
            }
            story.update({k: v for k, v in res.get("tags", {}).items() if k in ("transfer", "evidence", "matridermRelevant", "kind")})
            if res.get("discovered_competitors"):
                story["mentionedCompanies"] = res["discovered_competitors"]
            vid = next((m for m in members if m.get("video_id")), None)
            if vid:
                story["video"] = {"id": vid["video_id"], "thumbUrl": vid.get("thumb_url"), "duration": durations.get(vid["video_id"]),
                                  "watchUrl": f"https://www.youtube.com/watch?v={vid['video_id']}", "channel": vid["source"]}
            stories.append(story)
            state["seen"][sid] = {"first_seen": first_seen.isoformat(), "last_seen": NOW.isoformat()}
        stories.sort(key=lambda s: (s["score"], s["publishedAt"]), reverse=True)
        feed_out[cat] = stories[:CATEGORY_CAP]

    out = {
        "generatedAt": NOW.isoformat(),
        "windowsDays": CONFIG["windows_days"],
        "tabs": feed_out,
        "health": report,
        "filteredOut": dropped,
    }
    try:  # X leads: discovery only, verified downstream, never shown as facts
        import x_leads
        leads = x_leads.fetch()
        if leads:
            out["leads"] = leads
    except Exception as ex:
        out["xError"] = f"{type(ex).__name__}: {ex}"
    try:  # structured Barcelona data (needs API_FOOTBALL_KEY); skipped cleanly without it
        import barcelona
        bc = barcelona.build(NOW)
        if bc:
            out["barcelona"] = bc
    except Exception as ex:
        out["barcelonaError"] = f"{type(ex).__name__}: {ex}"
    OUT_PATH.write_text(json.dumps(out, ensure_ascii=False, indent=2))

    cutoff = NOW - timedelta(days=60)
    state["seen"] = {k: v for k, v in state["seen"].items() if parse_date(v["last_seen"]) > cutoff}
    state["last_brief"] = NOW.isoformat()
    STATE_PATH.write_text(json.dumps(state, indent=2))

    ok = sum(r["ok"] for r in report)
    print(f"{ok}/{len(report)} feeds ok")
    for r in report:
        print(f"  {'OK ' if r['ok'] else 'ERR'} {r['id']:<22} {r['items']:>3} items  {r['error'] or ''}")
    for cat, s in feed_out.items():
        print(f"{cat:<9} {len(s):>3} stories  ({dropped[cat]} filtered out)")
    required = [r for r, f in zip(report, feeds) if not f.get("optional")]
    return 0 if sum(r["ok"] for r in required) >= len(required) / 2 else 2


if __name__ == "__main__":
    sys.exit(main())
