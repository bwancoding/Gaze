"""
Scheduler - APScheduler-based task scheduling for news fetching, heat calculation, and clustering
"""
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.core.database import SessionLocal

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def _get_db():
    """Create an independent database session for background tasks"""
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise


def job_fetch_and_pipeline():
    """Scheduled task: Full fetch pipeline (every 4 hours)"""
    from app.services.news_aggregator import run_full_pipeline
    db = _get_db()
    try:
        logger.info("Scheduled: running full fetch pipeline")
        result = run_full_pipeline(db)
        logger.info(f"Scheduled: pipeline complete - {result}")
    except Exception as e:
        logger.error(f"Scheduled: pipeline error - {e}")
    finally:
        db.close()


def job_update_heat():
    """Scheduled task: Update heat scores (every 1 hour)"""
    from app.services.news_aggregator import run_heat_update
    db = _get_db()
    try:
        logger.info("Scheduled: updating heat scores")
        result = run_heat_update(db)
        logger.info(f"Scheduled: heat update complete - {result}")
    except Exception as e:
        logger.error(f"Scheduled: heat update error - {e}")
    finally:
        db.close()


def job_clustering():
    """Scheduled task: Incremental clustering + trim (every 6 hours)"""
    from app.services.news_aggregator import run_clustering
    db = _get_db()
    try:
        logger.info("Scheduled: running clustering")
        result = run_clustering(db)
        logger.info(f"Scheduled: clustering complete - {result}")
    except Exception as e:
        logger.error(f"Scheduled: clustering error - {e}")
    finally:
        db.close()


def init_scheduler():
    """Initialize and start the scheduler"""
    if scheduler.running:
        return

    # Every 4 hours: full fetch pipeline (fetch → dedup → cluster → heat → trim)
    scheduler.add_job(
        job_fetch_and_pipeline,
        trigger=IntervalTrigger(hours=4),
        id="fetch_pipeline",
        name="Full news fetch pipeline",
        replace_existing=True,
    )

    # Every 1 hour: update heat scores + trim
    scheduler.add_job(
        job_update_heat,
        trigger=IntervalTrigger(hours=1),
        id="heat_update",
        name="Update heat scores",
        replace_existing=True,
    )

    # Every 6 hours: incremental clustering + trim
    scheduler.add_job(
        job_clustering,
        trigger=IntervalTrigger(hours=6),
        id="clustering",
        name="Incremental clustering",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Scheduler started with 3 jobs: fetch(4h), heat(1h), cluster(6h)")


def shutdown_scheduler():
    """Shut down the scheduler"""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler shut down")
