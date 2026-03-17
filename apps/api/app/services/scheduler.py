"""
定时任务调度器 - 使用 APScheduler 管理新闻抓取、热度计算、聚类任务
"""
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.core.database import SessionLocal

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def _get_db():
    """创建独立的数据库会话用于后台任务"""
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise


def job_fetch_and_pipeline():
    """定时任务：完整抓取管线（每 4 小时）"""
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
    """定时任务：更新热度分数（每 1 小时）"""
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
    """定时任务：增量聚类（每 6 小时）"""
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
    """初始化并启动调度器"""
    if scheduler.running:
        return

    # 每 4 小时：完整抓取管线
    scheduler.add_job(
        job_fetch_and_pipeline,
        trigger=IntervalTrigger(hours=4),
        id="fetch_pipeline",
        name="Full news fetch pipeline",
        replace_existing=True,
    )

    # 每 1 小时：更新热度分数
    scheduler.add_job(
        job_update_heat,
        trigger=IntervalTrigger(hours=1),
        id="heat_update",
        name="Update heat scores",
        replace_existing=True,
    )

    # 每 6 小时：增量聚类
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
    """关闭调度器"""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler shut down")
