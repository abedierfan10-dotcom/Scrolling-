"""Synthetic RSS fixtures (clearly fake) to exercise dedupe/freshness/ranking offline."""
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from pathlib import Path
now = datetime.now(timezone.utc)
def rss(items):
    body = "".join(f"<item><title>{t}</title><link>{l}</link><pubDate>{format_datetime(now - timedelta(hours=h))}</pubDate><description>&lt;p&gt;{d}&lt;/p&gt;</description></item>" for t, l, h, d in items)
    return f"<?xml version='1.0'?><rss version='2.0'><channel><title>x</title>{body}</channel></rss>"
fx = Path(__file__).parent / "fixtures"
fx.mkdir(exist_ok=True)
(fx / "feeds.bbci.co.uk.xml").write_text(rss([
  ("Barcelona beat Girona 3-1 in La Liga", "https://feeds.bbci.co.uk/a?utm_source=x", 5, "Barcelona won at home. Yamal scored twice. A third sentence."),
  ("Arsenal sign new striker", "https://feeds.bbci.co.uk/b", 20, "Arsenal completed a deal."),
  ("Old story from last month", "https://feeds.bbci.co.uk/old", 24*30, "Too old."),
  ("Future dated glitch", "https://feeds.bbci.co.uk/fut", -72, "Clock skew."),
  ("Barcelona Girona latest: injury update", "https://feeds.bbci.co.uk/c", 1, "Fitness news."),
  ("Barcelona Girona latest: lineup confirmed", "https://feeds.bbci.co.uk/d", 12, "Lineups."),
  ("Barcelona Girona latest: post-match reaction", "https://feeds.bbci.co.uk/e", 2, "Reactions."),
]))
(fx / "www.espn.com.xml").write_text(rss([
  ("Barcelona beat Girona 3-1 in La Liga clash", "https://www.espn.com/x", 4, "ESPN report of the Barcelona match with much more detail here. Second sentence."),
  ("Celebrity gossip roundup", "https://www.espn.com/g", 3, "gossip"),
]))
(fx / "www.tagesschau.de.xml").write_text(rss([
  ("Hamburger Senat beschließt neues Hafenkonzept", "https://www.tagesschau.de/h", 6, "Der Senat hat in Hamburg ein Konzept für den Hafen beschlossen. Weitere Details folgen."),
  ("Bundestag debattiert Haushalt", "https://www.tagesschau.de/b", 30, "Debatte im Bundestag."),
]))
atom = f"<?xml version='1.0'?><feed xmlns='http://www.w3.org/2005/Atom'><entry><title>FDA clears new dermal regeneration template</title><link rel='alternate' href='https://www.fda.gov/1'/><published>{(now - timedelta(days=5)).isoformat()}</published><summary>FDA 510(k) clearance for a dermal template.</summary></entry></feed>"
(fx / "www.fda.gov.xml").write_text(atom)
yt = f"""<?xml version='1.0'?><feed xmlns='http://www.w3.org/2005/Atom' xmlns:yt='http://www.youtube.com/xml/schemas/2015' xmlns:media='http://search.yahoo.com/mrss/'>
<entry><yt:videoId>abc123XYZ</yt:videoId><title>How to negotiate your salary with BATNA</title><link rel='alternate' href='https://www.youtube.com/watch?v=abc123XYZ'/><published>{(now - timedelta(days=20)).isoformat()}</published>
<media:group><media:thumbnail url='https://i.ytimg.com/vi/abc123XYZ/hqdefault.jpg'/><media:description>A talk on salary negotiation and leverage. See https://example.com for more.</media:description></media:group></entry></feed>"""
(fx / "www.youtube.com.xml").write_text(yt)
(fx / "www.ndr.de.xml").write_text(rss([
  ("Polizei nimmt Tatverdächtigen nach Diebstahl in Hamburg fest", "https://www.ndr.de/a", 3, "Routine."),
  ("Hamburger Senat beschließt neuen Haushalt", "https://www.ndr.de/b", 5, "Der Senat hat den Haushalt beschlossen."),
]))
