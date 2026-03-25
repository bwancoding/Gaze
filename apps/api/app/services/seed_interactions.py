"""
Seed Interactions Service
Generates fake users, threads, comments, and votes for active events
to make the platform look active during early stage.
"""

import json
import logging
import os
import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.models import Event, User
from app.models.personas import UserPersona
from app.models.threads import Thread
from app.models.comments import Comment
from app.models.user_likes import UserLike
# Import all models to ensure SQLAlchemy relationships resolve properly
from app.models.stakeholders import Stakeholder, EventStakeholder  # noqa: F401
from app.models.trending import TrendingEvent, TrendingArticle, TrendingSource  # noqa: F401
from app.services.seed_prompts import SEED_THREAD_PROMPT, SEED_COMMENT_PROMPT

logger = logging.getLogger(__name__)

SEED_USER_EMAIL_DOMAIN = "seed.wrhitw.local"

# English internet-style display names
SEED_DISPLAY_NAMES = [
    # Platform-generated style
    "MidEast Policy Watcher",
    "Climate Data Analyst",
    "Tech Industry Insider",
    "Journalism Student",
    "Ex-Diplomat Observer",
    "Defense Policy Researcher",
    "Econ PhD Candidate",
    "Human Rights Advocate",
    "Energy Sector Analyst",
    "Foreign Affairs Buff",
    # Internet nickname style
    "NightOwlReader",
    "GeopoliticsNerd",
    "NewsJunkie42",
    "GlobalWatcher",
    "SkepticalAnalyst",
    "CuriousCitizen",
    "DataDrivenThinker",
    "TheDevilsAdvocate",
    "SilentMajority",
    "ObjectiveLens",
]

AVATAR_COLORS = ["blue", "green", "red", "purple", "orange", "teal", "pink", "indigo"]

# Indices of seed users that should appear as verified stakeholders (~30%)
VERIFIED_INDICES = {0, 2, 4, 7, 8, 14}


def _get_ai_client():
    """Create OpenAI-compatible client for DashScope."""
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        return None
    from openai import AsyncOpenAI
    import httpx
    return AsyncOpenAI(
        base_url=os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
        api_key=api_key,
        timeout=httpx.Timeout(30.0, connect=8.0),
        max_retries=1,
    )


def ensure_seed_users(db: Session, count: int = 20) -> List[User]:
    """Create or fetch seed users. Idempotent."""
    existing = db.query(User).filter(
        User.email.like(f"%@{SEED_USER_EMAIL_DOMAIN}")
    ).all()

    if len(existing) >= count:
        return existing[:count]

    existing_emails = {u.email for u in existing}

    for i, name in enumerate(SEED_DISPLAY_NAMES[:count]):
        email = f"{name.lower().replace(' ', '.').replace('_', '')}@{SEED_USER_EMAIL_DOMAIN}"
        if email in existing_emails:
            continue

        user = User(
            email=email,
            display_name=name,
            password_hash="SEED_USER_NO_LOGIN",
            is_active=True,
            is_verified=False,
        )
        db.add(user)
        existing.append(user)

    db.flush()
    return existing[:count]


def ensure_seed_personas(db: Session, users: List[User]) -> List[UserPersona]:
    """Create 1 persona per seed user. Idempotent."""
    all_personas = []

    for i, user in enumerate(users):
        existing = db.query(UserPersona).filter(
            UserPersona.user_id == user.id,
            UserPersona.is_deleted == False,
        ).first()

        if existing:
            all_personas.append(existing)
            continue

        persona = UserPersona(
            user_id=user.id,
            persona_name=user.display_name,
            avatar_color=random.choice(AVATAR_COLORS),
            is_verified=i in VERIFIED_INDICES,  # ~30% verified
        )
        db.add(persona)
        all_personas.append(persona)

    db.flush()
    return all_personas


def _event_already_seeded(db: Session, event_id: str) -> bool:
    """Check if this event already has seed interactions."""
    seed_user_ids = [
        r[0] for r in db.query(User.id).filter(
            User.email.like(f"%@{SEED_USER_EMAIL_DOMAIN}")
        ).all()
    ]
    if not seed_user_ids:
        return False

    count = db.query(Thread).filter(
        Thread.event_id == event_id,
        Thread.user_id.in_(seed_user_ids),
        Thread.is_deleted == False,
    ).count()

    return count > 0


async def _generate_threads_ai(event: Event, thread_count: int = 4) -> List[Dict]:
    """Use AI to generate thread content."""
    client = _get_ai_client()
    if not client:
        logger.warning("No AI client available, generating placeholder threads")
        return _generate_threads_fallback(event, thread_count)

    prompt = SEED_THREAD_PROMPT.format(
        thread_count=thread_count,
        event_title=event.title,
        event_summary=(event.summary or "")[:500],
        event_category=event.category or "General",
    )

    try:
        response = await client.chat.completions.create(
            model="qwen3.5-plus",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.85,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        data = json.loads(content)
        return data.get("threads", [])
    except Exception as e:
        logger.error(f"AI thread generation failed for event {event.id}: {e}")
        return _generate_threads_fallback(event, thread_count)


async def _generate_comments_ai(
    event: Event, thread_title: str, thread_content: str, comment_count: int = 8
) -> List[Dict]:
    """Use AI to generate comment content."""
    client = _get_ai_client()
    if not client:
        return _generate_comments_fallback(comment_count)

    prompt = SEED_COMMENT_PROMPT.format(
        comment_count=comment_count,
        event_title=event.title,
        event_summary=(event.summary or "")[:500],
        thread_title=thread_title,
        thread_content=thread_content,
    )

    try:
        response = await client.chat.completions.create(
            model="qwen3.5-plus",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.85,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        data = json.loads(content)
        return data.get("comments", [])
    except Exception as e:
        logger.error(f"AI comment generation failed: {e}")
        return _generate_comments_fallback(comment_count)


def _generate_threads_fallback(event: Event, count: int) -> List[Dict]:
    """Fallback thread generation without AI — rich diverse templates."""
    title_short = event.title[:40]
    cat = event.category or "General"

    all_angles = [
        ("What are the long-term implications?",
         f"Thinking about '{title_short}' — this could have far-reaching consequences that we haven't fully considered yet. I'm curious what long-term shifts people see coming from this."),
        ("Who benefits from this situation?",
         "It's worth analyzing who the real winners and losers are here. Follow the money, as they say. What power dynamics are at play?"),
        ("Media framing across different outlets",
         "I've been comparing how different outlets are covering this — the framing varies wildly. Some emphasize fear, others emphasize opportunity. Anyone else noticing this?"),
        ("Historical parallels worth exploring",
         f"This isn't happening in a vacuum. There are historical parallels that give context to what's unfolding in '{title_short}'. Let's discuss them."),
        ("What can ordinary people do?",
         "Beyond scrolling through the news, I wonder what practical steps regular people can take. Sometimes local action is more impactful than we think."),
        ("The stakeholders nobody is talking about",
         "Most coverage focuses on the obvious players, but there are communities and groups being affected that barely get mentioned. Who are they?"),
        ("How is this being discussed outside the West?",
         "It's easy to get stuck in English-language media bubbles. How are people in other regions reacting to this? Any non-Western perspectives to share?"),
        ("Economic ripple effects",
         f"The economic consequences of '{title_short}' go beyond the obvious. Supply chains, labor markets, investment patterns — what should we be watching?"),
        ("Technology's role in this story",
         "Technology is playing an interesting role here — both amplifying certain voices and potentially offering solutions. What's the tech angle people are seeing?"),
        ("Separating fact from speculation",
         "There's a lot of noise around this topic. Let's try to pin down what we actually know vs. what's speculation or early reporting that hasn't been verified."),
    ]

    random.shuffle(all_angles)
    threads = []
    for i in range(min(count, len(all_angles))):
        title, content = all_angles[i]
        tags = random.sample(["discussion", "analysis", "perspective", "question", cat.lower()], k=min(3, 2 + random.randint(0, 1)))
        threads.append({
            "title": title,
            "content": content,
            "tags": tags,
        })
    return threads


def _generate_comments_fallback(count: int) -> List[Dict]:
    """Fallback comment generation without AI — varied realistic comments."""
    all_templates = [
        {"content": "This is a really important point. I hadn't thought about it from this angle before.", "reply_to_index": None},
        {"content": "I respectfully disagree. The situation is more nuanced than most coverage suggests.", "reply_to_index": None},
        {"content": "Does anyone have links to primary sources on this? I'd like to read beyond the headlines.", "reply_to_index": None},
        {"content": "Exactly my thoughts! Really well put.", "reply_to_index": 0},
        {"content": "The mainstream narrative is missing a lot of important context. Here's what I've been reading...", "reply_to_index": None},
        {"content": "As someone with a background in this area, I can share that this is more complex than it appears on the surface.", "reply_to_index": None},
        {"content": "Good thread. But what about the economic implications? That's what concerns me most.", "reply_to_index": 1},
        {"content": "I think we need to wait for more verified information before drawing conclusions.", "reply_to_index": None},
        {"content": "Thank you for starting this discussion. It's hard to find places online where people actually listen to each other.", "reply_to_index": None},
        {"content": "I live in the region being discussed, and I can tell you the reality on the ground is quite different from what's being reported.", "reply_to_index": None},
        {"content": "Worth noting that this is part of a much larger trend that's been building for years.", "reply_to_index": 2},
        {"content": "Has anyone seen how local communities are organizing in response to this? That part of the story deserves more attention.", "reply_to_index": None},
        {"content": "The geopolitical implications here are enormous. This could reshape alliances in the region.", "reply_to_index": None},
        {"content": "I appreciate hearing multiple perspectives here. Social media usually just gives us echo chambers.", "reply_to_index": 0},
        {"content": "One thing being overlooked: the environmental impact. Every policy decision has downstream ecological effects.", "reply_to_index": None},
        {"content": "Solid analysis. I'd add that the timing of this is not a coincidence either.", "reply_to_index": 1},
        {"content": "Reading through this thread is genuinely more informative than most news articles I've seen on this topic.", "reply_to_index": None},
        {"content": "Can we talk about the humanitarian angle? Real people are being affected and their voices matter most.", "reply_to_index": None},
        {"content": "I was skeptical at first but you've made a compelling case. Changed my mind on this.", "reply_to_index": 3},
        {"content": "The data actually supports a different conclusion if you look at the full picture. Let me explain...", "reply_to_index": None},
    ]
    random.shuffle(all_templates)
    selected = all_templates[:count]
    # Re-index reply_to_index to stay valid
    for c in selected:
        if c["reply_to_index"] is not None and c["reply_to_index"] >= len(selected):
            c["reply_to_index"] = None
    return selected


def _random_timestamp(base_time: datetime, hours_range: int = 72) -> datetime:
    """Generate a random timestamp within hours_range from base_time."""
    offset = random.randint(0, hours_range * 3600)
    return base_time + timedelta(seconds=offset)


async def seed_event_interactions(
    db: Session,
    event_id: str,
    thread_count: int = 4,
    comments_per_thread: int = 8,
    force: bool = False,
) -> Dict:
    """Generate seed interactions for a single event."""

    # Check idempotency
    if not force and _event_already_seeded(db, event_id):
        return {"status": "skipped", "reason": "already_seeded", "event_id": event_id}

    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        return {"status": "error", "reason": "event_not_found", "event_id": event_id}

    # Ensure seed users and personas
    users = ensure_seed_users(db)
    personas = ensure_seed_personas(db, users)
    user_persona_pairs = list(zip(users, personas))

    base_time = event.published_at or event.created_at or datetime.utcnow() - timedelta(days=2)

    # Generate threads via AI
    thread_count = random.randint(3, 5)
    thread_data = await _generate_threads_ai(event, thread_count)

    created_threads = []
    total_comments = 0
    total_votes = 0

    for t_data in thread_data:
        # Pick random user/persona for thread author
        author_user, author_persona = random.choice(user_persona_pairs)
        thread_time = _random_timestamp(base_time, hours_range=48)

        thread = Thread(
            event_id=event.id,
            user_id=author_user.id,
            user_persona_id=author_persona.id,
            title=t_data.get("title", "Discussion")[:500],
            content=t_data.get("content", "What do you think?"),
            tags=t_data.get("tags", []),
            view_count=random.randint(50, 500),
            created_at=thread_time,
            updated_at=thread_time,
        )
        db.add(thread)
        db.flush()
        created_threads.append(thread)

        # Generate comments for this thread
        comment_count = random.randint(5, 15)
        comment_data = await _generate_comments_ai(
            event, thread.title, thread.content, comment_count
        )

        created_comments = []
        for c_idx, c_data in enumerate(comment_data):
            # Pick different user than thread author
            available = [p for p in user_persona_pairs if p[0].id != author_user.id]
            if not available:
                available = user_persona_pairs
            c_user, c_persona = random.choice(available)

            comment_time = _random_timestamp(thread_time, hours_range=24)

            # Handle reply_to_index
            parent_id = None
            reply_idx = c_data.get("reply_to_index")
            if reply_idx is not None and isinstance(reply_idx, int) and 0 <= reply_idx < len(created_comments):
                parent_id = created_comments[reply_idx].id

            comment = Comment(
                user_id=c_user.id,
                user_persona_id=c_persona.id,
                event_id=event.id,
                thread_id=thread.id,
                parent_id=parent_id,
                content=c_data.get("content", "Interesting perspective."),
                created_at=comment_time,
                updated_at=comment_time,
            )
            db.add(comment)
            db.flush()
            created_comments.append(comment)
            total_comments += 1

            # Update parent reply_count
            if parent_id:
                parent_comment = db.query(Comment).filter(Comment.id == parent_id).first()
                if parent_comment:
                    parent_comment.reply_count = (parent_comment.reply_count or 0) + 1

        # Update thread reply_count
        thread.reply_count = len(created_comments)

        # Generate votes for thread — track who voted to avoid duplicates
        thread_like = 0
        thread_dislike = 0
        voters = random.sample(user_persona_pairs, min(random.randint(5, 20), len(user_persona_pairs)))
        voted_user_ids = set()
        for v_user, _ in voters:
            if v_user.id in voted_user_ids:
                continue
            voted_user_ids.add(v_user.id)
            vote_type = 'like' if random.random() < 0.7 else 'dislike'
            vote = UserLike(
                user_id=v_user.id,
                thread_id=thread.id,
                vote_type=vote_type,
                created_at=_random_timestamp(thread_time, 48),
            )
            db.add(vote)
            if vote_type == 'like':
                thread_like += 1
            else:
                thread_dislike += 1
            total_votes += 1
        thread.like_count = thread_like
        thread.dislike_count = thread_dislike
        db.flush()

        # Generate votes for comments
        for comment in created_comments:
            c_like = 0
            c_dislike = 0
            voter_count = random.randint(2, 10)
            c_voters = random.sample(user_persona_pairs, min(voter_count, len(user_persona_pairs)))
            c_voted_ids = set()
            for v_user, _ in c_voters:
                if v_user.id in c_voted_ids:
                    continue
                c_voted_ids.add(v_user.id)
                vote_type = 'like' if random.random() < 0.7 else 'dislike'
                vote = UserLike(
                    user_id=v_user.id,
                    comment_id=comment.id,
                    vote_type=vote_type,
                    created_at=_random_timestamp(comment.created_at, 24),
                )
                db.add(vote)
                if vote_type == 'like':
                    c_like += 1
                else:
                    c_dislike += 1
                total_votes += 1
            comment.like_count = c_like
            comment.dislike_count = c_dislike
        db.flush()

    # Update event last_activity_at
    from app.services.event_lifecycle import touch_event_activity
    touch_event_activity(db, str(event.id))

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to commit seed data for event {event.id}: {e}")
        return {"status": "error", "event_id": str(event.id), "error": str(e)}

    return {
        "status": "success",
        "event_id": str(event.id),
        "event_title": event.title[:50],
        "threads_created": len(created_threads),
        "comments_created": total_comments,
        "votes_created": total_votes,
    }


async def seed_all_active_events(
    db: Session,
    force: bool = False,
) -> Dict:
    """Seed interactions for ALL active events."""
    active_events = db.query(Event).filter(Event.status == 'active').all()

    results = []
    success_count = 0
    skip_count = 0
    error_count = 0

    for event in active_events:
        try:
            result = await seed_event_interactions(db, str(event.id), force=force)
            results.append(result)
            if result["status"] == "success":
                success_count += 1
            elif result["status"] == "skipped":
                skip_count += 1
            else:
                error_count += 1
        except Exception as e:
            logger.error(f"Failed to seed event {event.id}: {e}")
            error_count += 1
            results.append({
                "status": "error",
                "event_id": str(event.id),
                "error": str(e),
            })

    return {
        "total_events": len(active_events),
        "seeded": success_count,
        "skipped": skip_count,
        "errors": error_count,
        "details": results,
    }


async def cleanup_seed_data(db: Session) -> Dict:
    """Remove all seed users and their data (cascaded via FK)."""
    seed_users = db.query(User).filter(
        User.email.like(f"%@{SEED_USER_EMAIL_DOMAIN}")
    ).all()

    seed_user_ids = [u.id for u in seed_users]
    if not seed_user_ids:
        return {"status": "nothing_to_clean", "deleted_users": 0}

    # Delete votes by seed users
    votes_deleted = db.query(UserLike).filter(
        UserLike.user_id.in_(seed_user_ids)
    ).delete(synchronize_session='fetch')

    # Delete comments by seed users
    comments_deleted = db.query(Comment).filter(
        Comment.user_id.in_(seed_user_ids)
    ).delete(synchronize_session='fetch')

    # Delete threads by seed users
    threads_deleted = db.query(Thread).filter(
        Thread.user_id.in_(seed_user_ids)
    ).delete(synchronize_session='fetch')

    # Delete personas
    personas_deleted = db.query(UserPersona).filter(
        UserPersona.user_id.in_(seed_user_ids)
    ).delete(synchronize_session='fetch')

    # Delete seed users
    for user in seed_users:
        db.delete(user)

    db.commit()

    return {
        "status": "cleaned",
        "deleted_users": len(seed_users),
        "deleted_personas": personas_deleted,
        "deleted_threads": threads_deleted,
        "deleted_comments": comments_deleted,
        "deleted_votes": votes_deleted,
    }
