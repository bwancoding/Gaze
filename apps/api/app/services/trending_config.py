"""
Trending configuration - heat algorithm parameters, RSS source list
"""
from typing import List, Dict
import os

# Heat algorithm configuration
HEAT_TIME_DECAY_LAMBDA: float = float(os.getenv("HEAT_TIME_DECAY_LAMBDA", "0.1"))
HEAT_COMMENT_WEIGHT: float = float(os.getenv("HEAT_COMMENT_WEIGHT", "5.0"))
HEAT_SHARE_WEIGHT: float = float(os.getenv("HEAT_SHARE_WEIGHT", "3.0"))

# Category weights: all 1.0. The earlier Phase A experiment tried lifting
# entertainment/sports/gaming with 1.4x multipliers, but that was a
# band-aid on the real problem — the heat formula was supply-side only
# (media_count * 10) and ignored the demand-side Reddit/HN engagement
# signals that topic seeds already carry. Phase B fixed that root cause
# by persisting topic_engagement_score on TrendingEvent and reading it as
# a first-class term in HeatCalculator.calculate_event_heat, so the
# category multipliers are no longer needed. Keeping the dict for future
# per-category overrides if data shows they're warranted.
CATEGORY_WEIGHTS: Dict[str, float] = {
    "Geopolitics": 1.0,
    "Politics": 1.0,
    "Environment": 1.0,
    "Economy": 1.0,
    "Health": 1.0,
    "Science": 1.0,
    "Technology": 1.0,
    "Society": 1.0,
    "Culture": 1.0,
    "Entertainment": 1.0,
    "Sports": 1.0,
    "Gaming": 1.0,
    "Lifestyle": 1.0,
}
CATEGORY_DEFAULT_WEIGHT: float = 1.0

# Region diversity: events covered by sources from multiple regions get a bonus
REGION_DIVERSITY_BONUS: Dict[int, float] = {
    1: 1.0,    # single region
    2: 1.15,   # 2 regions
    3: 1.3,    # 3 regions (truly global)
}
REGION_DIVERSITY_MAX: float = 1.4  # 4+ regions

# Cap article count influence to prevent niche topics with bot-amplified article counts
ARTICLE_COUNT_BONUS_CAP: float = 1.5  # max multiplier from article count

# Auto-categorization keyword rules
CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "Geopolitics": ["war", "sanctions", "treaty", "nato", "military", "invasion", "diplomacy",
                     "missile", "ceasefire", "troops", "geopolitical", "airbase", "airstrike",
                     "territorial", "embassy", "un security council", "arms deal", "proxy war",
                     "blockade", "buffer zone", "ground operations", "pentagon", "strike",
                     "iran", "israel", "israeli", "gaza", "palestine", "ukraine", "russia",
                     "netanyahu", "zelensky", "zelenskyy", "putin", "kremlin",
                     "air base", "satellite images", "oil tanker", "cuba", "lebanon",
                     "wounded", "troops wounded", "journalist killed", "journalists",
                     "pope", "vatican", "catholic", "palm sunday", "holy land"],
    "Politics": ["election", "vote", "president", "congress", "parliament", "legislation",
                 "senator", "democrat", "republican", "policy", "campaign", "impeach",
                 "executive order", "governor", "mayor", "political party", "white house",
                 "supreme court", "ruling", "protest", "rally", "activist",
                 "fbi", "doj", "cia", "dhs", "kash patel", "hacked", "director",
                 "no kings", "tsa", "house rejects", "executive order",
                 "attorney general", "ousted", "appointed", "cabinet", "nominee"],
    "Environment": ["climate", "carbon", "emissions", "wildfire", "drought", "flood", "hurricane",
                     "earthquake", "tsunami", "pollution", "deforestation", "renewable", "rainforest",
                     "endangered", "conservation", "biodiversity", "coral reef", "glacier",
                     "ecosystem", "wildlife", "bee", "pollinator", "species"],
    "Economy": ["gdp", "inflation", "recession", "trade", "tariff", "stock", "market",
                "unemployment", "fed", "interest rate", "cryptocurrency", "bitcoin",
                "supply chain", "futures", "treasury", "bond", "bank", "settlement",
                "financial", "earnings", "revenue", "profit", "futures markets",
                "layoff", "lay off", "lays off", "employees",
                # Retail / commerce / corporate
                "retail", "retailer", "walmart", "costco", "amazon", "target",
                "store", "chain", "supermarket", "grocery", "wholesale",
                "business", "corporate", "company", "companies", "firm", "firms",
                "ceo", "cfo", "founder", "ipo", "merger", "acquisition", "buyout",
                "startup funding", "venture capital", "private equity",
                "consumer", "customer", "pricing", "discount", "sale",
                "gas station", "fuel prices", "oil prices", "pump"],
    "Technology": ["ai", "artificial intelligence", "quantum", "spacex", "starship", "robot",
                   "chip", "software", "cyber", "data breach", "startup",
                   "nvidia", "amd", "intel", "laptop", "display",
                   "processor", "cpu", "gpu", "cache", "battery", "smartphone", "browser",
                   "linux", "open source", "developer", "programming", "cloud",
                   "machine learning", "llm", "compute", "iphone", "android",
                   "usb", "printer", "tls", "filesystem",
                   "compiler", "runtime", "backend", "frontend", "framework",
                   "ocaml", "c++", "rust", "python", "javascript", "typescript",
                   "java", "golang", "swift", "kotlin", "haskell", "zig",
                   "github", "git", "api", "database", "sql", "nosql",
                   "docker", "kubernetes", "devops", "ci/cd", "deploy",
                   "algorithm", "data structure", "benchmark", "performance",
                   "webassembly", "wasm", "llvm", "jit", "garbage collector",
                   "type system", "functional programming", "concurrency",
                   "codebase", "refactor", "debug", "ide", "editor",
                   "server", "microservice", "serverless", "cdn", "dns"],
    "Health": ["vaccine", "pandemic", "virus", "malaria", "cancer", "fda", "disease",
               "outbreak", "hospital", "medical", "alzheimer", "dementia", "clinical trial",
               "mental health", "mortality", "diagnosis", "therapy", "pharmaceutical",
               "medicine shortages"],
    "Science": ["nasa", "discovery", "species", "genome", "physics", "cern", "telescope",
                "mars", "moon", "asteroid", "fossil", "evolution", "particle", "experiment",
                "observatory", "exoplanet", "biology", "chemistry"],
    "Culture": ["fashion", "art", "book", "novel", "bestseller", "exhibit", "exhibition",
                "architecture", "design", "travel", "tourism",
                "museum", "digitizing", "gallery", "sculpture", "painting", "literature",
                "photography", "heritage", "tradition", "festival", "cultural",
                "landmark", "monument", "opera", "ballet", "theater", "theatre",
                "author", "poet", "poetry", "memoir", "biography", "nonfiction",
                "short story", "publisher", "library", "bookstore", "readers",
                "designer", "couture", "runway", "met gala", "fashion week",
                "vintage", "curator", "retrospective", "installation art"],
    "Lifestyle": ["food", "restaurant", "recipe", "cooking", "chef", "cuisine",
                  "dining", "michelin", "tasting menu", "cookbook", "coffee",
                  "wellness", "yoga", "meditation", "self-care", "skincare",
                  "gym", "workout", "fitness", "nutrition", "diet", "vegan", "vegetarian",
                  "home decor", "interior design", "diy",
                  "gardening", "pets", "cat", "dog", "dating", "relationship",
                  "parenting", "kids", "lifestyle", "habits", "routine"],
    "Society": ["rights", "inequality", "migration", "refugee", "poverty", "education",
                "housing", "jury", "verdict", "lawsuit", "court", "ban", "social media",
                "children", "youth", "privacy", "discrimination", "community", "library",
                "population", "immigration", "foreign resident",
                "instagram", "youtube", "designed to addict",
                "arrest", "arrested", "jailed", "sentenced", "prison", "pleads guilty",
                "plead guilty", "guilty", "murder", "murdered", "killed", "killing",
                "homicide", "kidnap", "abduct", "assault", "rape", "robbery", "fraud",
                "manslaughter", "stabbed", "shot dead", "shooting", "crime", "criminal",
                "police", "prosecutor", "indicted", "convicted", "conviction", "serial killer",
                "missing", "vanished", "husband", "wife",
                "bans", "banned", "deported", "expelled"],
    "Entertainment": ["movie", "film", "oscar", "grammy", "celebrity", "album", "concert",
                      "netflix", "box office", "tv show", "series", "episode", "season",
                      "music", "singer", "actor", "actress", "director", "screenwriter",
                      "streaming", "disney", "hbo", "hulu", "apple tv", "amazon prime",
                      "paramount", "max", "peacock", "a24",
                      "anime", "manga",
                      "trailer", "sequel", "prequel", "remake", "reboot", "spinoff",
                      "broadway", "west end",
                      "billboard chart", "spotify", "apple music", "viral",
                      "premiere", "debut", "soundtrack", "score",
                      "emmy", "golden globe", "bafta", "cannes", "sundance", "venice film festival",
                      "podcast", "standup", "comedian", "comedy special", "reality tv", "reality show",
                      "k-pop", "idol", "boy band", "girl group",
                      "taylor swift", "beyonce", "kendrick", "drake", "rihanna",
                      "dua lipa", "olivia rodrigo", "sza", "harry styles",
                      "timothee", "zendaya", "pedro pascal", "margot robbie",
                      "box office", "debuts", "topping the charts", "number one",
                      "tour dates", "residency", "concert tour", "world tour"],
    "Gaming": ["video game", "gaming", "esports", "gamer", "console", "playstation",
               "xbox", "nintendo", "switch", "steam deck", "pc gaming",
               "ps5", "ps4", "xbox series x", "series s",
               "game release", "game launch", "dlc", "expansion pack",
               "game trailer", "gameplay", "beta test", "early access",
               "indie game", "rpg", "mmorpg", "fps", "battle royale",
               "minecraft", "fortnite", "call of duty", "gta", "grand theft auto",
               "zelda", "pokemon", "final fantasy", "elden ring", "elder scrolls",
               "god of war", "spider-man", "mortal kombat",
               "valorant", "league of legends", "dota", "counter-strike", "csgo", "cs2",
               "overwatch", "apex legends", "rocket league", "fifa game", "nba 2k",
               "twitch", "streamer", "livestream", "stream",
               "game studio", "developer", "publisher", "bethesda", "ubisoft",
               "activision", "ea sports", "electronic arts", "sony interactive",
               "xbox game pass", "nintendo direct", "e3", "game awards", "the game awards",
               "unreal engine", "unity engine", "game mod"],
    "Sports": ["olympic", "world cup", "championship", "tournament", "league", "soccer",
               "football", "basketball", "tennis", "golf", "race",
               "athlete", "nba", "nfl", "mlb", "f1", "formula 1",
               "tiger woods", "rollover crash",
               "premier league", "champions league", "super bowl", "playoffs", "draft",
               "transfer", "injury", "coach", "stadium", "fifa", "ufc", "mma", "boxing",
               "cricket", "rugby", "baseball", "hockey", "nhl", "la liga", "bundesliga",
               "serie a", "world series", "grand slam", "marathon", "triathlon",
               "manager", "manager sacked", "coach fired", "head coach",
               "messi", "ronaldo", "lebron", "mbappe", "haaland", "djokovic", "nadal",
               "alcaraz", "mahomes", "brady",
               "transfer window", "signing", "signed", "free agent",
               "goalscorer", "scored", "goals", "hat-trick", "assist",
               "derby", "clasico", "rivalry", "relegation", "promotion",
               "season opener", "finale", "final", "semi-final", "quarter-final",
               "wimbledon", "us open", "french open", "australian open", "masters",
               "champions", "trophy", "title", "mvp", "player of the year",
               "knockout", "ko", "belt", "featherweight", "heavyweight", "lightweight"],
}

# Clustering configuration
CLUSTER_SIMILARITY_THRESHOLD: float = float(os.getenv("CLUSTER_SIMILARITY_THRESHOLD", "0.75"))
CLUSTER_TOP_KEYWORDS: int = int(os.getenv("CLUSTER_TOP_KEYWORDS", "20"))

# RSS fetch configuration
RSS_FETCH_TIMEOUT: int = int(os.getenv("RSS_FETCH_TIMEOUT", "30"))
RSS_MAX_ARTICLES_PER_FEED: int = int(os.getenv("RSS_MAX_ARTICLES_PER_FEED", "100"))

# RSS source configuration list
RSS_SOURCES: List[Dict] = [
    # P0 priority - authoritative media
    {"id": 1, "name": "Reuters", "stance": "center", "region": "international",
     "url": "https://news.google.com/rss/search?q=when:24h+allinurl:reuters.com&ceid=US:en&hl=en-US&gl=US", "priority": "P0", "enabled": True},
    {"id": 2, "name": "Associated Press", "stance": "center", "region": "international",
     "url": "https://apnews.com/apf-topnews", "priority": "P0", "enabled": True},
    {"id": 3, "name": "BBC News", "stance": "center-left", "region": "uk",
     "url": "https://feeds.bbci.co.uk/news/rss.xml", "priority": "P0", "enabled": True},
    {"id": 4, "name": "The Guardian", "stance": "left", "region": "uk",
     "url": "https://www.theguardian.com/uk/rss", "priority": "P0", "enabled": True},
    {"id": 5, "name": "Financial Times", "stance": "center", "region": "uk",
     "url": "https://www.ft.com/?format=rss", "priority": "P0", "enabled": True},
    {"id": 6, "name": "Bloomberg", "stance": "center", "region": "us",
     "url": "https://www.bloomberg.com/feed/podcast/businessweek.xml", "priority": "P0", "enabled": True},
    # P1 priority - mainstream media
    {"id": 7, "name": "CNN", "stance": "left", "region": "us",
     "url": "http://rss.cnn.com/rss/edition.rss", "priority": "P1", "enabled": True},
    {"id": 8, "name": "Fox News", "stance": "right", "region": "us",
     "url": "https://moxie.foxnews.com/google-publisher/top_stories.xml", "priority": "P1", "enabled": True},
    {"id": 9, "name": "The New York Times", "stance": "left", "region": "us",
     "url": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml", "priority": "P1", "enabled": True},
    {"id": 10, "name": "The Wall Street Journal", "stance": "right", "region": "us",
     "url": "https://feeds.a.dj.com/rss/RSSOpinion.xml", "priority": "P1", "enabled": True},
    {"id": 11, "name": "The Economist", "stance": "center-right", "region": "uk",
     "url": "https://www.economist.com/the-world-this-week/rss.xml", "priority": "P1", "enabled": True},
    {"id": 12, "name": "Al Jazeera", "stance": "center", "region": "international",
     "url": "https://www.aljazeera.com/xml/rss/all.xml", "priority": "P1", "enabled": True},
    # P2 priority - other media
    {"id": 13, "name": "Politico", "stance": "center-left", "region": "us",
     "url": "https://www.politico.com/rss/politics08.xml", "priority": "P2", "enabled": True},
    {"id": 14, "name": "The Hill", "stance": "center", "region": "us",
     "url": "https://thehill.com/feed/", "priority": "P2", "enabled": True},
    {"id": 15, "name": "NPR", "stance": "left", "region": "us",
     "url": "https://feeds.npr.org/1001/rss.xml", "priority": "P2", "enabled": True},
    # Additional sources for broader coverage
    {"id": 16, "name": "BBC World", "stance": "center-left", "region": "uk",
     "url": "https://feeds.bbci.co.uk/news/world/rss.xml", "priority": "P0", "enabled": True},
    {"id": 17, "name": "Reuters World", "stance": "center", "region": "international",
     "url": "https://news.google.com/rss/search?q=when:24h+allinurl:reuters.com+world&ceid=US:en&hl=en-US&gl=US", "priority": "P0", "enabled": True},
    {"id": 18, "name": "Guardian World", "stance": "left", "region": "uk",
     "url": "https://www.theguardian.com/world/rss", "priority": "P1", "enabled": True},
    {"id": 19, "name": "CNN World", "stance": "left", "region": "us",
     "url": "http://rss.cnn.com/rss/edition_world.rss", "priority": "P1", "enabled": True},
    {"id": 20, "name": "ABC News", "stance": "center-left", "region": "us",
     "url": "https://abcnews.go.com/abcnews/topstories", "priority": "P1", "enabled": True},
    {"id": 21, "name": "CBS News", "stance": "center-left", "region": "us",
     "url": "https://www.cbsnews.com/latest/rss/main", "priority": "P1", "enabled": True},
    {"id": 22, "name": "Sky News", "stance": "center", "region": "uk",
     "url": "https://feeds.skynews.com/feeds/rss/world.xml", "priority": "P2", "enabled": True},
    {"id": 23, "name": "France24", "stance": "center", "region": "europe",
     "url": "https://www.france24.com/en/rss", "priority": "P2", "enabled": True},
    {"id": 24, "name": "DW News", "stance": "center", "region": "europe",
     "url": "https://rss.dw.com/rdf/rss-en-all", "priority": "P2", "enabled": True},
    {"id": 25, "name": "The Independent", "stance": "center-left", "region": "uk",
     "url": "https://www.independent.co.uk/news/world/rss", "priority": "P2", "enabled": True},
    {"id": 26, "name": "South China Morning Post", "stance": "center", "region": "asia",
     "url": "https://www.scmp.com/rss/91/feed", "priority": "P2", "enabled": True},
    {"id": 27, "name": "Times of India", "stance": "center", "region": "asia",
     "url": "https://timesofindia.indiatimes.com/rssfeedstopstories.cms", "priority": "P2", "enabled": True},
    {"id": 28, "name": "NHK World", "stance": "center", "region": "asia",
     "url": "https://www3.nhk.or.jp/rss/news/cat0.xml", "priority": "P2", "enabled": True},
    # Entertainment & Sports sources
    {"id": 29, "name": "ESPN", "stance": "center", "region": "us",
     "url": "https://www.espn.com/espn/rss/news", "priority": "P1", "enabled": True},
    {"id": 30, "name": "Variety", "stance": "center", "region": "us",
     "url": "https://variety.com/feed/", "priority": "P1", "enabled": True},
    {"id": 31, "name": "BBC Sport", "stance": "center-left", "region": "uk",
     "url": "https://feeds.bbci.co.uk/sport/rss.xml", "priority": "P1", "enabled": True},
    {"id": 32, "name": "BBC Culture", "stance": "center-left", "region": "uk",
     "url": "https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml", "priority": "P1", "enabled": True},
    # ── Phase A expansion: full-category coverage ──
    # Entertainment: movies / TV / music / celebrity
    {"id": 33, "name": "Hollywood Reporter", "stance": "center", "region": "us",
     "url": "https://www.hollywoodreporter.com/feed/", "priority": "P1", "enabled": True},
    {"id": 34, "name": "Deadline", "stance": "center", "region": "us",
     "url": "https://deadline.com/feed/", "priority": "P1", "enabled": True},
    {"id": 35, "name": "Rolling Stone", "stance": "center-left", "region": "us",
     "url": "https://www.rollingstone.com/feed/", "priority": "P1", "enabled": True},
    {"id": 36, "name": "Pitchfork", "stance": "center", "region": "us",
     "url": "https://pitchfork.com/rss/news/", "priority": "P2", "enabled": True},
    {"id": 37, "name": "Billboard", "stance": "center", "region": "us",
     "url": "https://www.billboard.com/feed/", "priority": "P2", "enabled": True},
    # Sports
    {"id": 38, "name": "Sky Sports", "stance": "center", "region": "uk",
     "url": "https://www.skysports.com/rss/12040", "priority": "P2", "enabled": True},
    # Tech & Gaming
    {"id": 40, "name": "The Verge", "stance": "center-left", "region": "us",
     "url": "https://www.theverge.com/rss/index.xml", "priority": "P1", "enabled": True},
    {"id": 41, "name": "Ars Technica", "stance": "center", "region": "us",
     "url": "https://feeds.arstechnica.com/arstechnica/index", "priority": "P1", "enabled": True},
    {"id": 42, "name": "TechCrunch", "stance": "center", "region": "us",
     "url": "https://techcrunch.com/feed/", "priority": "P1", "enabled": True},
    {"id": 43, "name": "Wired", "stance": "center-left", "region": "us",
     "url": "https://www.wired.com/feed/rss", "priority": "P1", "enabled": True},
    {"id": 44, "name": "Polygon", "stance": "center", "region": "us",
     "url": "https://www.polygon.com/rss/index.xml", "priority": "P2", "enabled": True},
    {"id": 45, "name": "IGN", "stance": "center", "region": "us",
     "url": "https://feeds.ign.com/ign/all", "priority": "P2", "enabled": True},
    {"id": 57, "name": "Eurogamer", "stance": "center", "region": "uk",
     "url": "https://www.eurogamer.net/?format=rss", "priority": "P2", "enabled": True},
    {"id": 58, "name": "GameSpot", "stance": "center", "region": "us",
     "url": "https://www.gamespot.com/feeds/mashup/", "priority": "P2", "enabled": True},
    {"id": 59, "name": "Rock Paper Shotgun", "stance": "center", "region": "uk",
     "url": "https://www.rockpapershotgun.com/feed", "priority": "P2", "enabled": True},
    # Science
    {"id": 48, "name": "New Scientist", "stance": "center", "region": "uk",
     "url": "https://www.newscientist.com/feed/home/", "priority": "P1", "enabled": True},
    {"id": 49, "name": "Phys.org", "stance": "center", "region": "international",
     "url": "https://phys.org/rss-feed/", "priority": "P2", "enabled": True},
    {"id": 50, "name": "Ars Technica Science", "stance": "center", "region": "us",
     "url": "https://feeds.arstechnica.com/arstechnica/science", "priority": "P2", "enabled": True},
    {"id": 60, "name": "Nature News", "stance": "center", "region": "uk",
     "url": "https://www.nature.com/nature.rss", "priority": "P1", "enabled": True},
    {"id": 61, "name": "Quanta Magazine", "stance": "center", "region": "us",
     "url": "https://www.quantamagazine.org/feed/", "priority": "P1", "enabled": True},
    # Culture / Lifestyle
    {"id": 51, "name": "The Atlantic", "stance": "center-left", "region": "us",
     "url": "https://www.theatlantic.com/feed/best-of/", "priority": "P1", "enabled": True},
    {"id": 52, "name": "The New Yorker", "stance": "left", "region": "us",
     "url": "https://www.newyorker.com/feed/everything", "priority": "P1", "enabled": True},
    {"id": 53, "name": "Vogue", "stance": "center", "region": "us",
     "url": "https://www.vogue.com/feed/rss", "priority": "P2", "enabled": True},
    {"id": 54, "name": "GQ", "stance": "center", "region": "us",
     "url": "https://www.gq.com/feed/rss", "priority": "P2", "enabled": True},
    # Food
    {"id": 55, "name": "Eater", "stance": "center", "region": "us",
     "url": "https://www.eater.com/rss/index.xml", "priority": "P2", "enabled": True},
    {"id": 56, "name": "Bon Appétit", "stance": "center", "region": "us",
     "url": "https://www.bonappetit.com/feed/rss", "priority": "P2", "enabled": True},
]

# Reddit sources (source_id 101+)
REDDIT_SOURCES = [
    {"id": 101, "name": "Reddit r/all", "stance": "center", "region": "international",
     "subreddit": "all", "priority": "P1", "enabled": True},
    {"id": 102, "name": "Reddit r/worldnews", "stance": "center", "region": "international",
     "subreddit": "worldnews", "priority": "P1", "enabled": True},
    {"id": 103, "name": "Reddit r/news", "stance": "center", "region": "us",
     "subreddit": "news", "priority": "P1", "enabled": True},
    {"id": 104, "name": "Reddit r/technology", "stance": "center", "region": "international",
     "subreddit": "technology", "priority": "P1", "enabled": True},
    {"id": 106, "name": "Reddit r/entertainment", "stance": "center", "region": "international",
     "subreddit": "entertainment", "priority": "P1", "enabled": True},
    {"id": 107, "name": "Reddit r/movies", "stance": "center", "region": "international",
     "subreddit": "movies", "priority": "P1", "enabled": True},
    {"id": 108, "name": "Reddit r/sports", "stance": "center", "region": "international",
     "subreddit": "sports", "priority": "P1", "enabled": True},
    {"id": 109, "name": "Reddit r/science", "stance": "center", "region": "international",
     "subreddit": "science", "priority": "P1", "enabled": True},
    {"id": 110, "name": "Reddit r/business", "stance": "center", "region": "international",
     "subreddit": "business", "priority": "P1", "enabled": True},
    # Phase A expansion — active entertainment / hobby / lifestyle subs
    {"id": 112, "name": "Reddit r/popculturechat", "stance": "center", "region": "us",
     "subreddit": "popculturechat", "priority": "P2", "enabled": True},
    {"id": 113, "name": "Reddit r/television", "stance": "center", "region": "international",
     "subreddit": "television", "priority": "P2", "enabled": True},
    {"id": 114, "name": "Reddit r/Music", "stance": "center", "region": "international",
     "subreddit": "Music", "priority": "P2", "enabled": True},
    {"id": 115, "name": "Reddit r/gaming", "stance": "center", "region": "international",
     "subreddit": "gaming", "priority": "P2", "enabled": True},
    {"id": 116, "name": "Reddit r/Games", "stance": "center", "region": "international",
     "subreddit": "Games", "priority": "P2", "enabled": True},
    {"id": 117, "name": "Reddit r/nba", "stance": "center", "region": "us",
     "subreddit": "nba", "priority": "P2", "enabled": True},
    {"id": 118, "name": "Reddit r/soccer", "stance": "center", "region": "international",
     "subreddit": "soccer", "priority": "P2", "enabled": True},
    {"id": 119, "name": "Reddit r/books", "stance": "center", "region": "international",
     "subreddit": "books", "priority": "P2", "enabled": True},
    {"id": 120, "name": "Reddit r/food", "stance": "center", "region": "international",
     "subreddit": "food", "priority": "P2", "enabled": True},
    {"id": 121, "name": "Reddit r/Futurology", "stance": "center", "region": "international",
     "subreddit": "Futurology", "priority": "P2", "enabled": True},
    {"id": 122, "name": "Reddit r/space", "stance": "center", "region": "international",
     "subreddit": "space", "priority": "P2", "enabled": True},
]

# Hacker News source (source_id 105)
HN_SOURCE = {"id": 105, "name": "Hacker News", "url": "https://news.ycombinator.com/",
             "stance": "center", "region": "international", "priority": "P1", "enabled": True}

# Bluesky source (source_id 111)
BLUESKY_SOURCE = {"id": 111, "name": "Bluesky", "url": "https://bsky.app/",
                  "stance": "center", "region": "international", "priority": "P1", "enabled": True}

ALL_SOURCES = RSS_SOURCES + REDDIT_SOURCES + [HN_SOURCE, BLUESKY_SOURCE]


def get_sources_by_priority(priority: str = "P0") -> List[Dict]:
    return [s for s in RSS_SOURCES if s["priority"] == priority and s["enabled"]]


def get_all_enabled_sources() -> List[Dict]:
    return [s for s in RSS_SOURCES if s["enabled"]]
