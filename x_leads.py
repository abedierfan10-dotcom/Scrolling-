"""X (Twitter) as a discovery source only.

Reads recent posts from a public X List (the accounts you follow, put in a list) with an
app-only bearer token. Posts are returned as *leads*: they point at things worth checking
and are never shown as facts. The daily summary step verifies each lead against reputable
journalism or primary sources before anything reaches the feed.

Env: X_BEARER_TOKEN (X API access required, paid), X_LIST_ID.
Without them this returns [] and nothing is invented.
"""
import json
import os
import re
import urllib.parse
import urllib.request

API = "https://api.x.com/2/lists/{id}/tweets"


def _get(url, token):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}", "User-Agent": "ScrollingBriefBot/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read())


def parse(data):
    users = {u["id"]: u for u in data.get("includes", {}).get("users", [])}
    leads = []
    for t in data.get("data", []):
        u = users.get(t.get("author_id"), {})
        links = [x.get("expanded_url") for x in t.get("entities", {}).get("urls", []) if x.get("expanded_url") and "x.com/" not in x["expanded_url"] and "twitter.com/" not in x["expanded_url"]]
        text = re.sub(r"https?://t\.co/\S+", "", t.get("text", "")).strip()
        handle = u.get("username", "unknown")
        leads.append({
            "text": text[:280], "author": handle, "authorName": u.get("name"),
            "postUrl": f"https://x.com/{handle}/status/{t['id']}",
            "postedAt": t.get("created_at"), "links": links,
            "verified": False,  # a post is a lead, not a fact
        })
    return leads


def fetch(get=_get):
    token, list_id = os.environ.get("X_BEARER_TOKEN"), os.environ.get("X_LIST_ID")
    if not token or not list_id:
        return []
    q = urllib.parse.urlencode({"max_results": 100, "tweet.fields": "created_at,author_id,entities", "expansions": "author_id", "user.fields": "username,name"})
    return parse(get(f"{API.format(id=list_id)}?{q}", token))
