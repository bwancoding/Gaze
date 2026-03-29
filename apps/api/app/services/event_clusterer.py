"""
Event deduplication and clustering service

Features:
- TF-IDF + cosine similarity computation
- Event centroid vectors
- Incremental updates
"""
from typing import List, Dict, Optional, Tuple, Set
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_
import math
import re
from collections import Counter

from app.models.trending import TrendingArticle, TrendingEvent, TrendingSource
from app.services.trending_config import CLUSTER_SIMILARITY_THRESHOLD, CLUSTER_TOP_KEYWORDS, CATEGORY_KEYWORDS


class TextPreprocessor:
    """Text preprocessor"""

    STOP_WORDS = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
        'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
        'this', 'that', 'these', 'those', 'it', 'its', 'as', 'if', 'when',
        'than', 'because', 'while', 'although', 'though', 'after', 'before',
        'about', 'into', 'through', 'during', 'without', 'against', 'between',
        'under', 'over', 'above', 'below', 'up', 'down', 'out', 'off', 'again',
        'further', 'then', 'once', 'here', 'there', 'all', 'any', 'both',
        'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor',
        'not', 'only', 'own', 'same', 'so', 'just', 'also', 'now', 'very'
    }

    @staticmethod
    def clean_text(text: str) -> str:
        if not text:
            return ""
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    @staticmethod
    def tokenize(text: str) -> List[str]:
        if not text:
            return []
        text = TextPreprocessor.clean_text(text)
        words = text.split()
        return [w for w in words if w not in TextPreprocessor.STOP_WORDS and len(w) > 2]

    @staticmethod
    def extract_keywords(text: str, top_n: int = 20) -> List[str]:
        words = TextPreprocessor.tokenize(text)
        if not words:
            return []
        word_counts = Counter(words)
        return [word for word, _ in word_counts.most_common(top_n)]


class TFIDFVectorizer:
    """TF-IDF vectorizer"""

    def __init__(self):
        self.idf: Dict[str, float] = {}
        self.vocabulary: Set[str] = set()

    def fit(self, documents: List[str]):
        doc_freq: Dict[str, int] = {}
        n_docs = len(documents)
        for doc in documents:
            words = set(TextPreprocessor.tokenize(doc))
            for word in words:
                doc_freq[word] = doc_freq.get(word, 0) + 1
                self.vocabulary.add(word)
        for word, df in doc_freq.items():
            self.idf[word] = math.log((n_docs + 1) / (df + 1)) + 1

    def transform(self, document: str) -> Dict[str, float]:
        words = TextPreprocessor.tokenize(document)
        if not words:
            return {}
        tf = Counter(words)
        total_words = len(words)
        tfidf = {}
        for word, count in tf.items():
            tf_score = count / total_words
            idf_score = self.idf.get(word, 1.0)
            tfidf[word] = tf_score * idf_score
        return tfidf

    def fit_transform(self, documents: List[str]) -> List[Dict[str, float]]:
        self.fit(documents)
        return [self.transform(doc) for doc in documents]


class EventClusterer:
    """Event clusterer"""

    def __init__(self, db: Session):
        self.db = db
        self.similarity_threshold = CLUSTER_SIMILARITY_THRESHOLD
        self.top_keywords = CLUSTER_TOP_KEYWORDS
        self.vectorizer = TFIDFVectorizer()

    def cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        if not vec1 or not vec2:
            return 0.0
        common_words = set(vec1.keys()) & set(vec2.keys())
        if not common_words:
            return 0.0
        dot_product = sum(vec1[word] * vec2[word] for word in common_words)
        magnitude1 = math.sqrt(sum(v ** 2 for v in vec1.values()))
        magnitude2 = math.sqrt(sum(v ** 2 for v in vec2.values()))
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        similarity = dot_product / (magnitude1 * magnitude2)
        return min(max(similarity, 0.0), 1.0)

    def extract_event_vector(self, event: TrendingEvent) -> str:
        texts = []
        if event.title:
            texts.extend([event.title, event.title])  # Title weight x2
        if event.summary:
            texts.append(event.summary)
        if event.keywords:
            texts.append(' '.join(event.keywords))
        if event.articles:
            texts.extend(a.title for a in event.articles[:10])
            texts.extend(a.summary for a in event.articles[:5] if a.summary)
        return ' '.join(texts)

    def extract_article_vector(self, article: TrendingArticle) -> str:
        texts = []
        if article.title:
            texts.extend([article.title, article.title])
        if article.summary:
            texts.append(article.summary)
        if article.content:
            texts.append(article.content[:1000])
        return ' '.join(texts)

    def calculate_event_centroid(self, event: TrendingEvent) -> Dict[str, float]:
        event_text = self.extract_event_vector(event)
        return self.vectorizer.transform(event_text)

    def find_similar_events(self, text: str, limit: int = 10,
                            min_similarity: float = None) -> List[Tuple[TrendingEvent, float]]:
        if min_similarity is None:
            min_similarity = self.similarity_threshold

        cutoff_time = datetime.utcnow() - timedelta(days=7)
        events = self.db.query(TrendingEvent).filter(
            and_(TrendingEvent.created_at >= cutoff_time, TrendingEvent.heat_score > 0)
        ).all()

        if not events:
            return []

        documents = [self.extract_event_vector(e) for e in events]
        documents.append(text)
        self.vectorizer.fit(documents)

        query_vec = self.vectorizer.transform(text)
        similarities = []
        for event in events:
            event_vec = self.calculate_event_centroid(event)
            similarity = self.cosine_similarity(query_vec, event_vec)
            if similarity >= min_similarity:
                similarities.append((event, similarity))

        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:limit]

    def detect_new_event(self, article: TrendingArticle) -> Tuple[bool, Optional[TrendingEvent], float]:
        article_text = self.extract_article_vector(article)
        similar_events = self.find_similar_events(article_text, limit=5)
        if not similar_events:
            return True, None, 0.0
        best_event, best_similarity = similar_events[0]
        if best_similarity < self.similarity_threshold:
            return True, None, best_similarity
        return False, best_event, best_similarity

    def classify_category(self, text: str, title: str = "") -> Optional[str]:
        text_lower = text.lower()
        title_lower = title.lower() if title else ""
        scores: Dict[str, float] = {}
        for category, keywords in CATEGORY_KEYWORDS.items():
            score = 0.0
            for kw in keywords:
                if kw in title_lower:
                    score += 3.0  # Title matches count 3x
                elif kw in text_lower:
                    score += 1.0
            if score > 0:
                scores[category] = score
        if not scores:
            return None
        return max(scores, key=scores.get)

    def create_event_from_articles(self, articles: List[TrendingArticle],
                                   source_id: Optional[int] = None) -> TrendingEvent:
        if not articles:
            raise ValueError("Article list cannot be empty")

        all_texts = [self.extract_article_vector(a) for a in articles]
        combined_text = ' '.join(all_texts)
        keywords = TextPreprocessor.extract_keywords(combined_text, self.top_keywords)

        first_article = articles[0]
        category = self.classify_category(combined_text, title=first_article.title or "")

        event = TrendingEvent(
            title=first_article.title,
            summary=first_article.summary,
            keywords=keywords,
            category=category,
            source_id=source_id or first_article.source_id,
            article_count=len(articles),
            media_count=len(set(a.source_id for a in articles)),
        )

        self.db.add(event)
        self.db.flush()

        for article in articles:
            article.event_id = event.id

        self.db.commit()
        self.db.refresh(event)
        return event

    def merge_events(self, event1: TrendingEvent, event2: TrendingEvent) -> TrendingEvent:
        for article in event2.articles:
            article.event_id = event1.id

        event1.article_count = event1.article_count + event2.article_count
        event1.media_count = len(set(
            [a.source_id for a in event1.articles] +
            [a.source_id for a in event2.articles]
        ))

        all_keywords = list(set((event1.keywords or []) + (event2.keywords or [])))
        event1.keywords = all_keywords[:self.top_keywords]

        self.db.delete(event2)
        self.db.commit()
        self.db.refresh(event1)
        return event1

    def find_duplicate_events(self, time_window_days: int = 3) -> List[Tuple[TrendingEvent, TrendingEvent, float]]:
        cutoff_time = datetime.utcnow() - timedelta(days=time_window_days)
        events = self.db.query(TrendingEvent).filter(
            and_(TrendingEvent.created_at >= cutoff_time, TrendingEvent.heat_score > 0)
        ).all()

        if len(events) < 2:
            return []

        documents = [self.extract_event_vector(e) for e in events]
        self.vectorizer.fit(documents)

        duplicates = []
        n = len(events)
        for i in range(n):
            vec1 = self.calculate_event_centroid(events[i])
            for j in range(i + 1, n):
                vec2 = self.calculate_event_centroid(events[j])
                similarity = self.cosine_similarity(vec1, vec2)
                if similarity >= self.similarity_threshold:
                    duplicates.append((events[i], events[j], similarity))

        duplicates.sort(key=lambda x: x[2], reverse=True)
        return duplicates

    def incremental_update(self, new_articles: List[TrendingArticle]) -> Dict:
        result = {
            "new_articles_count": len(new_articles),
            "clustered_count": 0,
            "new_events_count": 0,
            "merged_events_count": 0,
        }

        if not new_articles:
            return result

        new_event_articles: List[TrendingArticle] = []

        for article in new_articles:
            is_new, matched_event, similarity = self.detect_new_event(article)
            if is_new:
                new_event_articles.append(article)
            else:
                article.event_id = matched_event.id
                matched_event.article_count += 1
                matched_event.media_count = len(set(
                    [a.source_id for a in matched_event.articles] + [article.source_id]
                ))
                result["clustered_count"] += 1

        if new_event_articles:
            new_event_articles.sort(key=lambda a: a.published_at)
            current_group = [new_event_articles[0]]

            for article in new_event_articles[1:]:
                time_diff = (article.published_at - current_group[-1].published_at).total_seconds() / 3600
                if time_diff < 2:
                    current_group.append(article)
                else:
                    if current_group:
                        self.create_event_from_articles(current_group)
                        result["new_events_count"] += 1
                    current_group = [article]

            if current_group:
                self.create_event_from_articles(current_group)
                result["new_events_count"] += 1

        duplicates = self.find_duplicate_events()
        for event1, event2, similarity in duplicates[:5]:
            self.merge_events(event1, event2)
            result["merged_events_count"] += 1

        self.db.commit()
        return result


def backfill_categories(db: Session) -> Dict:
    """Assign categories to existing uncategorized trending events."""
    clusterer = EventClusterer(db)
    events = db.query(TrendingEvent).filter(TrendingEvent.category.is_(None)).all()
    updated = 0
    for event in events:
        text = clusterer.extract_event_vector(event)
        category = clusterer.classify_category(text, title=event.title or "")
        if category:
            event.category = category
            updated += 1
    db.commit()
    return {"total_uncategorized": len(events), "categorized": updated}


def cluster_new_articles(db: Session, articles: Optional[List[TrendingArticle]] = None) -> Dict:
    """Convenience function: cluster new articles"""
    clusterer = EventClusterer(db)

    if articles is None:
        articles = db.query(TrendingArticle).filter(
            and_(
                TrendingArticle.is_processed == False,
                TrendingArticle.event_id.is_(None)
            )
        ).all()

    result = clusterer.incremental_update(articles)

    for article in articles:
        article.is_processed = True
    db.commit()

    return result
