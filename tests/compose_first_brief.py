"""One-off: the first real brief (20 Sep 2026), composed by hand from fetched pages.
Writes the per-document JSON files that go into the artifact db. Every fact below
was read from a page fetched on 20 Sep 2026; nothing is inferred except where a
line says so."""
import json, os, sys, datetime as dt
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
NOW = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()

def src(name, url, iso, tier): return {"name": name, "url": url, "publishedAt": iso, "tier": tier}
def story(cat, n, lang, title, summary, url, iso, subs, sources, score, **kw):
    s = {"id": f"2026-09-20-{cat}-{n}", "category": cat, "lang": lang, "title": title, "summary": summary, "url": url,
         "publishedAt": iso, "subtopics": subs, "sources": sources, "developing": False, "latestUpdate": None, "earlier": [],
         "isNew": True, "score": score, "firstSeen": iso}
    s.update(kw); return s

# ---------------- FOOTBALL ----------------
GOAL = "https://www.goal.com/en-us/team/barcelona/fixtures-results/agh9ifb2mw3ivjusgedj7c3fe"
GG = "https://www.101greatgoals.com/football/la-liga/sevilla-barcelona-result-report-goals/"
LL = "https://www.laliga.com/en-GB/laliga-easports/standing"
SKYLL = "https://www.skysports.com/la-liga"
AJ = "https://www.aljazeera.com/sports/liveblog/2026/9/20/live-atletico-madrid-vs-real-madrid-la-liga-2"
VV = "https://www.vavel.com/en-us/soccer/2026/09/20/1272224-atletico-madrid-vs-real-madrid-live-updates-laliga.html"
LLN = "https://www.laliga.com/en-GB/clubs/fc-barcelona/next-matches"
BL = "https://www.bundesliga.com/en/bundesliga/matchday"
SKYRSS = "https://www.skysports.com/rss/12040"
football = [
 story("football", 1, "en", "Raphinha hat-trick as Barcelona win 3–1 at Sevilla to stay perfect",
  "Barcelona came from behind after Fofana's 19th-minute opener, with Raphinha scoring in the 22nd, 52nd and 69th minutes. It is their seventh league win in seven and leaves them six points clear of Real Madrid.",
  GG, "2026-09-19T18:00:00+00:00", ["Barcelona", "Results", "La Liga"],
  [src("101 Great Goals", GG, "2026-09-19T18:00:00+00:00", 4), src("Goal", GOAL, "2026-09-19T18:00:00+00:00", 4), src("LaLiga", LL, "2026-09-20T12:00:00+00:00", 1), src("Sky Sports", SKYLL, "2026-09-20T12:00:00+00:00", 2)],
  17.5,
  readMore={"keyPoints": [
    "Youssouf Fofana put Sevilla ahead in the 19th minute; Raphinha equalised in the 22nd and added goals in the 52nd and 69th.",
    "The match report calls it Raphinha's second successive hat-trick; Barcelona beat Racing Santander 7–2 on 16 September.",
    "Barcelona had 69% possession and 24 shots (7 on target) against Sevilla's 7 (3), per one match report.",
    "League table: 7 wins from 7, 31 goals for and 7 against, 21 points. Real Madrid have 15."],
   "why": "Barcelona lead La Liga by six points after seven matchdays. The possession and shot numbers come from a single report and are not confirmed elsewhere."}),
 story("football", 2, "en", "Atlético beat ten-man Real Madrid 2–1 in the derby",
  "Atlético Madrid won the Madrid derby 2–1 with Real Madrid reduced to ten men, according to Al Jazeera's live-blog headline and VAVEL's highlights title. Scorers and the sending-off are not confirmed here.",
  AJ, "2026-09-20T16:00:00+00:00", ["La Liga", "Real Madrid", "Results"],
  [src("Al Jazeera", AJ, "2026-09-20T16:00:00+00:00", 2), src("VAVEL", VV, "2026-09-20T16:00:00+00:00", 4)],
  9.4,
  readMore={"keyPoints": [
    "Both headlines give the score as Atlético 2, Real Madrid 1; the Al Jazeera headline says Real finished with ten men and calls the derby stormy.",
    "The league table read before the match showed Real Madrid second on 15 points, Barcelona first on 21.",
    "Goalscorers, minutes and the red-card details could not be retrieved."],
   "why": "On the table read before the match, Barcelona lead Real Madrid by six points (21 v 15), and a Real defeat leaves that gap unchanged. El Clásico is at Camp Nou on 25 October."}),
 story("football", 3, "en", "Barcelona's next five: Getafe, then Galatasaray, Betis, PSG and Real Madrid",
  "LaLiga's fixture list has Barcelona at home to Getafe on 10 October, away at Galatasaray in the Champions League on 13 October, at Real Betis on 17 October, away at PSG on 20 October, then home to Real Madrid on 25 October.",
  LLN, "2026-09-20T12:00:00+00:00", ["Barcelona", "Fixtures", "Champions League"],
  [src("LaLiga", LLN, "2026-09-20T12:00:00+00:00", 1), src("Goal", GOAL, "2026-09-20T12:00:00+00:00", 4)],
  11.2,
  readMore={"keyPoints": [
    "10 Oct: Barcelona v Getafe (LaLiga, Spotify Camp Nou).",
    "13 Oct: Galatasaray v Barcelona (Champions League).",
    "17 Oct: Real Betis v Barcelona (LaLiga). Betis are third in the table.",
    "20 Oct: PSG v Barcelona (Champions League).",
    "25 Oct: Barcelona v Real Madrid (LaLiga, Spotify Camp Nou)."],
   "why": "Nothing is scheduled between now and 10 October. Kickoff times differ between LaLiga and Goal, so only dates are shown."}),
 story("football", 4, "en", "Dortmund win again for a perfect 12 points; Bayern rout Union 7–0",
  "After Bundesliga matchday 4, Dortmund lead the table for the first time since 2023 with four wins from four. Bayern beat Union Berlin 7–0 and Hamburger SV won 2–1 against Cologne.",
  BL, "2026-09-19T20:00:00+00:00", ["Bundesliga", "Results"],
  [src("Bundesliga", BL, "2026-09-20T12:00:00+00:00", 1)],
  4.8,
  readMore={"keyPoints": [
    "Stuttgart 0–1 Dortmund: Dortmund's best start in 11 years, per the Bundesliga site.",
    "Bayern Munich 7–0 Union Berlin (Friday). Hamburger SV 2–1 Cologne (Saturday).",
    "Also Saturday: Bremen 3–2 Augsburg, Gladbach 3–4 Mainz, Frankfurt 2–2 Freiburg.",
    "Leverkusen v Leipzig, Schalke v Elversberg and Paderborn v Hoffenheim were still to be played when the page was read."],
   "why": "The page did not include a full table, so the order behind Dortmund is not shown."}),
 story("football", 5, "en", "Man City go top after an eight-goal win over Sunderland; Liverpool stay unbeaten",
  "Manchester City beat Sunderland 5–3 on Sunday, and Sky Sports says they go top. Liverpool won 1–0 at Bournemouth through an Alexander Isak goal and keep their unbeaten start.",
  SKYRSS, "2026-09-20T15:35:00+00:00", ["Premier League", "Results"],
  [src("Sky Sports", SKYRSS, "2026-09-20T15:35:00+00:00", 2)],
  3.9,
  readMore={"keyPoints": [
    "Manchester City 5–3 Sunderland: the Sky Sports report headline calls it an eight-goal thriller.",
    "Bournemouth 0–1 Liverpool: Isak scored the winner on Andoni Iraola's return to Bournemouth.",
    "Crystal Palace drew 0–0 at unbeaten Leeds."],
   "why": "Only feed headlines and one-line descriptions were read, not the full reports."}),
]

barcelona = {
  "asOf": NOW,
  "nextMatch": {"opponent": "Getafe", "competition": "LaLiga", "kickoff": "2026-10-10", "venue": "Spotify Camp Nou", "home": True, "form": "WWWWW"},
  "lastMatch": {"opponent": "Sevilla", "competition": "LaLiga", "home": False, "score": {"for": 3, "against": 1},
                "scorers": [{"player": "Raphinha", "minute": 22}, {"player": "Raphinha", "minute": 52}, {"player": "Raphinha", "minute": 69}],
                "possession": 69, "shots": 24, "xg": None},
  "laLiga": {"pos": 1, "of": 20, "points": 21, "played": 7},
  "ucl": {"points": 3, "played": 1},
}

# ---------------- NEWS ----------------
ZDF_LIST = "https://www.zdfheute.de/politik/deutschland/wahl-berlin-landtagswahl-mecklenburg-vorpommern-prognose-hochrechnung-ergebnisse-liveticker-102.html"
ZDF_MV = "https://www.zdfheute.de/politik/deutschland/landtagswahl-mecklenburg-vorpommern-wahlergebnisse-afd-spd-holm-schwesig-100.html"
ZDF_BE = "https://www.zdfheute.de/politik/deutschland/wahl-berlin-wahlergebnisse-cdu-die-linke-evers-eralp-100.html"
ZDF_MERZ = "https://www.zdfheute.de/politik/deutschland/merz-kanzler-wahlen-berlin-mecklenburg-vorpommern-statement-cdu-regierung-100.html"
ZDF_MOS = "https://www.zdfheute.de/politik/ausland/moskau-angriff-parlamentswahl-ukraine-krieg-russland-100.html"
IRINT = "https://www.iranintl.com/en/liveblog/202609196155"
EURON = "https://www.euronews.com/my-europe/2026/09/16/ursula-von-der-leyen-delivers-state-of-the-union-speech"
BNN = "https://www.bnnbloomberg.ca/business/economics/2026/09/16/us-federal-reserve-hikes-key-rate-for-1st-time-in-3-years-defying-trump-demands-for-a-cut/"
FIN = "https://www.finanzen.at/nachrichten/aktien/ezb-erhoeht-die-zinsen-dax-bricht-25500-nasdaq-vor-29000!-1036537500"
WIKI = "https://en.wikipedia.org/wiki/2026_Iran_war"

news = [
 story("news", 1, "de", "Landtagswahlen: AfD knapp vor SPD in Mecklenburg-Vorpommern, Linke klar vorn in Berlin",
  "Laut Prognose von ZDFheute liegt in Mecklenburg-Vorpommern die AfD mit 38,0 Prozent knapp vor der SPD mit 36,5 Prozent. In Berlin führt die Linke mit 26 Prozent vor der CDU mit 20 Prozent. Es sind Prognosen und Hochrechnungen, kein Endergebnis.",
  ZDF_LIST, "2026-09-20T16:31:00+00:00", ["Germany", "Politics", "Elections"],
  [src("ZDFheute", ZDF_MV, "2026-09-20T16:31:00+00:00", 2), src("ZDFheute", ZDF_BE, "2026-09-20T16:31:00+00:00", 2), src("ZDFheute", ZDF_MERZ, "2026-09-20T16:26:00+00:00", 2)],
  19.0, developing=True, latestUpdate="Prognose und Hochrechnungen vom Wahlabend, 20.09.2026 gegen 18:30 Uhr",
  earlier=[{"title": "Hält Merz dem Druck stand?", "source": "ZDFheute", "publishedAt": "2026-09-17T14:35:00+00:00"}],
  en={"title": "State elections: AfD narrowly ahead of SPD in Mecklenburg-Vorpommern, Left clearly ahead in Berlin",
      "summary": "ZDFheute's forecast puts the AfD on 38.0% in Mecklenburg-Vorpommern, just ahead of the SPD on 36.5%. In Berlin the Left leads on 26% ahead of the CDU on 20%. These are forecasts and projections, not final results."},
  readMore={
   "why": "Zwei Landtagswahlen am selben Tag gelten als Test für Bundeskanzler Merz. Nach dem Absturz der CDU bei der Wahl in Sachsen-Anhalt vor zwei Wochen war die Kritik in der Partei lauter geworden.",
   "happened": [
     "In Mecklenburg-Vorpommern sieht die Prognose der Forschungsgruppe Wahlen die AfD (Spitzenkandidat Leif-Erik Holm) bei 38,0 Prozent und die SPD von Ministerpräsidentin Manuela Schwesig bei 36,5 Prozent. Die Linke kommt auf 6,0, die Grünen auf 5,5, die CDU auf 5,0 und das BSW auf 4,8 Prozent.",
     "In Berlin liegt die Linke (Elif Eralp) laut Hochrechnung bei 26 Prozent und 37 Sitzen, die CDU (Stefan Evers) bei 20 Prozent und 28 Sitzen. Es folgen Grüne 15,5, AfD 13,5, SPD 12 und BSW 5 Prozent.",
     "Bundeskanzler Merz sagte, die Regierung wolle den Reformkurs fortsetzen: „Die Reformen müssen kommen.“"],
   "background": "In Mecklenburg-Vorpommern hatte die SPD 2021 noch 39,6 Prozent erreicht, die AfD 16,7 Prozent. Erstmals durften Wähler ab 16 abstimmen; rund 1,3 Millionen Menschen waren wahlberechtigt. In Berlin tritt der Regierende Bürgermeister Kai Wegner (CDU) nicht erneut an. Die SPD droht dort mit 12 Prozent deutlich unter ihr Ergebnis von 2023 (18,4 Prozent) zu fallen.",
   "sides": [
     {"who": "Bundeskanzler Merz (CDU)", "view": "Deutschland sei reformfähig; die Reformen müssten kommen. Er beklagte einen raueren Ton in der Gesellschaft und warnte vor sinkendem Vertrauen in Institutionen durch radikale Parteien."},
     {"who": "Parteien in Berlin", "view": "Die CDU lehnt eine Koalition mit der Linken ab; alle Parteien schließen eine Zusammenarbeit mit der AfD aus (laut ZDFheute)."}],
   "confirmed": ["Die genannten Zahlen stammen aus der Prognose der Forschungsgruppe Wahlen und aus ZDF-Hochrechnungen vom Wahlabend."],
   "uncertain": [
     "Das Endergebnis steht noch aus; in Mecklenburg-Vorpommern liegen CDU, Grüne und BSW nahe an der Fünf-Prozent-Hürde.",
     "In Berlin sind nach der Hochrechnung nur zwei Dreierbündnisse rechnerisch möglich: Linke, Grüne und SPD (76 von 130 Sitzen) oder CDU, Grüne und SPD (67 Sitze); für die Mehrheit sind 66 Sitze nötig."],
   "keyPoints": ["Mecklenburg-Vorpommern: Kopf-an-Kopf-Rennen zwischen AfD und SPD.", "Berlin: Linke deutlich vor der CDU, die SPD auf Tiefstand.", "Merz hält am Reformkurs fest."]}),
 story("news", 2, "en", "Iran's parliament speaker: fight and negotiate at the same time, as MPs raise leaving the NPT",
  "Speaker Mohammad-Bagher Ghalibaf said Iran should fight 'rationally and forcefully' and negotiate 'at the appropriate time'. One MP called for leaving the NPT, and a committee chair warned the IAEA of 'serious and regrettable responses', per Iran International's live blog.",
  IRINT, "2026-09-20T09:00:00+00:00", ["Iran", "Iran war", "Nuclear"],
  [src("Iran International", IRINT, "2026-09-20T09:00:00+00:00", 4), src("Wikipedia (background only)", WIKI, "2026-09-20T09:00:00+00:00", 5)],
  13.0, developing=True, latestUpdate="Live blog of 19–20 September: statements on talks, the NPT and the Strait of Hormuz",
  readMore={
   "why": "Iran's stance on talks and on the NPT bears on whether the war escalates again. The war's oil-price shock is the reason the ECB gave for its latest rate rise.",
   "happened": [
     "Ghalibaf said Iran should pursue both approaches at once, criticising unconditional warfare that rejects diplomacy and appeasement that gives up national interests.",
     "A lawmaker argued that staying in the NPT 'produces nothing but harm'. The chair of parliament's national-security committee warned the IAEA of 'serious and regrettable responses' if it continued alleged one-sided conduct, and cautioned Oman against delaying negotiations over the Strait of Hormuz.",
     "Security official Mohsen Rezaei said Tehran remains committed to the late supreme leader's ban on nuclear weapons but added, 'we do not know what will happen in the future'. The IRGC deputy commander said the strait remains under the armed forces' control. Trump cut short a Camp David stay while the US weighs its next step; no details were given."],
   "background": "Per Wikipedia's summary (background only, not a primary source): the war began on 28 February 2026 with US-Israeli strikes that killed Ali Khamenei. A two-week ceasefire started on 8 April, talks in Islamabad failed on 12–13 April, a memorandum on 17 June lifted the dual blockades, and the ceasefire collapsed on 8 July. Iran has claimed control of the Strait of Hormuz.",
   "sides": [
     {"who": "Ghalibaf (Parliament Speaker)", "view": "Fight forcefully and negotiate from a position of authority; reject both extremes."},
     {"who": "Hardline MPs", "view": "One lawmaker called for NPT withdrawal; the security-committee chair threatened the IAEA."},
     {"who": "Mohsen Rezaei", "view": "Committed to the nuclear-weapons ban for now, with no promise for the future."}],
   "confirmed": ["These are statements reported by Iran International, an outlet based outside Iran. They show what officials said, not what will happen."],
   "uncertain": ["Whether parliament will act on NPT withdrawal.", "When and through whom talks resume; Oman is named as an intermediary.", "What the US will do next."],
   "keyPoints": ["Two-track message from the parliament speaker: fight and negotiate.", "NPT withdrawal is being openly discussed by MPs.", "Strait of Hormuz talks via Oman are unresolved."]}),
 story("news", 3, "en", "Von der Leyen's State of the Union: European Security Council, a hybrid-attack mechanism and an EU Kids Act",
  "On 16 September the Commission President proposed a European Security Council including Ukraine, the UK, Norway and Canada, and an 'Article 4'-style mechanism for hybrid attacks. She also announced a social-media age limit proposal, a heatwave plan and associate membership for Canada.",
  EURON, "2026-09-16T12:00:00+00:00", ["EU", "Politics", "Security"],
  [src("Euronews", EURON, "2026-09-16T12:00:00+00:00", 2)],
  12.5,
  readMore={
   "why": "The speech sets the Commission's agenda for the coming year and touches Germany directly through defence funding, migration rules and the 2028–2034 budget talks.",
   "happened": [
     "Security: a European Security Council with Ukraine, the UK, Norway and Canada; a new 'Article 4' mechanism to coordinate the EU response to hybrid attacks; unspent defence loans to fund joint European-Ukrainian projects including the Freyja missile system.",
     "Migration: a 'European Emergency Response Framework' for mass arrivals, giving temporary procedural flexibility, plus a stronger role for Frontex in border management and returns.",
     "Digital and AI: an EU Kids Act to restrict under-15s and ban under-13s from social media, with platforms bearing the burden of proof. She called for pacing frontier AI development and proposed industrial AI projects in five sectors.",
     "Climate: a European Heatwave Plan and a Climate Insurance Alliance (about 25% of catastrophe losses are insured today), and a water initiative. Canada was invited to become the EU's first 'associate member'."],
   "sides": [
     {"who": "EPP", "view": "Backs a stronger EU budget and opposes the combustion-engine ban."},
     {"who": "S&D", "view": "Wants a windfall tax on energy companies to fund social support."},
     {"who": "Greens", "view": "Demand climate-adaptation funding and an inquiry into Green Deal enforcement."},
     {"who": "Patriots", "view": "Want European preference in public procurement and criticise migration handling."}],
   "confirmed": ["The announcements above are as reported by Euronews; they are proposals, not adopted law."],
   "uncertain": ["The EU Kids Act text was due later in the week and was not read.", "A von der Leyen–Carney summit is planned for October in Montreal; long-term budget talks are meant to conclude by year-end."],
   "keyPoints": ["Security council and hybrid-attack mechanism.", "Under-15 social-media restriction proposed.", "Canada offered associate membership."]}),
 story("news", 4, "en", "Fed raises rates for the first time in three years, defying Trump",
  "The Federal Reserve raised its benchmark rate by a quarter point on 16 September, to roughly 3.75–4%. All policymakers backed the move, announced by Chair Kevin Warsh, and President Trump called the board 'very hostile'.",
  BNN, "2026-09-16T19:00:00+00:00", ["US", "Economy", "Markets"],
  [src("BNN Bloomberg", BNN, "2026-09-16T19:00:00+00:00", 2), src("finanzen.at", FIN, "2026-09-10T12:00:00+00:00", 4)],
  10.5,
  readMore={
   "why": "US and euro-area central banks are both tightening because of the oil-price shock, which affects mortgages, exchange rates and the DAX.",
   "happened": [
     "The Fed lifted its rate by 0.25 points to about 3.9% (the CNBC headline gives 3.75–4%). Projections point to a possible second increase to 4.1% this year. The vote was unanimous; in July three officials had dissented in favour of higher rates.",
     "Inflation was 3.7% in July and core inflation 3.3%. Gas prices rose more than 7% in recent weeks because of the US-Iran conflict. Two-year Treasury yields rose to 4.74% from 4.67%."],
   "background": "The ECB also raised its deposit rate, from 2.25% to 2.50%, citing the oil-price shock from the Iran war, according to finanzen.at; the DAX fell below 25,500 that day. The article's headline and URL are dated 10 September while one line in the text says 18 September, so the exact day is not confirmed.",
   "sides": [
     {"who": "Federal Reserve", "view": "Inflation is well above the 2% target and demand is strong, so rates are not yet restrictive enough."},
     {"who": "President Trump", "view": "Said 'the board is very hostile. They're very political' and accused policymakers of acting to damage him politically."}],
   "confirmed": ["Quarter-point increase, unanimous vote, Kevin Warsh announcing (BNN Bloomberg)."],
   "uncertain": ["The next meeting is in late October and is likely to leave rates unchanged given the proximity of the midterms; futures price a December hike.", "The exact date of the ECB decision."],
   "keyPoints": ["First Fed hike in three years.", "Inflation 3.7% in July.", "ECB has also raised rates; exact date unclear."]}),
 story("news", 5, "de", "Ukrainischer Drohnenangriff auf Moskau überschattet Russlands Parlamentswahl",
  "Nach russischen Angaben wurden mehr als 1.600 Drohnen abgefangen, davon 450 im Anflug auf Moskau. Eine Ölraffinerie wurde beschädigt, vier Menschen starben und etwa 20 wurden verletzt. Die Zahlen stammen von russischer Seite.",
  ZDF_MOS, "2026-09-20T12:10:00+00:00", ["World", "Ukraine war", "Russia"],
  [src("ZDFheute", ZDF_MOS, "2026-09-20T12:10:00+00:00", 2)],
  8.0,
  en={"title": "Ukrainian drone attack on Moscow overshadows Russia's parliamentary election",
      "summary": "According to Russian figures, more than 1,600 drones were intercepted, 450 of them heading for Moscow. A refinery was damaged, four people died and about 20 were injured. The figures come from the Russian side."},
  readMore={
   "why": "Die Wahl ist die erste Parlamentswahl in Russland seit Beginn des Angriffskriegs gegen die Ukraine im Februar 2022.",
   "happened": [
     "Die Ukraine flog am 20. September einen massiven Drohnenangriff auf Moskau. Nach russischen Angaben starben vier Menschen in der Region Moskau und im besetzten Teil der Region Cherson; etwa 20 wurden verletzt.",
     "Die Wahl lief vom 18. bis 20. September. Die Beteiligung lag am Sonntag über 45 Prozent; ein klarer Sieg der Regierungspartei „Einiges Russland“ wird erwartet. Die Wahlkommission meldete Cyberangriffe auf die Wahl-Infrastruktur."],
   "sides": [
     {"who": "Präsident Selenskyj", "view": "Die Langstrecken-Reaktionen der vergangenen Nacht hätten „sehr bedeutende Auswirkungen“ in der Region Moskau gehabt."},
     {"who": "Moskaus Bürgermeister", "view": "Sprach von einem „beispiellosen Angriff“, der die Wahl stören sollte."},
     {"who": "Ukraine", "view": "Bezeichnet die Abstimmung in Russland als „Pseudowahl“."}],
   "confirmed": ["Die Angaben zu Drohnen, Toten und Verletzten sind russische Angaben, wie ZDFheute sie wiedergibt."],
   "uncertain": ["Das Ausmaß der Schäden an der Raffinerie ist nicht unabhängig bestätigt.", "Das Wahlergebnis stand beim Abruf noch aus."],
   "keyPoints": ["Mehr als 1.600 Drohnen nach russischen Angaben abgefangen.", "Erste Parlamentswahl seit Beginn des Krieges.", "Alle Zahlen stammen von russischer Seite."]}),
]

# ---------------- MEDICAL ----------------
PM = "https://pubmed.ncbi.nlm.nih.gov/42564714/"
MTD_HUGO = "https://www.medtechdive.com/news/fda-clears-vessel-sealing-device-for-medtronics-hugo-robot/830625/"
MTD_COG = "https://www.medtechdive.com/news/cognita-imaging-wins-fda-contract-to-test-llms-in-evaluating-radiology-ai/830788/"
medical = [
 story("medical", 1, "en", "Global Delphi panel defines what counts as a dermal matrix in surgical reconstruction",
  "An international expert panel reached consensus on 34 of 41 statements defining dermal matrices, covering definitions, safety, biological function and outcomes (JPRAS Open, September 2026). It did not agree on synthetic components, degradation timing, pore size or barrier properties.",
  PM, "2026-09-01T00:00:00+00:00", ["Dermal matrices", "Reconstructive surgery", "Consensus"],
  [src("PubMed / JPRAS Open", PM, "2026-09-01T00:00:00+00:00", 2)],
  18.0, evidence="peer_reviewed", matridermRelevant=True,
  readMore={
   "why": "A shared definition of 'dermal matrix' affects how products are grouped in guidelines and compared in studies. The points left open are features that separate product types, so they are likely to matter in future comparisons.",
   "newsSummary": [
     "A steering committee drafted 41 statements. A global panel rated them on a five-point scale, with 75% agreement needed for consensus. Agreement was reached on 34 statements about definitions, safety, biological functions and clinical outcomes.",
     "Disagreement remained on synthetic components, specific matrix constituents, degradation timing, pore dimensions and barrier properties. The authors put the gaps down to product variability and too little comparative research."],
   "background": "The paper, 'Defining dermal matrices: Results of a global Delphi panel in surgical reconstruction', appears in JPRAS Open, volume 51, issue 4 (September 2026), DOI 10.1016/j.jpra.2026.07.007, PMID 42564714. The lead author is C. Magnoni; collaborators include J.-P. Hong, E. Dantzer and A. de Vries. The exact online date was not retrieved.",
   "study": {"design": "Delphi consensus study: structured expert rating, 75% agreement threshold", "intervention": "None. The panel rated statements about definitions.", "area": "Dermal matrices in surgical reconstruction"},
   "results": "Consensus on 34 of 41 statements. No consensus on synthetic components, matrix constituents, degradation timing, pore dimensions or barrier properties.",
   "limitations": "Expert consensus, not trial data. Panel size and the full text were not retrieved, so this summary rests on the abstract.",
   "relevance": {
     "clinicians": "A common vocabulary for comparing matrices in reconstructive cases.",
     "companies": "Product claims are likely to be read against the consensus definition. This is an inference, not stated in the abstract."},
   "matriderm": {
     "competitive": "The abstract names no products, so whether MatriDerm's collagen-elastin structure meets each consensus statement needs the full text.",
     "positioning": "The open points on synthetic components and degradation are where positioning against synthetic templates such as NovoSorb BTM could be tested. This is an inference."},
   "keyTakeaways": ["Consensus on 34 of 41 statements.", "Synthetic components and degradation timing remain contested.", "Full text needed before drawing product-level conclusions."]}),
 story("medical", 2, "en", "FDA clears vessel-sealing instrument for Medtronic's Hugo robot",
  "The LigaSure instrument is now cleared for use with Medtronic's Hugo robotic system, expanding the platform's surgical applications (MedTech Dive, 17 September).",
  MTD_HUGO, "2026-09-17T14:43:00+00:00", ["Regulatory", "Surgical robotics"],
  [src("MedTech Dive", MTD_HUGO, "2026-09-17T14:43:00+00:00", 5)],
  4.0, evidence="trade_press", matridermRelevant=False,
  readMore={"why": "Robotic-surgery clearances shape the device market but sit next to, not inside, wound care and dermal matrices.",
            "newsSummary": ["Based on the trade-press headline and one-line description. The FDA record was not checked."],
            "limitations": "Trade-press item; full article not read."}),
 story("medical", 3, "en", "Cognita Imaging wins FDA contract to test LLMs in evaluating radiology AI",
  "The FDA has awarded Cognita a contract to test a method for evaluating AI-generated radiology reports, as the agency considers how to regulate generative-AI-enabled devices (MedTech Dive, 18 September).",
  MTD_COG, "2026-09-18T15:35:00+00:00", ["Regulatory", "AI"],
  [src("MedTech Dive", MTD_COG, "2026-09-18T15:35:00+00:00", 5)],
  3.2, evidence="trade_press", matridermRelevant=False,
  readMore={"why": "An early signal of how the FDA may assess generative AI in devices.",
            "newsSummary": ["Based on the trade-press headline and one-line description. The full article was not read."],
            "limitations": "Trade-press item; full article not read."}),
]

# ---------------- GROWTH ----------------
OUT_URL = "https://www.oneusefulthing.org/p/the-overhang"
SW = "https://simonwillison.net/2026/Sep/17/how-to-write-with-an-llms/"
FS = "https://fs.blog/knowledge-project-podcast/tobi-lutke-3/"
growth = [
 story("growth", 1, "en", "The Overhang: what today's AI can already do, and what only you bring",
  "Ethan Mollick argues that current models already hold large, unused capability. He names four human advantages that matter most when working with them: deep knowledge, wide knowledge, taste and agency.",
  OUT_URL, "2026-09-18T17:54:00+00:00", ["AI & smart tools"],
  [src("One Useful Thing", OUT_URL, "2026-09-18T17:54:00+00:00", 3)],
  8.4, kind="article",
  readMore={
   "useful": "Helps you decide where to spend your own effort when AI can produce a first draft of almost anything.",
   "idea": [
     "Mollick argues that while society debates future AI risks, today's models already have transformative capabilities that are widely underused. The gap between what they can do and what people ask of them is the 'overhang'.",
     "The opportunity is not to compete with AI on output but to combine it with four human advantages: deep knowledge, wide knowledge, taste and agency."],
   "example": "Examples in the post: turning the 1977 text game Zork into a playable 3D action game, rebuilding Umberto Eco's library in 3D from videos and catalogue data, and making animated book trailers with Blender and video-generation tools.",
   "keyTakeaways": [
     "The capability overhang is real: guided well, current systems can do weeks of human work.",
     "Expertise, breadth, judgement and the willingness to explore boundaries gain value as routine production is automated.",
     "How AI is used remains a choice between enhancing and replacing human effort."]}),
 story("growth", 2, "en", "How To Write With An LLM: use it as a copyeditor, not a writer",
  "Simon Willison highlights Thomas Ptacek's advice: treat an LLM as a copyeditor rather than a writer, and avoid its suggested phrasing entirely.",
  SW, "2026-09-17T12:00:00+00:00", ["AI & smart tools", "Communication"],
  [src("Simon Willison", SW, "2026-09-17T12:00:00+00:00", 3)],
  6.9, kind="article",
  readMore={
   "useful": "A simple rule for using AI on your own writing without losing your voice.",
   "idea": ["Only the feed summary was read: the advice is to use the model for copyediting and to reject its suggested phrasing."],
   "keyTakeaways": ["Copyeditor, not writer.", "Do not adopt the model's phrasing."]}),
 story("growth", 3, "en", "Tobi Lütke: AI agents, better decisions and the future of work",
  "The Shopify founder talks about using AI 'councils' for strategic decisions, and why human judgement becomes more valuable as AI advances (The Knowledge Project, 10 September).",
  FS, "2026-09-10T12:00:00+00:00", ["Decision-making", "Leadership", "AI & smart tools"],
  [src("Farnam Street", FS, "2026-09-10T12:00:00+00:00", 3)],
  5.2, kind="article",
  readMore={
   "useful": "Shows how a founder uses AI as one input into a decision rather than the decision-maker.",
   "idea": ["Only the feed description was read: it covers AI councils for strategic decisions and the growing value of human judgement."],
   "keyTakeaways": ["AI as a council for decisions.", "Human judgement gains value."]}),
]

meta = {
  "generatedAt": NOW,
  "windowsDays": {"football": 3, "news": 7, "medical": 21, "growth": 90},
  "sample": False,
  "notes": [
    "First real brief, compiled by hand on 20 September 2026 from the pages that could be fetched. Not every configured source was reachable.",
    "Not reachable today: NDR, Tagesschau, DW, BBC, AP, Guardian and FT. No reliable Hamburg source, so there are no Hamburg stories. Iran and Fed items rest on the sources named on each card.",
    "No video cards: YouTube feeds could not be read, and thumbnails cannot load inside this page.",
    "Football: possession and shots come from one match report. xG, Champions League position and lineups need a licensed data feed and are unavailable. No verified transfer story was found in the window.",
    "Medical: one peer-reviewed item and two trade-press items in the 21-day window. No verified competitor news. A MatriDerm press release from January 2025 was left out as outside the window.",
    "Growth: Willison and Farnam Street cards are based on the feed summaries only, not the full posts.",
  ],
}

docs = {"football": {"updatedAt": NOW, "stories": football}, "news": {"updatedAt": NOW, "stories": news},
        "medical": {"updatedAt": NOW, "stories": medical}, "growth": {"updatedAt": NOW, "stories": growth},
        "barcelona": barcelona, "meta": meta}
for k, v in docs.items():
    with open(os.path.join(OUT, k + ".json"), "w") as f:
        json.dump(v, f, ensure_ascii=False)
    print(k, os.path.getsize(os.path.join(OUT, k + ".json")))
