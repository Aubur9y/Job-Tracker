import logging
from app.scrape import initialize_driver, scrape_job_listing, build_url
from app.database import connect_to_mongo
from app.args import parse_arguments
from app.config import load_config
from app.display import display_jobs

logging.basicConfig(level=logging.INFO)

def main():
    config = load_config()

    args = parse_arguments()

    logging.info("Job Tracker Arguments:")
    logging.info(f"Keyword: {args.keyword}")
    logging.info(f"Location: {args.location}")
    logging.info(f"Days Posted: {args.days_posted}")
    logging.info(f"Radius: {args.radius}")
    logging.info(f"Max Pages: {args.max_pages}")
    logging.info(f"Company Name: {args.company_name}")

    db = connect_to_mongo(uri=config["MONGO_URI"])

    url = build_url(
        keyword=args.keyword,
        location=args.location,
        days_posted=args.days_posted,
        radius=args.radius
    )

    driver = initialize_driver(headless=config["HEADLESS"])

    try:
        logging.info("Scraping job listings...")
        scraped_jobs = scrape_job_listing(
            driver, url, max_pages=args.max_pages, db=db, company_name_filter=args.company_name
        )
        
        display_jobs(scraped_jobs)

    finally:
        driver.quit()

if __name__ == "__main__":
    main()