"""Editorial rules for Scrolling: what enters each feed, how it is tagged and weighted.

Every function takes a *cluster* (a list of member items about the same story) and
returns None (drop the story) or {"subtopics": [...], "weight": float, "tags": {...}}.
Member items are dicts with: title, summary, source, tier, lang, published, url.

Priorities live in priorities.json / competitors.json so they can be edited without code.
"""
import json
import re
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).parent
P = json.loads((HERE / "priorities.json").read_text())
COMP = json.loads((HERE / "competitors.json").read_text())


# ---------- keyword helpers ----------
@lru_cache(maxsize=None)
def _re(kws: tuple):
    parts = []
    for k in kws:
        if k.endswith("*"):
            parts.append(re.escape(k[:-1]) + r"\w*")
        else:
            parts.append(re.escape(k))
    return re.compile(r"(?<!\w)(?:" + "|".join(parts) + r")(?!\w)", re.I)


def hits(text: str, kws):
    return sorted({m.group(0).lower() for m in _re(tuple(kws)).finditer(text)})


def rx(pattern: str):
    return re.compile(pattern, re.I)


def text_of(members):
    return " ".join(f"{m['title']} {m['summary']}" for m in members)


def best_tier(members):
    return min(m.get("tier", 4) for m in members)


def n_sources(members):
    return len({m["source"] for m in members})


# =====================================================================
# FOOTBALL
# =====================================================================
FB_AVOID = rx(r"\b(gossip|wags?|girlfriend|wife|instagram|tiktok|lookalike|net worth|hot take|opinion|column|verdict|talking points|player ratings|ranked|fans? react|social media|viral|transfer (?:news )?(?:live|round-?up)|rumou?r mill)\b")
FB_MINOR_RUMOUR = rx(r"\b(linked with|eyeing|monitoring|keeping tabs|considering a move|admirers?|on the radar|target(?:s|ed)?)\b")
FB_TRANSFER = rx(r"\b(transfers?|signings?|signs?|signed|loan (?:deal|move)|on loan|release clause|here we go|bids?|contract (?:extension|until|renewal)|extends? (?:his |her )?contract|permanent deal|agreed (?:a )?deal|completes? (?:a )?(?:move|transfer)|transfer fee)\b")
FB_RESULT = rx(r"\b(\d{1,2}\s?[-–]\s?\d{1,2}|beat|beats|defeat|defeated|draw|drew|victory|full[- ]time|match report|hat[- ]trick|wins?|loses?|thrash|stun)\b")
FB_UPCOMING = rx(r"\b(preview|fixtures?|kick[- ]?off|to face|will face|next match|schedule|how to watch|draw for|host|travel to)\b")
FB_LINEUP = rx(r"\b(line[- ]?ups?|starting xi|starting eleven|team news|predicted xi|confirmed xi|aufstellung)\b")
FB_TABLE = rx(r"\b(league table|standings?|top of the table|league leaders|relegation zone|points clear|title race)\b")
FB_UCL_STATUS = rx(r"\bchampions league\b.*\b(standings?|league phase|qualif\w+|knockout|last 16|play-?offs?|table)\b")
FB_FEE = rx(r"[€£$]\s?(\d{2,3})(?:\.\d+)?\s?(?:m\b|million)")
FB_OFFICIAL = rx(r"\b(official(?:ly)?|announce[sd]?|confirm(?:s|ed)?|unveil(?:s|ed)?|completes?|completed|has signed|penned)\b")
FB_HIGHLY = rx(r"\b(here we go|agreement reached|full agreement|verbal agreement|all agreed|medical (?:booked|scheduled|tomorrow))\b")
FB_REPORTED = rx(r"\b(report(?:s|ed)?|according to|understood|set to|close to|expected to|agreed|in talks|negotiat\w+|advanced talks)\b")
SPECIALISTS = {"fabrizio romano", "the athletic", "sky sports", "david ornstein", "gianluca di marzio", "relevo", "mundo deportivo", "sport"}


def transfer_reliability(members):
    """Best available label across all members of the cluster."""
    order = ["RUMOUR", "REPORTED", "HIGHLY RELIABLE", "OFFICIAL"]
    best = "RUMOUR"
    for m in members:
        t = f"{m['title']} {m['summary']}"
        if m.get("tier", 4) == 1 or FB_OFFICIAL.search(t) and m.get("tier", 4) <= 2:
            label = "OFFICIAL"
        elif FB_HIGHLY.search(t) or (m["source"].lower() in SPECIALISTS and FB_REPORTED.search(t)):
            label = "HIGHLY RELIABLE"
        elif FB_REPORTED.search(t) and m.get("tier", 4) <= 4:
            label = "REPORTED"
        else:
            label = "RUMOUR"
        if order.index(label) > order.index(best):
            best = label
    return best


def eval_football(members):
    cfg = P["football"]
    text = text_of(members)
    tier = best_tier(members)
    ents = [e for e in cfg["entities"] if hits(text, e["kw"])]
    barca = any(e.get("barcelona") for e in ents)
    positive = [e for e in ents if e["level"] != "remove"]
    removed = [e for e in ents if e["level"] == "remove"]

    # removed competitions only survive when exceptionally globally significant
    strong = [e for e in positive if e["level"] in ("high", "medium")]
    if removed and not strong and n_sources(members) < cfg["exceptional_sources"]:
        return None
    if not ents:
        return None

    is_transfer = bool(FB_TRANSFER.search(text))
    fee = FB_FEE.search(text)
    fee_m = int(fee.group(1)) if fee else 0
    important_transfer = is_transfer and (barca or any(e["level"] == "high" for e in positive) or fee_m >= 25 or n_sources(members) >= 3)
    if is_transfer and not important_transfer:
        return None  # minor transfer talk never enters the feed

    if FB_AVOID.search(text) and not (barca and n_sources(members) >= 2):
        return None
    if FB_MINOR_RUMOUR.search(text) and is_transfer and not (barca or fee_m >= 40):
        return None

    types = []
    weight = 0.0
    if important_transfer:
        types.append("Transfers"); weight += 2.0
    if FB_LINEUP.search(text):
        if barca:
            types.append("Lineups"); weight += 3.0
        else:
            if not types:
                return None  # lineups matter only for Barcelona
    if FB_RESULT.search(text) and not is_transfer:
        types.append("Results"); weight += 2.0
    if FB_UPCOMING.search(text):
        types.append("Upcoming"); weight += 1.5
    if FB_UCL_STATUS.search(text):
        types.append("UCL status"); weight += 2.0
    if FB_TABLE.search(text):
        types.append("Tables"); weight += 1.5
    if not types:
        if not barca:
            return None  # only the prioritised content types
        weight += 0.5

    top = max(cfg["level_weight"][e["level"]] for e in positive) if positive else 0
    weight += top
    if barca:
        weight += cfg["barcelona_boost"]
    if removed and not strong:
        weight += cfg["level_weight"]["remove"]  # exceptional story: keep but low
    subs = [e["name"] for e in sorted(positive, key=lambda e: {"high": 0, "medium": 1, "low": 2}[e["level"]])][:2]
    tags = {}
    if "Transfers" in types:
        tags["transfer"] = transfer_reliability(members)
    return {"subtopics": subs + types[:1], "weight": weight, "tags": tags, "types": types}


# =====================================================================
# NEWS / POLITICS
# =====================================================================
GEO = {
    "Germany": ["germany", "german", "deutschland", "deutsche*", "bundesregierung", "bundestag", "bundesrat", "berlin", "merz", "bundeskanzler*", "bundesland", "bundesländer", "cdu", "spd", "afd", "grüne", "fdp", "bund"],
    "Hamburg": ["hamburg", "hamburger", "elbe", "hafen", "hafencity", "senat", "bürgerschaft", "tschentscher"],
    "Iran": ["iran", "iranian", "iranische*", "tehran", "teheran", "khamenei", "irgc", "revolutionsgarde"],
    "EU": ["european union", "brussels", "brüssel", "european commission", "eu-kommission", "eurozone", "european parliament", "europäische*", "ecb", "ezb", "von der leyen"],
    "US": ["united states", "usa", "washington", "white house", "weißes haus", "congress", "kongress", "trump", "federal reserve", "pentagon", "supreme court"],
}
GEO_CS = {"US": re.compile(r"\bU\.?S\.?A?\b"), "EU": re.compile(r"\bEU\b")}
NEWS_TOPICS = {
    "high": {
        "Elections": ["election*", "wahl*", "vote", "voters", "ballot", "poll", "umfrage"],
        "Government": ["government", "regierung", "minister*", "parliament", "coalition", "koalition", "chancellor", "kanzler*", "president", "cabinet", "kabinett"],
        "Conflict": ["war", "krieg", "missile*", "ceasefire", "waffenruhe", "airstrike*", "invasion", "sanction*", "sanktion*", "attack", "angriff", "military", "nuclear", "atom*"],
        "Economy": ["economy", "wirtschaft", "inflation", "gdp", "recession", "rezession", "interest rate*", "zinsen", "unemployment", "arbeitslos*", "tariff*", "zoll", "zölle", "haushalt", "budget"],
        "Business": ["company", "unternehmen", "earnings", "merger", "acquisition", "ceo", "insolvenz*", "bankrupt*", "konzern"],
        "Immigration": ["immigration", "migration", "asyl*", "refugee*", "flüchtling*", "deportation*", "abschiebung*", "border"],
        "Markets": ["stocks", "stock market", "börse", "dax", "markets", "bond yields", "oil price", "ölpreis", "shares", "wall street", "bitcoin", "euro"],
    },
    "medium": {
        "Tech & AI": ["technology", "ai", "artificial intelligence", "künstliche intelligenz", "openai", "anthropic", "chip*", "semiconductor*", "cyber*", "software"],
        "Science": ["science", "wissenschaft", "study finds", "researchers", "space", "nasa", "esa", "physics", "discovery"],
        "Law & Policy": ["law", "gesetz*", "court", "gericht*", "ruling", "urteil", "bill", "regulation", "verordnung", "reform"],
    },
    "low": {
        "Healthcare": ["healthcare", "gesundheit*", "hospital", "krankenhaus", "krankenkasse*"],
        "Protests": ["protest*", "demonstration*", "demo", "strike", "streik"],
    },
}
INTL_REL = ["diplomat*", "summit", "gipfel", "talks", "relations", "treaty", "abkommen", "foreign minister", "außenminister*", "un security council"]

HH_CLASSES = {
    "climate": ["klima*", "umwelt*", "climate", "environment*", "emission*", "co2", "naturschutz", "fahrrad*"],
    "crime": ["polizei", "police", "festnahme*", "raub", "überfall", "mord", "crime", "messer*", "diebstahl", "einbruch", "prozess", "angeklagt*", "schüsse", "tatverdächtig*"],
    "accident": ["unfall", "unfälle", "accident", "brand", "feuer", "crash", "collision", "verunglückt", "kollision", "havarie"],
    "social": ["sozial*", "armut", "obdachlos*", "homeless*", "poverty", "kita", "mietpreis*", "wohnungslos*", "sucht", "drogen"],
}
HH_SIGNIFICANT = ["großeinsatz", "großlage", "sperrung", "gesperrt", "evakuier*", "stadtweit", "ganz hamburg", "city-wide", "citywide", "lockdown", "katastrophe", "disaster", "todesopfer", "tote", "stromausfall", "blackout", "unwetterwarnung", "sturmflut", "amok*", "terror*", "stillstand", "major disruption", "hafen gesperrt", "warnstreik", "bürgerschaftswahl"]


def eval_news(members):
    cfg = P["news"]
    text = text_of(members)
    srcs = n_sources(members)
    sig = srcs >= cfg["significant_sources"]

    geos = [g for g, kws in GEO.items() if hits(text, kws)]
    for g, patt in GEO_CS.items():
        if g not in geos and patt.search(text):
            geos.append(g)
    default_geo = members[0].get("geo")
    if default_geo and default_geo not in geos:
        geos.append(default_geo)
    if "Germany" in geos and "Hamburg" in geos:
        geos.remove("Germany")  # Hamburg is the more specific one
    if not geos:
        geos = ["World"]
    geo_w = max(cfg["geo_weight"][g] for g in geos)

    topics, tw = [], 0.0
    for level, groups in NEWS_TOPICS.items():
        for name, kws in groups.items():
            if hits(text, kws):
                topics.append(name)
                tw = max(tw, cfg["topic_weight"][level])
    if "Hamburg" in geos and hits(text, HH_SIGNIFICANT):
        sig = True  # city-wide relevance / major disruption
    intl = bool(hits(text, INTL_REL))
    if intl and not sig:
        tw -= 0.8  # international relations only when particularly significant
    if not topics and not sig:
        return None

    # Hamburg: keep routine local crime, accidents, climate and social items out
    if "Hamburg" in geos:
        dropped = [c for c, kws in HH_CLASSES.items() if hits(text, kws)]
        if dropped and not hits(text, HH_SIGNIFICANT) and not sig:
            return None
    weight = geo_w + tw + (1.0 if sig else 0.0)
    return {"subtopics": geos[:2] + topics[:1], "weight": weight, "tags": {}, "geo": geos}


# =====================================================================
# MEDICAL DEVICES
# =====================================================================
MED_TOPICS = {
    "high": {
        "Wound care": ["wound*", "ulcer*", "negative pressure", "npwt", "dressing*", "chronic wound*"],
        "Reconstructive surgery": ["reconstructive", "reconstruction", "microsurg*", "flap*", "skin graft*", "free flap*"],
        "Plastic surgery": ["plastic surgery", "plastic surgeon*", "aesthetic surgery", "breast reconstruction"],
        "Dermal matrices": ["dermal matri*", "dermal template*", "dermal regeneration", "dermal substitute*", "skin substitute*", "collagen-elastin", "collagen matri*", "biosynthetic matri*"],
        "Regenerative medicine": ["regenerative", "tissue engineering", "tissue regeneration", "stem cell*", "cell therapy", "cultured skin", "bioengineered"],
        "Surgical products": ["surgical", "sutures?", "staplers?", "surgical mesh", "hemostat*", "sealant*", "surgical device*"],
        "Biomaterials": ["biomaterial*", "scaffold*", "hydrogel*", "collagen", "hyaluronic", "polymer*"],
        "Medical aesthetics": ["aesthetic*", "dermal filler*", "botulinum", "energy-based device*", "body contouring", "laser resurfacing"],
        "Cardiovascular": ["cardiovascular", "stent*", "heart valve*", "tavr", "catheter*", "pacemaker*", "cardiac device*", "aortic"],
    },
    "medium": {
        "Burns": ["burn", "burns", "burn injur*", "burn center*", "burn unit*", "scald*"],
        "Hospital technology": ["hospital technolog*", "operating room", "or efficiency", "hospital purchasing", "value analysis"],
        "Surgical robotics": ["surgical robot*", "robotic surgery", "robot-assisted", "da vinci", "hugo ras", "versius", "robotics"],
        "AI & digital health": ["digital health", "ai-enabled", "artificial intelligence", "machine learning", "telehealth", "remote monitoring", "software as a medical device", "samd"],
        "Diagnostics & imaging": ["diagnostic*", "imaging", "mri", "ultrasound", "ct scan*", "in vitro diagnostic*", "ivd"],
    },
    "low": {
        "Orthopaedics": ["orthop*", "knee replacement", "hip replacement", "spine", "implant*"],
        "Dental": ["dental", "dentistry", "orthodont*", "aligner*"],
        "Industry": ["medtech", "medical device*", "medical-device*", "device maker*"],
    },
}
MED_INFO = {
    "high": {
        "Product launch": ["launch*", "unveil*", "introduc*", "new product", "commercial release", "debut*", "cleared for", "now available", "rolls out"],
        "Clinical study": ["clinical study", "clinical trial", "randomi[sz]ed", "rct", "cohort", "meta-analysis", "systematic review", "prospective", "retrospective", "patients"],
        "New technology": ["novel", "first-in-human", "breakthrough", "innovation", "new technology", "3d bioprint*", "bioprint*"],
        "Surgical technique": ["surgical technique", "new technique", "technique for", "approach to reconstruct", "operative technique"],
        "Conference": ["congress", "conference", "symposium", "ewma", "wcw", "annual meeting", "world union of wound healing"],
        "Purchasing": ["hospital purchasing", "group purchasing", "gpo", "tender*", "ausschreibung*", "procurement", "value analysis committee"],
    },
    "medium": {
        "Research": ["study", "research", "journal", "published in", "findings"],
        "Regulatory": ["fda", "510(k)", "premarket", "pma", "de novo", "ce mark", "mdr", "ivdr", "mdcg", "eudamed", "notified body", "regulation (eu)", "clearance", "approval", "approved"],
        "Acquisition": ["acquire*", "acquisition", "merger", "takeover", "buyout", "divest*"],
        "Market": ["market share", "market size", "market trend*", "forecast", "quarterly results", "earnings", "revenue"],
        "Pricing & reimbursement": ["reimbursement", "pricing", "cms", "coverage decision", "dRG", "erstattung*", "ncd", "lcd"],
    },
    "low": {
        "Partnership": ["partnership", "collaborat*", "distribution agreement", "alliance", "licens*"],
        "Funding": ["funding", "raises", "series a", "series b", "series c", "venture", "investment round", "financing"],
    },
    "very_low": {
        "Safety": ["recall*", "safety communication", "field safety", "safety alert", "warning letter", "correction notice", "class ii recall"],
    },
}
MED_MAJOR_SAFETY = rx(r"\b(class i recall|class 1 recall|deaths?|died|fatal\w*|serious (?:injur\w+|adverse)|patient harm|urgent|market withdrawal|stop use|ban(?:ned)?|suspend\w*|halt(?:ed)? (?:sales|distribution))\b")
MED_DERMAL_RESEARCH = ["dermal matri*", "dermal template*", "dermal regeneration", "dermal substitute*", "skin substitute*", "skin substitutes", "wound matri*", "collagen-elastin"]
CANDIDATE_CO = re.compile(r"\b([A-Z][A-Za-z&+\-]{2,}(?: [A-Z][A-Za-z&+\-]{2,}){0,2}) (?:Inc\.?|Ltd\.?|GmbH|Corp\.?|Medical|Therapeutics|Biosciences|Biosurgery|LifeSciences|Surgical|Biologics)\b")


def eval_medical(members, known_competitors=None):
    cfg = P["medical"]
    text = text_of(members)
    known = list(COMP["seed"]) + list(known_competitors or [])
    owner = hits(text, COMP["owner"])
    comps = hits(text, known)
    dermal = hits(text, MED_DERMAL_RESEARCH)

    topics, tw = [], 0.0
    for level, groups in MED_TOPICS.items():
        for name, kws in groups.items():
            if hits(text, kws):
                topics.append(name)
                tw = max(tw, cfg["topic_weight"][level])
    if not topics and not owner and not comps:
        return None  # professional device intelligence, not general health news

    info, iw, info_level = [], None, None
    for level, groups in MED_INFO.items():
        for name, kws in groups.items():
            if hits(text, kws):
                info.append(name)
                if iw is None or cfg["info_weight"][level] > iw:
                    iw, info_level = cfg["info_weight"][level], level
    iw = iw if iw is not None else 0.0

    safety_major = bool(MED_MAJOR_SAFETY.search(text))
    if "Safety" in info and not safety_major and n_sources(members) < 2:
        iw = cfg["info_weight"]["very_low"]
    if "Safety" in info and (safety_major or n_sources(members) >= 2):
        iw = 4.0  # importance overrides normal interest

    weight = tw + iw
    subs = []
    if owner:
        weight += cfg["matriderm_boost"]; subs.append("MatriDerm")
    if comps:
        weight += cfg["competitor_boost"]; subs.append("Competitors")
    if dermal:
        weight += cfg["dermal_research_boost"]
    weight += cfg["tier_bonus"][str(best_tier(members))]
    subs += topics[:2] + [i for i in info if i in ("Clinical study", "Regulatory", "Product launch", "Conference", "Acquisition", "Safety")][:1]
    # dedupe, keep order
    subs = list(dict.fromkeys(subs))

    evidence = {1: "regulator", 2: "peer_reviewed", 3: "society", 4: "company", 5: "trade_press"}[best_tier(members)]
    discovered = sorted({m.group(0) for m in CANDIDATE_CO.finditer(" ".join(f"{m['title']} {m['summary']}" for m in members))}) if (dermal or owner) else []
    return {"subtopics": subs, "weight": weight, "tags": {"evidence": evidence, "matridermRelevant": bool(owner or comps or dermal)},
            "discovered_competitors": discovered}


# =====================================================================
# GROWTH
# =====================================================================
GROWTH_TOPICS = {
    "fast": {
        "AI & smart tools": ["ai", "artificial intelligence", "llm*", "gpt*", "claude", "gemini", "copilot", "agent*", "automation", "automate*", "workflow*", "productivity app*", "no-code", "software", "app that", "tool for", "chatgpt", "prompt*"],
    },
    "core": {
        "Productivity & systems": ["focus", "prioriti*", "routine*", "time management", "deep work", "workflow", "decision system*", "efficien*", "organi[sz]ation", "getting things done", "second brain"],
        "Communication": ["communication", "conversation*", "active listening", "assertive*", "difficult conversation*", "explain*", "feedback", "listening"],
        "Presentation & speaking": ["presentation*", "public speaking", "storytelling", "pitch*", "keynote", "speaking", "talk structure"],
        "Leadership": ["leadership", "leader*", "delegat*", "managing people", "conflict management", "team behaviour", "team behavior", "psychological safety", "management"],
        "Entrepreneurship": ["startup*", "founder*", "entrepreneur*", "product-market fit", "pricing", "business model*", "go-to-market", "sales", "scaling", "validat*"],
        "Business case studies": ["case study", "turnaround", "why .* failed", "competitive advantage", "strategy", "how .* makes money", "business model", "post-mortem", "postmortem"],
        "Personal finance": ["investing", "investor*", "index fund*", "portfolio", "asset allocation", "compounding", "behavioural finance", "behavioral finance", "risk", "long-term invest*", "wealth", "etf"],
        "Psychology": ["psycholog*", "cognitive bias*", "bias", "motivation", "social psychology", "personality", "group dynamics", "behavioural economics", "behavioral economics", "nudge*", "human behaviou?r", "emotion*"],
        "Persuasion & negotiation": ["persuasion", "negotiat*", "framing", "influence", "batna", "leverage", "concession*", "manipulation", "nudge"],
        "Relationships": ["attraction", "dating", "attachment", "relationship*", "boundaries", "conflict", "intimacy", "partner", "romantic"],
        "Social skills": ["networking", "confidence", "first impression*", "social skills", "social awareness", "charisma", "rapport", "small talk"],
        "Behaviour change": ["habit*", "discipline", "behaviou?r change", "environment design", "friction", "self-control", "procrastinat*"],
        "Decision-making": ["mental model*", "decision-making", "decision making", "strategic thinking", "trade-off*", "probabilistic", "judgement", "judgment", "second-order"],
    },
}
GROWTH_AVOID = rx(r"(wake up at 5|5 ?am club|7 habits|seven habits|motivational quote|quotes? (?:to|that|for)|daily motivation|motivation monday|you won'?t believe|this one (?:trick|habit)|shocking|will change your life|life[- ]changing|hustle culture|grindset|sigma|alpha male|red ?pill|pick-?up artist|\bpua\b|gold ?digger|femoid|simp\b|get rich|millionaire (?:habits|mindset)|passive income|guaranteed returns?|100x|to the moon|manifest(?:ation|ing)|law of attraction|10x your|hack(?:s)? that|\d+ (?:habits|things|secrets|rules) (?:of|that|every))")
GROWTH_PSEUDO = rx(r"\b(detox|chakra|astrology|zodiac|manifest\w+|subliminal|biohack\w*|quantum healing|frequency healing)\b")


def eval_growth(members):
    cfg = P["growth"]
    text = text_of(members)
    if GROWTH_AVOID.search(text) or GROWTH_PSEUDO.search(text):
        return None
    topics, kind_weight, fast = [], 0.0, False
    for kind, groups in GROWTH_TOPICS.items():
        for name, kws in groups.items():
            patt = [k for k in kws]
            found = [k for k in patt if re.search(r"(?<!\w)" + (k if any(c in k for c in ".?") else re.escape(k.rstrip("*")) + (r"\w*" if k.endswith("*") else "")) + r"(?!\w)", text, re.I)]
            if found:
                topics.append(name)
                kind_weight = max(kind_weight, cfg["topic_weight"][kind])
                if kind == "fast":
                    fast = True
    if not topics:
        return None
    is_video = any(m.get("kind") == "video" for m in members)
    weight = kind_weight + (cfg["video_bonus"] if is_video else 0.0)
    weight += {2: 0.6, 3: 0.3}.get(best_tier(members), 0.0)
    return {"subtopics": topics[:3], "weight": weight, "tags": {"evergreen": not fast, "kind": "video" if is_video else "article"},
            "window_days": cfg["fast_window_days"] if fast else cfg["evergreen_window_days"]}
