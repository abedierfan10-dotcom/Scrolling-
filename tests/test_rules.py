"""Rule tests: run `python3 tests/test_rules.py` (no network needed)."""
import sys, json
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import rules, barcelona

NOW = datetime.now(timezone.utc)
def m(title, summary="", source="BBC Sport", tier=2, **kw):
    d = dict(title=title, summary=summary, source=source, tier=tier, lang="en", published=NOW, url="u"); d.update(kw); return d

fails = []
def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond: fails.append(name)

# ---- football
f = rules.eval_football
check("barca result kept, strongly weighted", (r := f([m("Barcelona beat Girona 3-1 in La Liga")])) and r["weight"] > 10 and "Results" in r["types"])
check("ligue 1 dropped", f([m("PSG beat Lyon 2-0 in Ligue 1")]) is None)
check("england NT dropped", f([m("England national team beat Serbia 2-0")]) is None)
check("removed league survives only if exceptional", f([m("Ligue 1 title decided 2-1", source=s) for s in ["BBC", "ESPN", "Sky", "Guardian"]]) is not None)
check("celebrity gossip dropped", f([m("Barcelona star's girlfriend Instagram post goes viral")]) is None)
check("minor transfer rumour dropped", f([m("Bournemouth linked with Norwich winger", "Serie A side monitoring")]) is None)
r = f([m("Barcelona sign midfielder: club announce official signing", "Barcelona have announced the signing", source="FC Barcelona", tier=1)])
check("official barca transfer -> OFFICIAL", r and r["tags"].get("transfer") == "OFFICIAL")
r = f([m("Barcelona close to €60m deal for striker, here we go", source="Fabrizio Romano", tier=3)])
check("here we go -> HIGHLY RELIABLE", r and r["tags"].get("transfer") == "HIGHLY RELIABLE")
r = f([m("Barcelona in talks over bid for defender, reports say")])
check("reports -> REPORTED", r and r["tags"].get("transfer") == "REPORTED")
r = f([m("Barcelona could be interested in a bid for winger", "Barcelona considering a move", source="Barca Blaugranes", tier=4)])
check("speculative important -> RUMOUR", r and r["tags"].get("transfer") == "RUMOUR")
check("non-barca lineup dropped", f([m("Arsenal starting XI vs Chelsea", "Premier League team news")]) is None)
check("barca lineup kept", (r := f([m("Barcelona starting XI vs Girona: team news", "La Liga")])) and "Lineups" in r["types"])
check("unlisted league dropped", f([m("Eredivisie: Ajax beat Feyenoord 2-1")]) is None)
check("premier league result kept, weighted below barca", (a := f([m("Arsenal beat Spurs 2-1 in the Premier League")])) and a["weight"] < 8)

# ---- news
n = rules.eval_news
check("hamburg routine crime dropped", n([m("Polizei nimmt Tatverdächtigen nach Diebstahl in Hamburg fest", source="NDR", geo="Hamburg", lang="de")]) is None)
check("hamburg accident dropped", n([m("Unfall auf der A7 bei Hamburg: zwei Verletzte", source="NDR", geo="Hamburg")]) is None)
check("hamburg major disruption kept", n([m("Hamburg: Sperrung des Hafens nach Sturmflut, S-Bahn Stillstand", source="NDR", geo="Hamburg")]) is not None)
check("hamburg politics kept, hamburg tagged", (r := n([m("Hamburger Senat beschließt Haushalt", source="NDR", geo="Hamburg")])) and "Hamburg" in r["subtopics"])
check("germany outranks world for same topic", n([m("Bundestag debattiert Haushalt", geo="Germany")])["weight"] > n([m("Parliament debates budget in Peru")])["weight"])
check("celebrity fluff dropped", n([m("Popstar shows off new hairstyle")]) is None)
check("iran conflict kept", (r := n([m("Iran missile attack raises war fears")])) and "Iran" in r["subtopics"])
check("'us' pronoun is not US", "US" not in n([m("Tell us about the election results")])["subtopics"])

# ---- medical
md = rules.eval_medical
check("matriderm mention boosted", (r := md([m("MatriDerm study shows dermal regeneration in burns", source="PubMed", tier=2)])) and r["weight"] > 10 and "MatriDerm" in r["subtopics"])
check("competitor tagged", (r := md([m("PolyNovo NovoSorb BTM launches new dermal template", tier=5)])) and "Competitors" in r["subtopics"])
check("general health news dropped", md([m("Study links coffee to longer life")]) is None)
check("routine recall very low", (a := md([m("Company announces recall of surgical stapler", tier=5)])) and a["weight"] < md([m("New surgical stapler launch", tier=5)])["weight"])
check("major safety overrides", (r := md([m("Class I recall of cardiac catheter after patient deaths", tier=1)])) and r["weight"] > 3)
check("company source flagged as company", md([m("Acme launches new wound dressing", source="Acme", tier=4)])["tags"]["evidence"] == "company")
check("regulator evidence", md([m("FDA clears dermal matrix for burns", source="FDA", tier=1)])["tags"]["evidence"] == "regulator")
check("dermal research beats orthopaedics", md([m("New dermal matrix trial for chronic wounds", tier=2)])["weight"] > md([m("Knee implant sales up", tier=5)])["weight"])

# ---- growth
g = rules.eval_growth
check("motivational cliche dropped", g([m("Wake up at 5 AM: the habit of successful people")]) is None)
check("get-rich dropped", g([m("Passive income to get rich fast investing")]) is None)
check("red-pill dating dropped", g([m("Alpha male dating tactics that work")]) is None)
check("negotiation kept, evergreen", (r := g([m("How BATNA changes salary negotiation outcomes")])) and r["tags"]["evergreen"] and "Persuasion & negotiation" in r["subtopics"])
check("AI tools is fast-changing (7d window)", (r := g([m("New AI agent tool automates your workflow")])) and r["window_days"] == 7)
check("video bonus", g([m("How to negotiate a raise", kind="video")])["weight"] > g([m("How to negotiate a raise")])["weight"])
check("off-topic dropped", g([m("Local bakery wins award")]) is None)

# ---- barcelona parsing (documented API-Football shapes, mock data)
fx = {"fixture": {"id": 1, "date": "2026-09-27T19:00:00+00:00", "venue": {"name": "Spotify Camp Nou", "city": "Barcelona"}},
      "league": {"name": "La Liga"}, "teams": {"home": {"id": 529, "name": "Barcelona"}, "away": {"id": 9, "name": "Girona"}}, "goals": {"home": 3, "away": 1}}
p = barcelona.parse_fixture(fx)
check("fixture parse", p["opponent"] == "Girona" and p["home"] and p["score"] == {"for": 3, "against": 1} and "Camp Nou" in p["venue"])
st = barcelona.parse_stats([{"team": {"id": 529}, "statistics": [{"type": "Ball Possession", "value": "61%"}, {"type": "Total Shots", "value": 17}, {"type": "expected_goals", "value": "2.31"}]}])
check("stats parse", st["possession"] == 61.0 and st["shots"] == 17 and st["xg"] == 2.31)
check("scorers parse", barcelona.parse_scorers([{"type": "Goal", "detail": "Normal Goal", "team": {"id": 529}, "player": {"name": "Yamal"}, "time": {"elapsed": 12}}])[0]["minute"] == 12)
check("lineup none when absent", barcelona.parse_lineup([{"team": {"id": 529}, "startXI": []}]) is None)
check("standing parse", barcelona.parse_standing([{"league": {"standings": [[{"rank": 3, "team": {"id": 529}, "points": 14, "all": {"played": 6}, "form": "WWDLW"}, {"rank": 1, "team": {"id": 1}, "points": 18, "all": {"played": 6}}]]}}])["pos"] == 3)

import x_leads
ld = x_leads.parse({"data": [{"id": "1", "author_id": "9", "text": "Big story https://t.co/abc", "created_at": "2026-09-20T10:00:00Z", "entities": {"urls": [{"expanded_url": "https://example.com/a"}, {"expanded_url": "https://x.com/i/status/1"}]}}], "includes": {"users": [{"id": "9", "username": "reporter", "name": "R"}]}})
check("x lead parsed, unverified, no x links", ld[0]["verified"] is False and ld[0]["links"] == ["https://example.com/a"] and ld[0]["text"] == "Big story")
check("x without token returns nothing", x_leads.fetch() == [])

print("\n%d failed" % len(fails)); sys.exit(1 if fails else 0)
