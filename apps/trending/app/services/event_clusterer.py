"""
事件去重聚类服务

功能：
- TF-IDF + 余弦相似度计算
- 事件中心向量
- 增量更新
- 测试验证
"""
from typing import List, Dict, Optional, Tuple, Set
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
import math
import re
from collections import Counter

from app.models.article import Article
from app.models.event import Event
from app.models.source import Source
from app.config import settings


class TextPreprocessor:
    """文本预处理器"""
    
    # 英文停用词（简化版）
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
        """
        清洗文本
        
        Args:
            text: 原始文本
            
        Returns:
            清洗后的文本
        """
        if not text:
            return ""
        
        # 转小写
        text = text.lower()
        
        # 移除特殊字符，保留字母、数字、空格
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        
        # 移除多余空格
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    @staticmethod
    def tokenize(text: str) -> List[str]:
        """
        分词
        
        Args:
            text: 文本
            
        Returns:
            词列表
        """
        if not text:
            return []
        
        # 简单空格分词
        words = text.split()
        
        # 移除停用词和短词
        words = [w for w in words if w not in TextPreprocessor.STOP_WORDS and len(w) > 2]
        
        return words
    
    @staticmethod
    def extract_keywords(text: str, top_n: int = 20) -> List[str]:
        """
        提取关键词（基于词频）
        
        Args:
            text: 文本
            top_n: 返回前 N 个关键词
            
        Returns:
            关键词列表
        """
        words = TextPreprocessor.tokenize(text)
        
        if not words:
            return []
        
        # 统计词频
        word_counts = Counter(words)
        
        # 返回 top N
        return [word for word, count in word_counts.most_common(top_n)]


class TFIDFVectorizer:
    """TF-IDF 向量化工具"""
    
    def __init__(self):
        """初始化向量化工具"""
        self.idf: Dict[str, float] = {}  # 词项的 IDF 值
        self.vocabulary: Set[str] = set()  # 词汇表
    
    def fit(self, documents: List[str]):
        """
        拟合文档集，计算 IDF
        
        Args:
            documents: 文档列表
        """
        # 统计每个词项出现在多少文档中
        doc_freq: Dict[str, int] = {}
        n_docs = len(documents)
        
        for doc in documents:
            words = set(TextPreprocessor.tokenize(doc))
            for word in words:
                doc_freq[word] = doc_freq.get(word, 0) + 1
                self.vocabulary.add(word)
        
        # 计算 IDF: log(N / df)
        for word, df in doc_freq.items():
            self.idf[word] = math.log((n_docs + 1) / (df + 1)) + 1
    
    def transform(self, document: str) -> Dict[str, float]:
        """
        将文档转换为 TF-IDF 向量
        
        Args:
            document: 文档文本
            
        Returns:
            TF-IDF 向量（稀疏表示：词->权重）
        """
        words = TextPreprocessor.tokenize(document)
        
        if not words:
            return {}
        
        # 计算 TF（词频）
        tf = Counter(words)
        total_words = len(words)
        
        # 计算 TF-IDF
        tfidf = {}
        for word, count in tf.items():
            tf_score = count / total_words
            idf_score = self.idf.get(word, 1.0)
            tfidf[word] = tf_score * idf_score
        
        return tfidf
    
    def fit_transform(self, documents: List[str]) -> List[Dict[str, float]]:
        """
        拟合并转换文档集
        
        Args:
            documents: 文档列表
            
        Returns:
            TF-IDF 向量列表
        """
        self.fit(documents)
        return [self.transform(doc) for doc in documents]


class EventClusterer:
    """事件聚类器"""
    
    def __init__(self, db: Session):
        """
        初始化聚类器
        
        Args:
            db: 数据库会话
        """
        self.db = db
        self.similarity_threshold = settings.CLUSTER_SIMILARITY_THRESHOLD
        self.top_keywords = settings.CLUSTER_TOP_KEYWORDS
        self.vectorizer = TFIDFVectorizer()
    
    def cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """
        计算两个向量的余弦相似度
        
        Args:
            vec1: 向量 1（稀疏表示）
            vec2: 向量 2（稀疏表示）
            
        Returns:
            余弦相似度（0-1）
        """
        if not vec1 or not vec2:
            return 0.0
        
        # 找到共同的词
        common_words = set(vec1.keys()) & set(vec2.keys())
        
        if not common_words:
            return 0.0
        
        # 计算点积
        dot_product = sum(vec1[word] * vec2[word] for word in common_words)
        
        # 计算模长
        magnitude1 = math.sqrt(sum(v ** 2 for v in vec1.values()))
        magnitude2 = math.sqrt(sum(v ** 2 for v in vec2.values()))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        # 余弦相似度
        similarity = dot_product / (magnitude1 * magnitude2)
        
        return min(max(similarity, 0.0), 1.0)
    
    def extract_event_vector(self, event: Event) -> str:
        """
        提取事件的文本表示（用于向量化）
        
        Args:
            event: 事件对象
            
        Returns:
            组合文本
        """
        texts = []
        
        # 事件标题（权重最高）
        if event.title:
            texts.append(event.title)
            texts.append(event.title)  # 标题重复一次以增加权重
        
        # 事件摘要
        if event.summary:
            texts.append(event.summary)
        
        # 关键词
        if event.keywords:
            texts.append(' '.join(event.keywords))
        
        # 相关文章标题（前 10 篇）
        if event.articles:
            article_titles = [a.title for a in event.articles[:10]]
            texts.extend(article_titles)
        
        # 相关文章摘要（前 5 篇）
        if event.articles:
            article_summaries = [a.summary for a in event.articles[:5] if a.summary]
            texts.extend(article_summaries)
        
        return ' '.join(texts)
    
    def extract_article_vector(self, article: Article) -> str:
        """
        提取文章的文本表示
        
        Args:
            article: 文章对象
            
        Returns:
            组合文本
        """
        texts = []
        
        # 标题（权重高）
        if article.title:
            texts.append(article.title)
            texts.append(article.title)
        
        # 摘要
        if article.summary:
            texts.append(article.summary)
        
        # 内容（如果有）
        if article.content:
            texts.append(article.content[:1000])  # 限制长度
        
        return ' '.join(texts)
    
    def calculate_event_centroid(self, event: Event) -> Dict[str, float]:
        """
        计算事件的中心向量
        
        Args:
            event: 事件对象
            
        Returns:
            中心向量
        """
        event_text = self.extract_event_vector(event)
        return self.vectorizer.transform(event_text)
    
    def find_similar_events(self, text: str, limit: int = 10, min_similarity: float = None) -> List[Tuple[Event, float]]:
        """
        查找与给定文本相似的事件
        
        Args:
            text: 查询文本
            limit: 返回数量
            min_similarity: 最小相似度阈值
            
        Returns:
            (事件，相似度) 列表
        """
        if min_similarity is None:
            min_similarity = self.similarity_threshold
        
        # 获取活跃事件（最近 7 天，有热度的）
        cutoff_time = datetime.utcnow() - timedelta(days=7)
        events = self.db.query(Event).filter(
            and_(
                Event.created_at >= cutoff_time,
                Event.heat_score > 0
            )
        ).all()
        
        if not events:
            return []
        
        # 构建文档集（用于计算 IDF）
        documents = [self.extract_event_vector(e) for e in events]
        documents.append(text)  # 加入查询文本
        
        # 拟合向量化工具
        self.vectorizer.fit(documents)
        
        # 转换查询文本
        query_vec = self.vectorizer.transform(text)
        
        # 计算相似度
        similarities = []
        for event in events:
            event_vec = self.calculate_event_centroid(event)
            similarity = self.cosine_similarity(query_vec, event_vec)
            
            if similarity >= min_similarity:
                similarities.append((event, similarity))
        
        # 按相似度排序
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:limit]
    
    def cluster_articles_to_events(self, articles: List[Article]) -> Dict[Event, List[Article]]:
        """
        将文章聚类到现有事件
        
        Args:
            articles: 文章列表
            
        Returns:
            {事件：相关文章列表}
        """
        if not articles:
            return {}
        
        # 获取活跃事件
        cutoff_time = datetime.utcnow() - timedelta(days=7)
        events = self.db.query(Event).filter(
            and_(
                Event.created_at >= cutoff_time,
                Event.heat_score > 0
            )
        ).all()
        
        if not events:
            return {}
        
        # 构建文档集
        documents = [self.extract_event_vector(e) for e in events]
        article_texts = [self.extract_article_vector(a) for a in articles]
        all_docs = documents + article_texts
        
        # 拟合向量化工具
        self.vectorizer.fit(all_docs)
        
        # 转换所有文档
        event_vectors = {e: self.calculate_event_centroid(e) for e in events}
        article_vectors = {a: self.vectorizer.transform(self.extract_article_vector(a)) for a in articles}
        
        # 为每篇文章找到最匹配的事件
        clustering: Dict[Event, List[Article]] = {e: [] for e in events}
        
        for article in articles:
            article_vec = article_vectors[article]
            
            best_event = None
            best_similarity = 0
            
            for event, event_vec in event_vectors.items():
                similarity = self.cosine_similarity(article_vec, event_vec)
                
                if similarity > best_similarity and similarity >= self.similarity_threshold:
                    best_similarity = similarity
                    best_event = event
            
            if best_event:
                clustering[best_event].append(article)
        
        # 过滤掉没有文章的事件
        clustering = {e: articles for e, articles in clustering.items() if articles}
        
        return clustering
    
    def detect_new_event(self, article: Article) -> Tuple[bool, Optional[Event], float]:
        """
        检测文章是否属于新事件
        
        Args:
            article: 文章对象
            
        Returns:
            (是否新事件，匹配的事件，最高相似度)
        """
        article_text = self.extract_article_vector(article)
        
        # 查找相似事件
        similar_events = self.find_similar_events(article_text, limit=5)
        
        if not similar_events:
            return True, None, 0.0
        
        best_event, best_similarity = similar_events[0]
        
        if best_similarity < self.similarity_threshold:
            return True, None, best_similarity
        else:
            return False, best_event, best_similarity
    
    def create_event_from_articles(self, articles: List[Article], source_id: Optional[int] = None) -> Event:
        """
        从文章列表创建新事件
        
        Args:
            articles: 文章列表
            source_id: 首发源 ID（可选）
            
        Returns:
            新创建的事件
        """
        if not articles:
            raise ValueError("文章列表不能为空")
        
        # 提取关键词
        all_texts = [self.extract_article_vector(a) for a in articles]
        combined_text = ' '.join(all_texts)
        keywords = TextPreprocessor.extract_keywords(combined_text, self.top_keywords)
        
        # 使用第一篇文章作为事件基础
        first_article = articles[0]
        
        # 创建事件
        event = Event(
            title=first_article.title,
            summary=first_article.summary,
            keywords=keywords,
            source_id=source_id or first_article.source_id,
            article_count=len(articles),
            media_count=len(set(a.source_id for a in articles)),
        )
        
        self.db.add(event)
        self.db.flush()
        
        # 关联文章
        for article in articles:
            article.event_id = event.id
        
        self.db.commit()
        self.db.refresh(event)
        
        return event
    
    def merge_events(self, event1: Event, event2: Event) -> Event:
        """
        合并两个事件
        
        Args:
            event1: 事件 1
            event2: 事件 2（将被删除）
            
        Returns:
            合并后的事件
        """
        # 将所有文章移到 event1
        for article in event2.articles:
            article.event_id = event1.id
        
        # 更新统计
        event1.article_count = event1.article_count + event2.article_count
        event1.media_count = len(set(
            [a.source_id for a in event1.articles] + 
            [a.source_id for a in event2.articles]
        ))
        
        # 合并关键词
        all_keywords = list(set((event1.keywords or []) + (event2.keywords or [])))
        event1.keywords = all_keywords[:self.top_keywords]
        
        # 删除 event2
        self.db.delete(event2)
        self.db.commit()
        self.db.refresh(event1)
        
        return event1
    
    def find_duplicate_events(self, time_window_days: int = 3) -> List[Tuple[Event, Event, float]]:
        """
        查找重复的事件
        
        Args:
            time_window_days: 时间窗口（天）
            
        Returns:
            (事件 1, 事件 2, 相似度) 列表
        """
        cutoff_time = datetime.utcnow() - timedelta(days=time_window_days)
        events = self.db.query(Event).filter(
            and_(
                Event.created_at >= cutoff_time,
                Event.heat_score > 0
            )
        ).all()
        
        if len(events) < 2:
            return []
        
        # 构建文档集
        documents = [self.extract_event_vector(e) for e in events]
        
        # 拟合向量化工具
        self.vectorizer.fit(documents)
        
        # 计算所有事件对的相似度
        duplicates = []
        n = len(events)
        
        for i in range(n):
            vec1 = self.calculate_event_centroid(events[i])
            
            for j in range(i + 1, n):
                vec2 = self.calculate_event_centroid(events[j])
                similarity = self.cosine_similarity(vec1, vec2)
                
                if similarity >= self.similarity_threshold:
                    duplicates.append((events[i], events[j], similarity))
        
        # 按相似度排序
        duplicates.sort(key=lambda x: x[2], reverse=True)
        
        return duplicates
    
    def incremental_update(self, new_articles: List[Article]) -> Dict:
        """
        增量更新事件聚类
        
        Args:
            new_articles: 新文章列表
            
        Returns:
            更新结果统计
        """
        result = {
            "new_articles_count": len(new_articles),
            "clustered_count": 0,
            "new_events_count": 0,
            "merged_events_count": 0,
        }
        
        if not new_articles:
            return result
        
        # 为每篇文章检测是否属于新事件
        new_event_articles: List[Article] = []
        
        for article in new_articles:
            is_new, matched_event, similarity = self.detect_new_event(article)
            
            if is_new:
                new_event_articles.append(article)
            else:
                # 添加到现有事件
                article.event_id = matched_event.id
                matched_event.article_count += 1
                matched_event.media_count = len(set(
                    [a.source_id for a in matched_event.articles] + [article.source_id]
                ))
                result["clustered_count"] += 1
        
        # 为新事件创建聚类
        if new_event_articles:
            # 按时间分组（相近时间的文章可能属于同一事件）
            new_event_articles.sort(key=lambda a: a.published_at)
            
            current_group = [new_event_articles[0]]
            
            for article in new_event_articles[1:]:
                # 如果与当前组的文章时间差在 2 小时内，加入当前组
                time_diff = (article.published_at - current_group[-1].published_at).total_seconds() / 3600
                
                if time_diff < 2:
                    current_group.append(article)
                else:
                    # 创建新事件
                    if current_group:
                        self.create_event_from_articles(current_group)
                        result["new_events_count"] += 1
                    current_group = [article]
            
            # 处理最后一组
            if current_group:
                self.create_event_from_articles(current_group)
                result["new_events_count"] += 1
        
        # 检测并合并重复事件
        duplicates = self.find_duplicate_events()
        for event1, event2, similarity in duplicates[:5]:  # 最多合并 5 对
            self.merge_events(event1, event2)
            result["merged_events_count"] += 1
        
        self.db.commit()
        
        return result
    
    def update_event_keywords(self, event: Event) -> List[str]:
        """
        更新事件的关键词
        
        Args:
            event: 事件对象
            
        Returns:
            新关键词列表
        """
        # 收集所有文章的文本
        texts = []
        
        if event.title:
            texts.append(event.title)
        
        if event.summary:
            texts.append(event.summary)
        
        for article in event.articles[:20]:  # 最多 20 篇
            if article.title:
                texts.append(article.title)
            if article.summary:
                texts.append(article.summary)
        
        combined_text = ' '.join(texts)
        keywords = TextPreprocessor.extract_keywords(combined_text, self.top_keywords)
        
        event.keywords = keywords
        self.db.commit()
        
        return keywords


def cluster_new_articles(db: Session, articles: Optional[List[Article]] = None) -> Dict:
    """
    聚类新文章（便捷函数）
    
    Args:
        db: 数据库会话
        articles: 文章列表（None 则获取未处理的文章）
        
    Returns:
        聚类结果统计
    """
    clusterer = EventClusterer(db)
    
    if articles is None:
        # 获取未处理的文章
        articles = db.query(Article).filter(
            and_(
                Article.is_processed == False,
                Article.event_id.is_(None)
            )
        ).all()
    
    # 增量更新
    result = clusterer.incremental_update(articles)
    
    # 标记已处理
    for article in articles:
        article.is_processed = True
    
    db.commit()
    
    return result
