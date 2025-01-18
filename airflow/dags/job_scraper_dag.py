from airflow import DAG
from airflow.operators.python import PythonOperator
from app.scrape import scrape_job_listing, initialize_driver
from app.database import connect_to_mongo, save_to_mongo
from app.config import load_config
from plugins.telegram_notifier import send_telegram_message
from datetime import datetime, timedelta
import logging


# Define default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['your_email@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
with DAG(
    'job_scraper_dag',
    default_args=default_args,
    description='A DAG to scrape job listings and store them in MongoDB',
    schedule_interval='0 */3 * * *',
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=['job_scraper'],
) as dag:

    def scrape_and_store():
        try:
            logging.info("Loading configuration...")
            config = load_config()
            logging.info("Connecting to MongoDB...")
            db = connect_to_mongo(uri=config["MONGO_URI"])
            logging.info("Initializing Selenium driver...")
            driver = initialize_driver(headless=config["HEADLESS"])

            logging.info("Scraping job listings...")
            url = "https://uk.indeed.com/jobs?q=software&l=London"
            scraped_jobs = scrape_job_listing(driver=driver, url=url, max_pages=5, db=None)

            logging.info("Saving scraped jobs to MongoDB...")
            save_to_mongo(db, "jobs", scraped_jobs)

            logging.info("Sending Telegram notification...")
            bot_token = config["TELEGRAM_BOT_TOKEN"]
            chat_id = config["TELEGRAM_CHAT_ID"]
            if scraped_jobs:
                message = f"<b>{len(scraped_jobs)} new jobs found</b>.\nCheck your database for details."
                send_telegram_message(bot_token, chat_id, message)

            logging.info("Closing Selenium driver...")
            driver.quit()
        except Exception as e:
            logging.error(f"Job scraping failed: {e}")
            raise RuntimeError(f"Job scraping failed: {e}")

    scrape_task = PythonOperator(
        task_id='scrape_and_store_jobs',
        python_callable=scrape_and_store,
    )

    scrape_task