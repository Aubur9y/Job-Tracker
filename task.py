from celery_app import app  # Import the app instance
from celery.utils.log import get_task_logger
from app.scrape import scrape_job_listing
from app.database import connect_to_mongo
from app.config import load_config
from airflow.plugins.telegram_notifier import send_telegram_message
from app.scrape import initialize_driver
from app.database import save_to_mongo

logger = get_task_logger(__name__)

@app.task
def scrape_and_notify():
    try:
        config = load_config()
        db = connect_to_mongo(uri=config["MONGO_URI"])
        driver = initialize_driver(headless=config["HEADLESS"])

        url = "https://uk.indeed.com/jobs?q=software&l=London"
        scraped_jobs = scrape_job_listing(driver=driver, url=url, max_pages=5, db=None)

        # Save jobs to the database and get the count of new records
        new_jobs_count = save_to_mongo(db, "jobs", scraped_jobs)

        logger.info(f"{new_jobs_count} new jobs added to the database.")

        # Notify via Telegram
        bot_token = config["TELEGRAM_BOT_TOKEN"]
        chat_id = config["TELEGRAM_CHAT_ID"]

        if new_jobs_count > 0:
            message = f"<b>{new_jobs_count} new jobs found</b>.\nCheck your database for details."
            send_telegram_message(bot_token, chat_id, message)
        else:
            logger.info("No new jobs found.")

        driver.quit()
    except Exception as e:
        logger.error(f"Error in scrape_and_notify task: {e}")
        raise


