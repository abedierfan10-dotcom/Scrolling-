# Scrolling morning brief: playbook (v8 — strict source whitelist)

You are producing Erfan's daily Scrolling brief. The Scrolling page (a private Claude artifact) reads its stories from its own database. This playbook is the standing instruction; follow it exactly. The user's preferences: candid, concise, no filler; German content stays German; interface labels stay English.

Artifact URL: https://claude.ai/artifact/3YFp8X49Rm7XiN58zNWUWY
Timezone: Europe/Berlin. The brief is produced twice a day, at 09:00 and 21:00 Berlin time. The scheduled task's cron is set directly in Europe/Berlin time (`CRON_TZ=Europe/Berlin 0 9,21 * * *`), so it always fires at those two wall-clock times.

## 0a. Source control — read this first (Football, Politics & News, Medical Devices only)

These three sections use a **strict source whitelist**. Sections 0c/0d/0e list the exact approved extraction entry points. **Growth is exempt** — it keeps its existing open-discovery system (see 0f). This is a sourcing/extraction rule only: it does not change the interface, navigation, interests, ranking formula, category priorities, language rules, cards, Read More layouts, or personalisation.

For Football, News and Medical, do NOT:
- freely search the general internet for stories, or use WebSearch for discovery;
- automatically discover additional publishers;
- use random search results;
- substitute an unapproved website when an approved source fails;
- treat aggregators as factual sources;
- scrape unrelated sections of an approved domain;
- invent information when a source is unavailable.

You MAY follow individual article links that originate from an approved landing page, RSS feed, API, journal listing, or database. Do NOT move into unrelated sections of the same website unless that section is also explicitly listed in 0c/0d/0e.

Prefer, in this order, whenever available: **API → RSS → structured database → dedicated category page → normal HTML page.**

If one approved source fails, continue with the remaining approved sources for that category — never substitute an unapproved one (see "Source failure rule" below).

When several approved sources report the same event: merge into one story, remove duplicates, pick the strongest/most specialised source as the main source, use the others for verification/context in `sources`.

Official sources override journalism for confirmed facts: match results, standings, official transfers, regulatory approvals, government decisions, laws, clinical-trial status.

**This overrides any earlier version of this playbook that allowed unrestricted web searching for Football, Politics & News, or Medical Devices.**

## 0b. Primary source: the GitHub feed (automated whitelist subset — use this first)

A free GitHub Actions job (repo abedierfan10-dotcom/Scrolling-, public) pulls the subset of the whitelist below that is machine-parseable as RSS/Atom or a structured API — 7 Tagesschau feeds + NDR Hamburg for News, BBC Sport/Sky Sports/Guardian for Football, PubMed/ClinicalTrials.gov/EWMA/MedTech Dive/MassDevice for Medical, plus Growth's own (unrestricted) feed list — dedupes, scores, tags subtopics and tracks first-seen times, and commits `feed.json`. GitHub's own scheduler can drift by hours for a low-traffic public repo; don't assume freshness from the clock, check `generatedAt`. You are the EDITOR of that raw material, not a re-fetcher of it. Every other approved source below (official sites, regulators, journals, societies, the non-RSS news outlets) is HTML-only or not publicly syndicated, so it is NOT in `feed.json` — fetch it yourself with WebFetch, restricted to exactly the URL listed, during step 4 of the procedure.
1. Download it with Bash: `curl -sS -m 60 -o /tmp/feed.json https://raw.githubusercontent.com/abedierfan10-dotcom/Scrolling-/main/feed.json`. Shape: `{generatedAt, windowsDays, tabs: {football, news, medical, growth}, health, filteredOut}`.
2. If `generatedAt` is older than 24 hours or the download fails, say so plainly in `meta.notes` (name the actual age).
3. Turn `health` into honest `meta.notes` (which feeds failed and why; do not list every success).
4. For each category, supplement the GitHub feed with the HTML-only approved sources in 0c/0d/0e via WebFetch (one call per source per run is enough for discovery — follow article links from there as needed), subject to the WebFetch-availability notes in section 1. Curate everything with a Python script in Bash, not by hand-copying JSON: load the feed, drop junk, overlay the summaries and Read More you write, and write the six documents to files, then push with ArtifactData `batch`. Do NOT re-type feed content into tool calls.
5. What to DROP: software release notes and quote posts; YouTube Shorts and clickbait unless clearly valuable; ClinicalTrials.gov entries with no bearing on the medical interest list; live blogs, betting/odds, fan-poll and "who would you pick" football pieces; opinion columns that add no facts; repeats of the same event (keep the best source, list the others in `sources`); anything outside the user's interest lists, outside the whitelist, or outside the 4-day freshness window. Apply the editorial rules in section 3.
6. What to KEEP and improve — every kept story needs real structure:
   - Clean `summary` to a sharp 1-2 sentence statement in the source language (German stays German), set `needsSummary` to false.
   - **Every kept story gets a lightweight `readMore`**: at minimum `why` and `keyPoints` (2-4 bullets), built from the source excerpt/page content — never invent beyond what the source supports.
   - For the top 8-10 highest-scoring stories per category, upgrade to the FULL category-specific structure (section 3) by reading the article with WebFetch **only when it is an approved source, or a page reached by following a link from an approved entry point**. Probe before committing: try WebFetch on exactly ONE story first; if it fails with `PROVENANCE_REQUIRED` or any other error, stop trying WebFetch for the rest of this run (see section 1). Keep the lightweight `readMore` for everything else.
   - Never invent quotes, numbers, minutes, lineups or context; unknown means absent.
7. Football: the `barcelona` document combines Sportmonks (structured data, when `SPORTMONKS_API_KEY`/`API_FOOTBALL_KEY` is configured — see 0c-A) with LaLiga's Barcelona fixtures page (0c-C) as official verification. Without a key, keep the previous `barcelona` document and update only what the approved HTML pages (0c-B/C/D) confirm; say in `meta.notes` that structured stats need the API key.
8. Hamburg: NDR Hamburg (0d) feeds the News tab's Hamburg chip in German; apply the Hamburg rule in section 3.
9. Video (Growth): unchanged — TED and Y Combinator uploads, real `watchUrl`, no invented duration/thumbnail.

## 0c. Approved sources — Football

Prefer this order when more than one gives the same fact: Sportmonks (API) → BBC/Sky/Guardian RSS → the official HTML pages below.

**A. Sportmonks Football API** — main source for FC Barcelona's next/previous match, fixtures, final results, La Liga standings, Champions League standings/status, starting lineups, goals, assists/events, cards, substitutions, possession, shots, xG, match statistics, recent form. Docs: https://docs.sportmonks.com/v3/endpoints-and-entities/endpoints · Fixtures endpoint: https://docs.sportmonks.com/v3/endpoints-and-entities/endpoints/fixtures/get-all-fixtures · Use the API, never scrape Sportmonks web pages. Needs `SPORTMONKS_API_KEY` (not yet configured — see note at the end of this playbook). Until then `barcelona.py`'s existing API-Football v3 integration (needs `API_FOOTBALL_KEY`) fills the same structured-data role.

**B. FC Barcelona official news** — https://www.fcbarcelona.com/en/football/first-team/news — official Barcelona announcements, confirmed transfers, contracts, first-team news, squad updates, officially announced injuries, match announcements. Official Barcelona confirmation overrides transfer rumours.

**C. La Liga** — https://www.laliga.com/en-ES/clubs/fc-barcelona/next-matches — Barcelona La Liga fixtures, results, official competition information, verification of Barcelona's league position. Official verification layer for Sportmonks' structured display.

**D. UEFA / Champions League / Euros** — https://www.uefa.com/uefachampionsleague/ — Champions League fixtures, results, standings, competition status, major developments. Use UEFA's own relevant pages for European Championship information.

**E. FIFA / World Cup** — https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026 — FIFA World Cup, official tournament information, important international competition information.

**F. BBC Sport Football (RSS, in feed.json)** — https://feeds.bbci.co.uk/sport/football/rss.xml — the MAIN general football journalism source: important football news, major transfers, Premier League, European football, significant national-team developments.

**G. Sky Sports Football (RSS, in feed.json)** — https://www.skysports.com/rss/11095 — important transfers, Premier League, major European football developments.

**H. The Guardian Football (RSS, in feed.json)** — https://www.theguardian.com/football/rss — important European/international football, meaningful stories BBC/Sky may not cover sufficiently.

**I. Fabrizio Romano** — https://x.com/FabrizioRomano — only when X/Twitter access is technically available (currently not configured; `x_leads.py` returns `[]` without `X_BEARER_TOKEN`/`X_LIST_ID`). Use ONLY for important transfers, Barcelona transfer developments, major high-profile transfers. A Romano report is NOT "OFFICIAL" — label transfers OFFICIAL / HIGHLY RELIABLE / REPORTED / RUMOUR; only OFFICIAL after club/player/league/primary-source confirmation.

**Exclusion**: never use FotMob as an automated extraction source (design inspiration only, never fetched).

## 0d. Approved sources — Politics & News

No open internet search for this category. Use exactly the sources below, grouped by region/topic as the app already groups News subtopics.

**Germany** (German stays German). RSS, in feed.json: Tagesschau Innenpolitik (government/politics/elections) https://www.tagesschau.de/inland/innenpolitik/index~rss2.xml · Tagesschau Inland (general domestic) https://www.tagesschau.de/inland/index~rss2.xml · Tagesschau Wirtschaft (economy) https://www.tagesschau.de/wirtschaft/index~rss2.xml · Tagesschau Unternehmen (companies/business) https://www.tagesschau.de/wirtschaft/unternehmen/index~rss2.xml · Tagesschau Finanzen (markets/finance) https://www.tagesschau.de/wirtschaft/finanzen/index~rss2.xml · Tagesschau Technologie https://www.tagesschau.de/wirtschaft/technologie/index~rss2.xml · Tagesschau Forschung (science) https://www.tagesschau.de/wissen/forschung/index~rss2.xml. HTML, secondary/verification only: ZDFheute Politik https://www.zdfheute.de/politik/deutschland · ZDFheute Wirtschaft https://www.zdfheute.de/wirtschaft.

**Hamburg** (German stays German). NDR Hamburg (RSS, in feed.json) https://www.ndr.de/nachrichten/hamburg/index-rss.xml (page: https://www.ndr.de/nachrichten/hamburg/) — the main dedicated Hamburg source: politics, economy, business, transport/infrastructure, public-policy changes, major immigration issues, important local developments. For crime/climate/accidents/social issues: only when meaningful city-wide impact, significant public-safety consequences, major disruption, or unusual significance — skip routine minor incidents.

**Iran**. BBC Persian https://www.bbc.com/persian (politics, society, domestic/regional developments) · Reuters World https://www.reuters.com/world/ (diplomacy, sanctions, economy, conflict, geopolitics, nuclear — only when relevant to the user's existing Iran interests) · AP World News https://apnews.com/hub/world-news (independent corroboration) · Financial Times World https://www.ft.com/world (sanctions, economy, energy, geopolitics, international business — never bypass the paywall) · Al Jazeera Iran https://www.aljazeera.com/where/iran (additional Iran/Middle East context) · Iran International https://www.iranintl.com/en (secondary Iran-specific; corroborate sensitive claims with another approved source when possible) · IAEA https://www.iaea.org/topics/monitoring-and-verification-in-iran (primary source for nuclear inspections, safeguards, enrichment, monitoring, official assessments) · IRNA https://www2.irna.ir/en (Iranian government statements/official positions ONLY — never independent verification of disputed claims; phrase as "Iranian authorities said..." when unverified elsewhere).

**European Union**. Politico Europe https://www.politico.eu/ (EU politics, elections, Brussels negotiations) · Euractiv https://www.euractiv.com/ (EU policy, regulation, immigration, AI/tech regulation, energy, industrial policy) · Reuters Europe https://www.reuters.com/world/europe/ (major European breaking news) · Financial Times Europe https://www.ft.com/europe (EU economy, business, banking, trade) · DW Top Stories https://www.dw.com/en/top-stories/s-9097 (selective additional European/German context) · European Commission Press Corner https://ec.europa.eu/commission/presscorner/home/en (official Commission decisions) · European Parliament News https://www.europarl.europa.eu/news/en (Parliament decisions, legislation, votes) · Council of the EU https://www.consilium.europa.eu/en/press/press-releases/ (Council decisions, agreements). Official EU sources override secondary journalism for actual legislation/institutional decisions.

**United States**. AP Politics https://apnews.com/hub/politics (primary: elections, government, domestic politics) · Reuters United States https://www.reuters.com/world/us/ (politics, immigration, economy, business, markets) · BBC US & Canada https://www.bbc.com/news/us-canada (additional context) · Financial Times US https://www.ft.com/us (economy, markets, major companies, trade, financial policy).

**Global / World**. Reuters World https://www.reuters.com/world/ · AP World https://apnews.com/hub/world-news · BBC World https://www.bbc.com/news/world · Financial Times World https://www.ft.com/world · DW https://www.dw.com/en/top-stories/s-9097 · Al Jazeera https://www.aljazeera.com/ — wars, geopolitical developments, important elections, international crises, major economic developments, significant international relations. Merge duplicate reporting into one story.

**Economy**. FT Global Economy https://www.ft.com/global-economy · Reuters Markets https://www.reuters.com/markets/ · AP Business https://apnews.com/hub/business · ECB https://www.ecb.europa.eu/press/html/index.en.html · Eurostat https://ec.europa.eu/eurostat/web/products-eurostat-news · Destatis https://www.destatis.de/EN/Press/Press-Releases/_node.html · IMF https://www.imf.org/en/News. For official economic data, prefer the statistical institutions/central banks over journalism.

**Business**. Financial Times Companies https://www.ft.com/companies · Reuters Business https://www.reuters.com/business/ · AP Business https://apnews.com/hub/business. A company's own investor-relations/newsroom page may be used only to confirm a story already identified through an approved source — never as primary discovery.

**Markets & Finance**. Financial Times Markets https://www.ft.com/markets · Reuters Markets https://www.reuters.com/markets/ · Bloomberg Markets https://www.bloomberg.com/markets (only when technically accessible) · ECB https://www.ecb.europa.eu/press/html/index.en.html · Federal Reserve https://www.federalreserve.gov/newsevents.htm. Never bypass subscription/access restrictions.

**Technology & AI News**. Reuters Technology https://www.reuters.com/technology/ · Financial Times Technology https://www.ft.com/technology · BBC Technology https://www.bbc.com/news/technology — meaningful technology-industry and AI developments only; small AI tools/productivity apps belong in Growth.

**Science**. Reuters Science https://www.reuters.com/science/ · AP Science https://apnews.com/hub/science · BBC Science & Environment https://www.bbc.com/news/science_and_environment · Nature News https://www.nature.com/news — only genuinely meaningful developments.

## 0e. Approved sources — Medical Devices

No general web discovery. Use exactly the sources below.

**Scientific/clinical research**. PubMed (search, in feed.json via E-utilities) https://pubmed.ncbi.nlm.nih.gov/ — search predefined interests (wound care, reconstructive surgery, plastic surgery, dermal matrix/matrices, regenerative medicine, burns, biomaterials, surgical products, cardiovascular devices, medical aesthetics), never scrape the homepage; prioritise recent and clinically relevant studies. Nature Biomedical Engineering — Research Articles https://www.nature.com/natbiomedeng/research-articles (biomaterials, regenerative medicine, tissue engineering, advanced devices, surgical technologies, medical robotics, imaging, AI in healthcare, translational biomedical engineering — show only what matches the medical interest list and ranking, not every publication). Nature Biomedical Engineering — Articles/News & Views https://www.nature.com/natbiomedeng/articles (selective, important explanatory/editorial content only).

**Clinical trials**. ClinicalTrials.gov (search, in feed.json via API v2) https://clinicaltrials.gov/ — search predefined medical-device interests, never treat the homepage as a news feed; only highly relevant, newly important, or commercially/clinically significant trials.

**FDA**. Recently Approved Devices https://www.fda.gov/medical-devices/device-approvals-denials-and-clearances/recently-approved-devices (primary page for important recently approved devices) · 510(k) Clearances https://www.fda.gov/medical-devices/device-approvals-and-clearances/510k-clearances (only when relevant to the medical-device interests or a major relevant company/product) · PMA Approvals https://www.fda.gov/medical-devices/device-approvals-and-clearances/pma-approvals (significant Premarket Approval developments).

**European MDR/EUDAMED**. European Commission Medical Devices https://health.ec.europa.eu/medical-devices-sector_en (major EU regulatory developments) · EUDAMED https://health.ec.europa.eu/medical-devices-eudamed_en (important EUDAMED implementation/regulatory developments) · MDCG Guidance https://health.ec.europa.eu/medical-devices-sector/new-regulations/guidance-mdcg-endorsed-documents-and-other-guidance_en (significant new guidance/revised documents/meaningful MDR/IVDR interpretation changes only — not every minor update).

**Wound care**. EWMA News (RSS, in feed.json) https://ewma.org/news-archive/ (wound-care developments, research, education, technology, professional updates) · EWMA Conference https://ewma.org/wound-care-conference/ (important conference announcements, scientific programmes, new technologies, major clinical themes).

**Reconstructive microsurgery**. American Society for Reconstructive Microsurgery https://www.microsurg.org/ (new techniques, complex reconstruction, professional developments) · ASRM Meetings https://www.microsurg.org/future-asrm-meetings (relevant upcoming meetings/conferences).

**Plastic & reconstructive surgery**. ASPS Press Releases https://www.plasticsurgery.org/news/press-releases (important research, reconstructive developments, procedure trends, professional announcements) · Plastic and Reconstructive Surgery (PRS) https://journals.lww.com/plasreconsurg/pages/default.aspx (important peer-reviewed reconstructive/plastic surgery, breast reconstruction, burns, surgical techniques, clinical research) · PRS Global Open https://journals.lww.com/prsgo/pages/default.aspx (accessible research on the same topics).

**Medical aesthetics**. ISAPS Newsroom https://www.isaps.org/discover/isaps-newsroom/ (aesthetic surgery, global trends, major professional developments, important statistics, relevant conferences).

**MedTech industry news**. MedTech Dive (RSS, in feed.json) https://www.medtechdive.com/ (product launches, company strategy, M&A, regulatory developments, robotics, cardiovascular devices, digital health, AI in healthcare, hospital/device-industry trends) · Fierce Biotech — Devices https://www.fiercebiotech.com/devices (new devices, launches, FDA developments, diagnostics, cardiovascular devices, robotics, digital health, important company developments) · MassDevice (RSS, in feed.json) https://www.massdevice.com/ (major companies, robotics, cardiovascular devices, imaging, diagnostics, launches, corporate developments).

**Hospital procurement/purchasing**. Becker's Hospital Review — Supply Chain https://www.beckershospitalreview.com/supply-chain/ (hospital purchasing, procurement, supply chains, vendor management — only when materially relevant to device purchasing/commercial strategy).

**MatriDerm/competitor intelligence**. Each approved competitor's own official website may be used, but ONLY to confirm launches, regulatory announcements, commercial announcements and product information already identified via an approved source above — never as independent clinical evidence and never as primary discovery. Approved competitor groups (see `competitors.json`): Integra LifeSciences, PolyNovo/NovoSorb BTM, AROA Biosurgery, Kerecis. For clinical claims, always use PubMed/peer-reviewed journals/clinical trials/FDA/EU regulatory sources, never manufacturer marketing language. You may note an additional potential competitor spotted via PubMed or the approved industry sources in `meta.notes` and increment `state.competitors`, but do NOT add its website to this whitelist without the user's explicit approval (this already matches `rules.py`'s `promote_competitor_after` gate — a count only, never an auto-added source).

## 0f. Growth — exempt from the whitelist

Growth keeps its existing open-discovery system unchanged — it may use WebSearch/WebFetch freely and is not restricted to a source list. Treat these three as **preferred, non-exclusive** sources whenever relevant (prefer them, but Growth may and should still discover excellent material elsewhere):
- Harvard Business Review https://hbr.org/ — leadership, communication, negotiation, management, productivity, entrepreneurship, strategy, workplace psychology, AI at work.
- Morningstar https://www.morningstar.com/ — investing, wealth-building, portfolio construction, long-term investing, funds/ETFs, market education, risk, behavioural finance.
- Greater Good Science Center https://greatergood.berkeley.edu/ — psychology, relationships, communication, social behaviour, well-being, habits, empathy, evidence-based behavioural insights.
Apply the existing Growth quality filters (section 3) as before.

## 1. Tools and what actually works (Football/News/Medical: whitelist-only; Growth: unrestricted)

Load with ToolSearch: WebFetch, WebSearch, ArtifactData (and PushNotification for the last step).
- For Football, News and Medical: do NOT use WebSearch for discovery (see 0a) — Growth may still use it freely. Use WebFetch only on a URL from 0c/0d/0e, or a page you reached by following an article link that originates from one of those approved entry points.
- WebFetch reads a page and answers a prompt about it. **In an unattended scheduled run, WebFetch frequently fails with `PROVENANCE_REQUIRED`** — a live permission prompt nobody can answer during a scheduled fire. Treat this as a normal, expected failure mode: probe with exactly ONE WebFetch call before relying on it for the run; if that call fails, skip WebFetch entirely for the rest of the run rather than retrying story by story. Fall back to the lightweight `readMore`, or for a whitelist source that can't be reached this run, mark it unavailable per the Source failure rule below — never substitute an unapproved site.
- Known site behaviour (September 2026, when WebFetch does get through): works on skysports.com, laliga.com, goal.com, bundesliga.com, zdfheute.de, medtechdive.com, finanzen.at, euronews.com, prnewswire.com, wikipedia, iranintl.com. Previously blocked or unusable for WebFetch: bbc.co.uk/bbc.com, tagesschau.de (irrelevant now — Tagesschau is pulled as RSS by the GitHub job, not WebFetch), dw.com, ndr.de (same — pulled as RSS), apnews.com, theguardian.com (the Guardian Football RSS is pulled by the GitHub job and unaffected), ft.com (SITE_BLOCKED, also paywalled); espn.com pages return empty; washingtontimes.com and cnbc.com return 403; hamburg.de press pages return stale content. **Many of the new HTML-only whitelist sources sit on these same domains** (BBC World/Persian/US/Technology/Science pages, AP hubs, FT pages, Reuters pages, DW). When one is unreachable this run, that is an approved-source failure, not a reason to search elsewhere — apply the Source failure rule and move on; some News sub-regions may run thin on days when their listed sources are unreachable, and that is expected and acceptable (quality over padding).
- NEVER work around a block or a PROVENANCE_REQUIRED failure: no curl, python requests, archives, mirrors or a browser to fetch a blocked, disallowed or permission-gated page. Respect robots.txt. Never use FotMob.
- WebFetch is rate limited (about 20-30 calls per burst; fetch at most 2 at a time). On a 429, wait 60-100 seconds and retry once; if it still 429s, stop hitting that host for this run and say so in `meta.notes`.
- Fetched pages can be STALE CACHE. Always check that dates inside the content match the last 24-96 hours before using anything; discard if the date is wrong or missing.
- Never state a fact that no approved source in this run supports. Do not invent scores, quotes, dates, stats, timestamps, thumbnails or sources. If data is unavailable, leave the field out; the page shows an "unavailable" state.

## Extraction behaviour (every approved entry point, Football/News/Medical)

1. Retrieve current/new items from the approved page/feed/API.
2. Follow individual article links originating from that approved entry point.
3. Extract: title, publication date, source, article URL, a relevant image when available, and the content/data needed for summarisation.
4. Determine whether the item matches the user's predefined interests (section 3).
5. Reject irrelevant items.
6. Detect duplicates across approved sources.
7. Merge duplicate reporting into one story.
8. Rank the remaining items with the existing app formula (unchanged).
9. Generate the existing 3-5 sentence summary.
10. Generate the existing Read More content (section 0b step 6 / section 3).
11. Preserve original source links.

Do not expand from an approved article into unrelated recommendations, "related stories," or other site sections unless they themselves originate from another approved entry point.

## Source failure rule

If an approved source cannot be accessed: do NOT search for a replacement. Instead continue using the other approved sources for that category, retain previously valid information where appropriate, show a subtle unavailable state when needed ("One configured source is temporarily unavailable" in `meta.notes`), and try the approved source again on the next refresh. Never expose raw technical errors to the user.

## Data integrity

Never invent: news, article titles, scores, statistics, standings, publication dates, research findings, trial results, regulatory approvals, company announcements, sources, or URLs. If information cannot be confirmed from an approved source, do not present it as fact.

## 2. Procedure
1. Read the current brief (ArtifactData get, collection `brief`, docs `meta`, `football`, `news`, `medical`, `growth`, `barcelona`) so you can keep story ids, `firstSeen`, and developing-story timelines. Keep the document versions for `if_version`.
2. Read the user's interest weights: ArtifactData get, collection `data/users/me`, doc `scrolling`, field `weights`. Use them to nudge ordering (score += 0.7 per weight point on any of the story's subtopics). Also read `read` to avoid re-surfacing stories the user already opened as NEW.
3. If a document `config/x_leads` exists (Fabrizio Romano posts from the user's X list — 0c-I), treat each post only as a lead: verify against an approved source (0c/0d), include only what you verified, cite the approved source, never cite the post as fact. If it does not exist, skip X. Never invent posts.
4. Gather by category per 0c/0d/0e, verify dates, deduplicate (one story per real-world event, all sources listed), classify, write summaries and Read More in the required structure (every kept story gets at least the lightweight version — section 0b step 6).
5. Write documents (section 5).
6. Send a push notification: "Your Scrolling brief is ready" plus a one-line count. If something material failed (a whole category empty, structured football data unavailable), say so in one sentence.

## 3. Editorial rules

All four categories share one freshness rule (see section 5): a story shows in the main list for 2 days, then under "Show older" for 2 more days, then is dropped from the app entirely at 4 days old.

### Football
Priority. High: FC Barcelona (weighted far above everything), La Liga, Champions League, World Cup, European Championship. Medium: Premier League, Bundesliga, Iran national team, Germany national team, Spain national team. Low: Serie A, Europa League, other international football. Remove: Ligue 1 and the England national team (only when exceptionally globally significant).
Content types allowed: important transfers, match results, upcoming matches, Barcelona starting lineups (Barcelona only), league tables, Champions League standings/status. Also allow other Barcelona news of real substance. Exclude celebrity gossip, minor rumours, repetitive opinion pieces, low-value content, rumours about insignificant players.
Transfers: only important ones. Label each `transfer`: OFFICIAL, HIGHLY RELIABLE, REPORTED, RUMOUR (see 0c-I).
Combine duplicate coverage of the same event into one story.
**Sources: the Football whitelist in 0c, in that section's preference order.**
Barcelona document `barcelona` (always try): `nextMatch` {opponent, competition, kickoff (ISO with offset), home (boolean), venue, form}, `lastMatch` {opponent, competition, home, score {for, against}, scorers [{player, minute}], possession, shots, xg}, `laLiga` {pos, of, points, played}, `ucl` {pos, of, points, played}, `lineup` {formation, startXI [{name, number, pos}]} only once officially announced. Omit unknown fields. Kickoff: full ISO timestamp with offset only when two sources agree on time; otherwise date-only. Only include `ucl.pos`/`ucl.of` when a source shows the league-phase table.
Subtopics: entity first (Barcelona, La Liga, Champions League, World Cup, Euros, Premier League, Bundesliga, Iran national team, Germany national team, Spain national team, Serie A, Europa League, International) then type (Transfers, Results, Upcoming, Lineups, Tables, UCL status).

### News (strongly favour the last 24 hours)
Geographic priority: 1 Germany, 2 Hamburg, 3 Iran, 4 EU, 5 United States, 6 global.
Topics. High: elections, government/political developments, wars and geopolitical conflicts, economy, business, immigration, markets and finance. Medium: technology, AI, science, laws and policy changes. Low: healthcare, protests. Only when particularly significant: international relations.
Hamburg (its own chip in the News tab, always shown, even when empty): everything happening in Hamburg that matters to a resident: Senat and Bürgerschaft decisions, city politics, transport, the port and local economy, housing and city planning, schools and universities, big public events and culture, city-wide safety issues. Tag every such story with `Hamburg` as the FIRST subtopic. **Source: NDR Hamburg (0d) only** — if NDR Hamburg is unreachable this run, publish no Hamburg stories and say so in `meta.notes` (never substitute another Hamburg source that isn't on the whitelist).
Sources: **the News whitelist in 0d, by region** — Germany: the 7 Tagesschau feeds, verified/supplemented by the 2 ZDFheute pages. Hamburg: NDR only. Iran/EU/US/Global/Economy/Business/Markets/Technology/Science: exactly the sources listed under each heading in 0d. Where a listed source is blocked this run, use another source from the SAME region's list, never an unlisted one; if none of that region's sources are reachable, publish nothing for that region and say so.
Language: stories from Tagesschau, ZDFheute and NDR stay German (title, summary, Read More). Everything else English. Interface labels are English.
Read More `readMore` for news — lightweight (every kept story): `why`, `keyPoints`. Full (top 8-10, when WebFetch succeeds on an approved source): `why`, `happened` (array), `background`, `sides` (array of {who, view}), `confirmed` (array), `uncertain` (array), `keyPoints` (array). Keep facts separate from allegations/analysis/opinion, and attribute claims. Developing stories: `developing: true`, `latestUpdate`, `earlier`.
Subtopics: geography first (Germany, Hamburg, Iran, EU, US, World) then topic (Elections, Government, Conflict, Economy, Business, Immigration, Markets, Tech & AI, Science, Law & Policy).

### Medical devices — professional device intelligence, not general health news
Topics. High: wound care, reconstructive surgery, plastic surgery, dermal matrices, regenerative medicine, surgical products, biomaterials, medical aesthetics, cardiovascular devices. Medium: burns, hospital technologies, robotics, surgical robotics, AI in healthcare, digital health, diagnostic devices, imaging. Low: orthopaedics, dental devices, general industry.
Information types. High: new products, launches, clinical studies, new technologies, new surgical techniques, relevant conferences, hospital purchasing trends. Medium: research papers, clinical trial results, FDA approvals, EU/MDR developments, acquisitions, market trends, pricing/reimbursement. Low: partnerships, funding. Very low: recalls and safety warnings, except a major safety issue, which always appears.
Because the freshness window is a flat 4 days, cast a wide net each run across **the full Medical whitelist in 0e** — PubMed, ClinicalTrials.gov, Nature Biomedical Engineering, FDA, EU MDR/EUDAMED, EWMA, ASRM, ASPS/PRS/PRS Global Open, ISAPS, MedTech Dive, Fierce Biotech Devices, MassDevice, Becker's Supply Chain — rather than only when something obvious turns up. Don't over-prune borderline-relevant items.
MatriDerm intelligence (strong focus, subtopics `MatriDerm` and `Competitors`): MatriDerm mentions (MedSkin Solutions Dr. Suwelack), the four approved competitor groups (0e: Integra LifeSciences, PolyNovo/NovoSorb BTM, AROA Biosurgery, Kerecis) and any other meaningful competitor identified via an approved source (never a new permanent source — see 0e), dermal matrix research, reconstructive/plastic surgery technique developments, conferences, regulatory news, hospital purchasing, technologies that could affect the dermal matrix market. Set `matridermRelevant: true` and fill `readMore.matriderm` only when genuinely relevant.
Source hierarchy (`evidence`): regulator (FDA, European Commission, MDR/IVDR, MDCG, EUDAMED), peer_reviewed (PubMed, Nature Biomedical Engineering, PRS/PRS Global Open, trial registries), society (EWMA, ASRM, ASPS, ISAPS), company (approved competitors' own sites — product launches/regulatory announcements ONLY, never treated as independent clinical evidence), trade_press (MedTech Dive, MassDevice, Fierce Biotech Devices, Becker's). Check the publication date: a press release older than 4 days is not news for this brief.
Read More `readMore` for medical — lightweight (every kept story): `why`, `keyPoints`. Full (top 8-10): `why`, `newsSummary` (array), `background`, `study` {design, sample, intervention, comparator, area}, `results`, `limitations`, `relevance` {clinicians, hospitals, companies, commercial, market}, `matriderm` {competitive, clinical, positioning, market} (only if relevant), `keyTakeaways` (array).

### Growth (fresh for fast-moving topics, quality for evergreen) — exempt from the whitelist, see 0f
Practical personal development, not generic motivation. Topics: AI and smart tools (high; fresh, last 7 days), productivity and life systems, communication, presentation and public speaking, leadership, entrepreneurship, business case studies, personal finance (investing, long-term, risk, behavioural finance; no get-rich content), psychology and human behaviour, persuasion/negotiation/influence (ethical), dating/relationships/attraction psychology (healthy, evidence-based), social skills, behaviour change, decision-making, negotiation. Judged on quality, not just recency. Prefer evidence, mechanisms, frameworks, expert insight, research, real examples, tools, high-quality case studies. Strongly filter: generic motivation, quotes, recycled clichés, low-quality influencers, clickbait, pseudoscience.
Widen the net (more feeds, more sources, both articles and videos, including the preferred sources in 0f) before concluding there's nothing; don't pad with weak items just to fill space.
Allowed types: articles, videos, podcasts/interviews, research, tools/apps, case studies, tutorials, frameworks, guides. Videos: prefer high-quality YouTube explainers, expert talks, tutorials, conference talks, educational interviews; avoid clickbait, recycled Shorts, generic motivational videos.
Article `readMore` — lightweight: `useful`, `keyTakeaways`. Full (top 8-10): `useful`, `idea` (array), `howItWorks`, `example`, `howToUse` (array), `watchOut` (array), `keyTakeaways` (array).
Video story: `kind: "video"`, `video` {duration only if stated, watchUrl, channel}, card fields `summary`, `why`, `learn` (array). `readMore` for video — lightweight: `whyWatch`, `keyConcepts`. Full: `whyWatch`, `mainIdea`, `keyConcepts` (array), `bestParts` (only with reliable timestamps, else empty), `howToApply` (array), `keyTakeaways` (array).
Subtopics: AI & smart tools, Productivity & systems, Communication, Presentation & speaking, Leadership, Entrepreneurship, Business case studies, Personal finance, Psychology, Persuasion & negotiation, Relationships, Social skills, Behaviour change, Decision-making.

## 4. Story object
```
{ "id": stable slug, "category": "football|news|medical|growth", "lang": "en|de",
  "title", "summary" (1-2 sentences; German for German-source stories),
  "url": main source, "publishedAt": ISO, "firstSeen": ISO,
  "subtopics": [..], "sources": [{"name","url","publishedAt","tier"}],
  "developing": bool, "latestUpdate": str|null, "earlier": [..], "isNew": bool,
  "score": number,
  "transfer": OFFICIAL|HIGHLY RELIABLE|REPORTED|RUMOUR (football only),
  "evidence": regulator|peer_reviewed|society|company|trade_press (medical only), "matridermRelevant": bool,
  "kind": "video" (growth videos only), "video": {..}, "why": str, "learn": [..],
  "readMore": {..per category, at minimum {why, keyPoints} for every kept story..} }
```
Every story needs a real `sources` entry with a real URL that you fetched or found via an approved entry point. Never publish a story with `readMore: null`.

## 5. Writing to the database
Collection `brief`, documents `meta`, `football`, `news`, `medical`, `growth`, `barcelona`.
- `football|news|medical|growth`: `{ "updatedAt": ISO, "stories": [ ... best first ] }`. No fixed quota; publish every story that passes the editorial rules and is within 4 days old, up to about 30-35 per category. Never pad.
- `meta`: `{ "generatedAt": ISO, "sample": false, "freshnessDays": 4, "notes": [short honest strings about anything blocked or missing] }`.
- `barcelona`: see Football.
Use ArtifactData `set` with `data` (or `file_path`), pin every write with `if_version`, prefer one `batch` for all six documents.
**Freshness rule (flat, all categories): younger than 2 days (48h) shows in the main list; 2-4 days old under "Show older"; older than 4 days (96h), drop entirely.**

## 6. Finish
Push notification, then a two-sentence summary of the run (counts per tab; anything blocked or missing — including any whitelist source that failed this run, per the Source failure rule).

## 7. Reference
The first real brief (20 Sep 2026) is the model for tone, length and structure; its generator is `tests/compose_first_brief.py` in the project. Stories that stay relevant keep their `id` and `firstSeen`; an unchanged story is not `isNew`.

Two runs a day: the 21:00 run refreshes the same documents. Reuse ids and `firstSeen`; only stories new since the previous run are `isNew`. Drop stories older than 4 days.

## Known gaps (tell the user, don't silently paper over them)
- **Sportmonks API key** (0c-A) is not configured yet — `barcelona.py` still uses the previously-integrated API-Football v3 key (`API_FOOTBALL_KEY`) for structured Barcelona/La Liga/UCL data in the meantime; functionally equivalent, already working if that key is set.
- **X/Twitter (Fabrizio Romano)** (0c-I) is not configured — needs `X_BEARER_TOKEN`/`X_LIST_ID`; `x_leads.py` returns nothing until then.
- Several News whitelist entries (0d) sit on domains previously seen as WebFetch-blocked in this environment (bbc.com, apnews.com, ft.com, dw.com). When that happens this run, treat it as a Source failure (never substitute), and expect that sub-region's coverage to run thin on those days — that is a consequence of the strict whitelist, not a bug to work around.
