"""Structured Barcelona data from a licensed football API (API-Football v3).

Needs env API_FOOTBALL_KEY. Returns None without it, so the app shows its
"unavailable" states instead of guessing. FotMob and other sources whose terms
forbid automated access are deliberately not used.

Endpoints used (API-Football v3, header x-apisports-key):
  /fixtures?team=529&next=1 | &last=1   next and last Barcelona fixture
  /fixtures/events|statistics|lineups?fixture=ID
  /standings?league=140&season=YYYY     La Liga
  /standings?league=2&season=YYYY       Champions League
Roughly 9 requests per run. Field names follow the public API-Football v3 docs;
run once with a real key and check the output before relying on it.
"""
import json
import os
import urllib.parse
import urllib.request

BASE = "https://v3.football.api-sports.io"
TEAM = 529      # FC Barcelona
LALIGA = 140
UCL = 2


def _get(path, params):
    key = os.environ.get("API_FOOTBALL_KEY")
    req = urllib.request.Request(f"{BASE}{path}?{urllib.parse.urlencode(params)}", headers={"x-apisports-key": key})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read())


def season_for(now):
    return now.year if now.month >= 7 else now.year - 1


def _num(v):
    if v is None:
        return None
    try:
        return float(str(v).rstrip("%"))
    except ValueError:
        return None


def parse_fixture(fx, team_id=TEAM):
    home = fx["teams"]["home"]["id"] == team_id
    opp = fx["teams"]["away" if home else "home"]["name"]
    return {
        "id": fx["fixture"]["id"],
        "opponent": opp,
        "competition": fx.get("league", {}).get("name"),
        "kickoff": fx["fixture"]["date"],
        "venue": ", ".join(x for x in [fx["fixture"].get("venue", {}).get("name"), fx["fixture"].get("venue", {}).get("city")] if x) or None,
        "home": home,
        "score": None if fx["goals"]["home"] is None else {"for": fx["goals"]["home" if home else "away"], "against": fx["goals"]["away" if home else "home"]},
    }


def parse_stats(resp, team_id=TEAM):
    for block in resp:
        if block["team"]["id"] != team_id:
            continue
        s = {x["type"]: x["value"] for x in block["statistics"]}
        return {"possession": _num(s.get("Ball Possession")), "shots": s.get("Total Shots"),
                "shotsOnTarget": s.get("Shots on Goal"), "xg": _num(s.get("expected_goals"))}
    return {}


def parse_scorers(resp, team_id=TEAM):
    return [{"player": e["player"]["name"], "minute": e["time"]["elapsed"]}
            for e in resp if e.get("type") == "Goal" and e["team"]["id"] == team_id and e.get("detail") != "Missed Penalty"]


def parse_lineup(resp, team_id=TEAM):
    for block in resp:
        if block["team"]["id"] == team_id and block.get("startXI"):
            return {"formation": block.get("formation"),
                    "startXI": [{"name": p["player"]["name"], "number": p["player"].get("number"), "pos": p["player"].get("pos")} for p in block["startXI"]]}
    return None


def parse_standing(resp, team_id=TEAM):
    rows = resp[0]["league"]["standings"]
    rows = [r for grp in rows for r in grp]
    for r in rows:
        if r["team"]["id"] == team_id:
            return {"pos": r["rank"], "of": len(rows), "points": r["points"], "played": r["all"]["played"], "form": r.get("form")}
    return None


def build(now, get=_get):
    if not os.environ.get("API_FOOTBALL_KEY") and get is _get:
        return None
    season = season_for(now)
    out = {}
    nxt = get("/fixtures", {"team": TEAM, "next": 1})["response"]
    lst = get("/fixtures", {"team": TEAM, "last": 1})["response"]
    la = get("/standings", {"league": LALIGA, "season": season})["response"]
    uc = get("/standings", {"league": UCL, "season": season})["response"]
    out["laLiga"] = parse_standing(la) if la else None
    out["ucl"] = parse_standing(uc) if uc else None
    form = (out["laLiga"] or {}).get("form")
    if nxt:
        n = parse_fixture(nxt[0])
        n["form"] = form
        n["position"] = (out["laLiga"] or {}).get("pos")
        lu = get("/fixtures/lineups", {"fixture": n["id"]})["response"]
        out["nextMatch"] = n
        out["lineup"] = parse_lineup(lu)          # None until the club announces it (about an hour before kickoff)
    if lst:
        l = parse_fixture(lst[0])
        l.update(parse_stats(get("/fixtures/statistics", {"fixture": l["id"]})["response"]))
        l["scorers"] = parse_scorers(get("/fixtures/events", {"fixture": l["id"]})["response"])
        out["lastMatch"] = l
    return {k: v for k, v in out.items() if v}
