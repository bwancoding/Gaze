"""
Timeline Summarizer — builds one "stage development" timeline entry from a
batch of articles that were just merged into (or created) a TrendingEvent.

Used by news_aggregator when:
- A new topic cluster is merged into an existing event (continuation)
- A new event is created (initial entry)

Each entry captures "what new happened in this pipeline run" for the story.
"""
import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


def _get_ai_client():
    """Create OpenAI-compatible client for SiliconCloud (mirrors ai_service.py)."""
    api_key = os.getenv("AI_API_KEY")
    if not api_key:
        return None
    try:
        from openai import AsyncOpenAI
        return AsyncOpenAI(
            base_url=os.getenv("AI_BASE_URL", "https://api.siliconflow.cn/v1"),
            api_key=api_key,
        )
    except Exception as e:
        logger.warning(f"timeline_summarizer: failed to init AI client: {e}")
        return None


def _fallback_entry(event_title: str, articles: List) -> Dict:
    """Rule-based fallback when LLM is unavailable or fails."""
    if not articles:
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "title": f"{event_title[:60]} — 新进展",
            "summary": "",
            "article_count": 0,
            "sources": [],
            "top_article_url": "",
        }
    top = max(articles, key=lambda a: getattr(a, "heat_score", 0) or 0)
    sources = list({
        getattr(getattr(a, "source", None), "name", None) or ""
        for a in articles
        if getattr(getattr(a, "source", None), "name", None)
    })[:5]
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "title": (getattr(top, "title", "") or event_title)[:120],
        "summary": (getattr(top, "summary", "") or "")[:400],
        "article_count": len(articles),
        "sources": sources,
        "top_article_url": getattr(top, "url", "") or "",
    }


async def summarize_batch(
    event_title: str,
    articles: List,
    is_initial: bool = False,
) -> Dict:
    """
    Summarize a batch of articles into one timeline entry.

    Args:
        event_title: The parent event's title (context for the LLM)
        articles: List of TrendingArticle objects just linked to the event
        is_initial: True if this is the first entry for a new event
    """
    if not articles:
        return _fallback_entry(event_title, articles)

    client = _get_ai_client()
    if client is None:
        return _fallback_entry(event_title, articles)

    # Build compact context: top ~12 articles by heat
    sorted_articles = sorted(
        articles,
        key=lambda a: getattr(a, "heat_score", 0) or 0,
        reverse=True,
    )[:12]

    lines = []
    for a in sorted_articles:
        src = getattr(getattr(a, "source", None), "name", None) or "?"
        title = (getattr(a, "title", "") or "").strip()
        summary = (getattr(a, "summary", "") or "").strip()[:200]
        lines.append(f"- [{src}] {title} — {summary}")
    articles_block = "\n".join(lines)

    all_sources = list({
        getattr(getattr(a, "source", None), "name", None) or ""
        for a in articles
        if getattr(getattr(a, "source", None), "name", None)
    })[:8]

    stage_hint = "首次出现" if is_initial else "最新进展"
    prompt = f"""你是新闻时间线编辑。下面是事件《{event_title}》的一批新报道（{stage_hint}，共 {len(articles)} 篇）。

请总结本批次的核心进展，输出严格的 JSON，字段：
- "title": 一句话进展标题，中文，<25 字，要具体（谁做了什么/发生了什么）
- "summary": 2-3 句摘要，中文，<200 字，突出本批次的新信息，不要泛泛重复事件背景

报道列表：
{articles_block}

只输出 JSON，不要额外文字。"""

    try:
        response = await asyncio.wait_for(
            client.chat.completions.create(
                model=os.getenv("AI_MODEL", "deepseek-ai/DeepSeek-V3"),
                messages=[
                    {"role": "system", "content": "You are a news timeline editor. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.4,
                response_format={"type": "json_object"},
            ),
            timeout=30,
        )
        content = response.choices[0].message.content
        data = json.loads(content)
        title = (data.get("title") or "").strip()[:120]
        summary = (data.get("summary") or "").strip()[:500]
        if not title:
            raise ValueError("empty title from LLM")
    except Exception as e:
        logger.warning(f"timeline_summarizer LLM failed ({e}), using fallback")
        return _fallback_entry(event_title, articles)

    top = sorted_articles[0]
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "title": title,
        "summary": summary,
        "article_count": len(articles),
        "sources": all_sources,
        "top_article_url": getattr(top, "url", "") or "",
    }


def summarize_batch_sync(event_title: str, articles: List, is_initial: bool = False) -> Dict:
    """Sync wrapper for use inside non-async pipeline code paths."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Already in an async context — caller should await summarize_batch directly
            logger.warning("summarize_batch_sync called in running loop; using fallback")
            return _fallback_entry(event_title, articles)
    except RuntimeError:
        pass
    try:
        return asyncio.run(summarize_batch(event_title, articles, is_initial))
    except Exception as e:
        logger.warning(f"summarize_batch_sync failed ({e}), using fallback")
        return _fallback_entry(event_title, articles)
