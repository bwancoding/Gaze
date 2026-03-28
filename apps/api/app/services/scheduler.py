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
    from app.services.event_clusterer import cluster_new_articles
    db = _get_db()
    try:
        logger.info("Scheduled: running clustering")
        result = cluster_new_articles(db)
        logger.info(f"Scheduled: clustering complete - {result}")
    except Exception as e:
        logger.error(f"Scheduled: clustering error - {e}")
    finally:
        db.close()


def job_auto_archive():
    """Scheduled task: Auto-archive stale/expired active events (every 1 hour)"""
    from app.services.event_lifecycle import auto_archive_events
    db = _get_db()
    try:
        logger.info("Scheduled: running auto-archive")
        result = auto_archive_events(db)
        logger.info(f"Scheduled: auto-archive complete - {result}")
    except Exception as e:
        logger.error(f"Scheduled: auto-archive error - {e}")
    finally:
        db.close()


def job_cleanup_logs():
    """Scheduled task: Prune old request_logs, page_views, and error_logs"""
    db = _get_db()
    try:
        from datetime import datetime, timedelta
        from sqlalchemy import text

        cutoff_90 = datetime.utcnow() - timedelta(days=90)
        cutoff_180 = datetime.utcnow() - timedelta(days=180)

        r1 = db.execute(text("DELETE FROM request_logs WHERE timestamp < :cutoff"), {"cutoff": cutoff_90})
        r2 = db.execute(text("DELETE FROM page_views WHERE timestamp < :cutoff"), {"cutoff": cutoff_90})
        r3 = db.execute(text("DELETE FROM error_logs WHERE timestamp < :cutoff"), {"cutoff": cutoff_180})
        db.commit()

        total = (r1.rowcount or 0) + (r2.rowcount or 0) + (r3.rowcount or 0)
        if total > 0:
            logger.info(f"Scheduled: cleaned up {total} old log entries")
    except Exception as e:
        logger.error(f"Scheduled: log cleanup error - {e}")
        db.rollback()
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

    # Every 1 hour: auto-archive stale/expired active events
    scheduler.add_job(
        job_auto_archive,
        trigger=IntervalTrigger(hours=1),
        id="auto_archive",
        name="Auto-archive stale events",
        replace_existing=True,
    )

    # Every 24 hours: clean up old logs (request_logs >90d, error_logs >180d)
    scheduler.add_job(
        job_cleanup_logs,
        trigger=IntervalTrigger(hours=24),
        id="log_cleanup",
        name="Clean up old logs",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Scheduler started with 5 jobs: fetch(4h), heat(1h), cluster(6h), auto-archive(1h), log-cleanup(24h)")


def shutdown_scheduler():
    """Shut down the scheduler"""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler shut down")
