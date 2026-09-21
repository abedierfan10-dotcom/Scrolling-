"""Clearly-fictional placeholder brief so the app can be judged before real feeds run.
Every headline is a stand-in; nothing here claims a real event."""
import json
from datetime import datetime, timedelta, timezone
now = datetime.now(timezone.utc)
def t(h): return (now - timedelta(hours=h)).isoformat()
def src(h, tier=2): return [{"name": "Sample feed", "url": "#", "publishedAt": t(h), "tier": tier}]
def s(i, cat, title, summary, subs, h, score, **kw):
    d = dict(id=f"sample-{cat}-{i}", category=cat, lang="en", title=title, summary=summary, url="#", publishedAt=t(h),
             subtopics=subs, sources=src(h), developing=False, latestUpdate=None, earlier=[], isNew=(h < 20), score=score, firstSeen=t(h))
    d.update(kw); return d
tabs = {
 "football": [
  s(1,"football","Sample headline: Barcelona match report","One or two sentences summarising the match appear here, in plain words.",["Barcelona","Results"],4,16.4,
    readMore={"keyPoints":["First key point of the match.","Second key point.","Third key point."],"why":"A line on what this result changes in the table."}),
  s(2,"football","Sample headline: important Barcelona transfer, officially confirmed","A transfer story carries a reliability label: official, highly reliable, reported or rumour.",["Barcelona","Transfers"],7,15.2,transfer="OFFICIAL"),
  s(3,"football","Sample headline: Champions League status update","Standing and status stories sit alongside results.",["Champions League","UCL status"],9,9.6,
    developing=True, latestUpdate="Sample latest update line for a developing story", earlier=[{"title":"Sample earlier update","source":"Sample feed","publishedAt":t(30)},{"title":"Sample first report","source":"Sample feed","publishedAt":t(52)}]),
  s(4,"football","Sample headline: a reported Premier League transfer","Medium-priority leagues appear below the high-priority ones.",["Premier League","Transfers"],14,5.4,transfer="REPORTED"),
  s(5,"football","Sample headline: an unconfirmed transfer","Important but unverified stories stay labelled.",["La Liga","Transfers"],16,6.1,transfer="RUMOUR"),
  s(6,"football","Sample headline: an older football story","This one is past the fresh window, so it sits under Show older.",["Bundesliga","Results"],58,3.1),
 ],
 "news": [
  s(1,"news","Sample headline: a Hamburg city story","German stories keep their language, with the title and summary in German.",["Hamburg","Government"],6,8.7, lang="de",
    readMore={"why":"One or two sentences on why the story matters to you.","happened":["First paragraph of a neutral account.","Second paragraph continues the account."],"background":"The context a reader needs to follow along.",
      "sides":[{"who":"Government / Party A","view":"Their documented position."},{"who":"Opposition / Party B","view":"Their documented position."}],
      "confirmed":["A verified fact."],"uncertain":["A disputed point.","What may happen next."],"keyPoints":["Takeaway one.","Takeaway two."]}),
  s(2,"news","Sample headline: a Germany-wide story","Another placeholder summary, one sentence.",["Germany","Economy"],11,7.5, lang="de"),
  s(3,"news","Sample headline: an Iran story","Placeholder geopolitical news.",["Iran","Conflict"],15,6.2),
  s(4,"news","Sample headline: an EU story","Placeholder EU policy news.",["EU","Law & Policy"],22,4.0),
  s(5,"news","Sample headline: an older news story","Past the news window's fresh period.",["World"],100,1.0),
 ],
 "medical": [
  s(1,"medical","Sample headline: MatriDerm clinical study","A placeholder for a dermal matrix story that mentions MatriDerm.",["MatriDerm","Dermal matrices","Clinical study"],30,17.9,evidence="peer_reviewed",matridermRelevant=True,
    readMore={"why":"Why this matters clinically and commercially.","newsSummary":["First professional paragraph.","Second professional paragraph."],"background":"Short relevant context.",
      "study":{"design":"Study design in one line.","sample":"Who was studied.","intervention":"What was applied.","comparator":"What it was compared with.","area":"Clinical area."},
      "results":"Key outcomes with the useful numbers.","limitations":"Weaknesses and uncertainty.",
      "relevance":{"clinicians":"What changes for clinicians.","hospitals":"What changes for hospitals.","companies":"What changes for device companies.","commercial":"Commercial strategy angle.","market":"Market development angle."},
      "matriderm":{"competitive":"Competitive implication.","clinical":"Clinical implication.","positioning":"Positioning implication.","market":"Market implication."},
      "keyTakeaways":["Takeaway one.","Takeaway two.","Takeaway three."]}),
  s(2,"medical","Sample headline: a competitor launches a new dermal template","A placeholder for competitor news.",["Competitors","Product launch"],40,11.1,evidence="company"),
  s(3,"medical","Sample headline: FDA clearance for a wound-care device","A placeholder for a regulator notice.",["Wound care","Regulatory"],70,7.2,evidence="regulator"),
  s(4,"medical","Sample headline: reconstructive surgery technique paper","A placeholder for a research paper.",["Reconstructive surgery","Research"],200,5.5,evidence="peer_reviewed"),
  s(5,"medical","Sample headline: an older industry item","Within the three-week window but past the fresh week.",["Industry"],300,1.2,evidence="trade_press"),
 ],
 "growth": [
  s(1,"growth","Sample headline: a negotiation talk worth watching","A placeholder video summary of three to five sentences appears here so the card explains what the talk covers before you press play.",["Persuasion & negotiation"],30,5.6,kind="video",
    video={"duration":"18:42","watchUrl":"#","channel":"Sample channel"},why="Why this video is useful to you.",learn=["First thing you will learn.","Second thing you will learn."],
    readMore={"whyWatch":"Why this is worth watching.","mainIdea":"The main idea in a sentence or two.","keyConcepts":["Concept one.","Concept two."],"bestParts":[],"howToApply":["Practical step one.","Practical step two."],"keyTakeaways":["Takeaway one.","Takeaway two."]}),
  s(2,"growth","Sample headline: an AI tool that saves an hour a day","A placeholder for a useful tool or workflow.",["AI & smart tools"],20,4.6,
    readMore={"useful":"Where this helps in real life.","idea":["Two or three clear paragraphs.","Second paragraph."],"howItWorks":"The mechanism or framework.","example":"A realistic example.",
      "howToUse":["Practical action one.","Practical action two."],"watchOut":["A limitation or common mistake."],"keyTakeaways":["Takeaway one.","Takeaway two."]}),
  s(3,"growth","Sample headline: a decision-making framework","Evergreen ideas are judged on quality rather than recency.",["Decision-making"],400,3.0),
 ],
}
barcelona = {"nextMatch":{"opponent":"Sample FC","competition":"La Liga","kickoff":(now+timedelta(days=2)).isoformat(),"home":True,"venue":"Sample Stadium, Sample City","form":"WWDLW"},
             "lastMatch":{"opponent":"Example United","competition":"La Liga","home":False,"score":{"for":2,"against":1},"scorers":[{"player":"Player A","minute":12},{"player":"Player B","minute":67}],"possession":58.0,"shots":14,"xg":None},
             "laLiga":{"pos":3,"of":20,"points":14,"played":6},"ucl":{"pos":9,"of":36,"points":4,"played":2}}
print(json.dumps({"generatedAt": now.isoformat(), "sample": True, "windowsDays": {"football":3,"news":7,"medical":21,"growth":90}, "tabs": tabs, "barcelona": barcelona}, indent=1))
