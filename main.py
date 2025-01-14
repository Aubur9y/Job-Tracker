import logging
from scrape import initialize_driver, scrape_job_listing
from database import connect_to_mongo, query_jobs

logging.basicConfig(level=logging.INFO)

def main():
    url = "https://uk.indeed.com/jobs?q=&l=london"
    print(f"Scraping jobs from {url}")
    keyword = "AI"

    uri = "mongodb+srv://auburyqx0215:Ww876973145@cluster0.0hv3r.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    db = connect_to_mongo(uri=uri)

    driver = initialize_driver(headless=False)

    try:
        logging.info("Scraping job listings...")
        scrape_job_listing(driver, url, max_pages=1, keyword=keyword, db=db)

        saved_jobs = query_jobs(db, "jobs", {"job_title": {"$regex": keyword, "$options": "i"}})
        for job in saved_jobs:
            print(job)

    #     if job:
    #         logging.info(f"Scraped {len(job)} job listings")
    #         for i, job in enumerate(job, start=1):
    #             print(f"\nJob {i}")
    #             for key, value in job.items():
    #                 print(f"{key.capitalize()}: {value}")
    #     else:
    #         logging.warning("No jobs listings found.")
    # except Exception as e:
    #     logging.error(f"Error scraping job listings: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()