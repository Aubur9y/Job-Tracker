import logging
from scrape import initialize_driver, scrape_job_listing

logging.basicConfig(level=logging.INFO)

def main():
    url = "https://uk.indeed.com/jobs?q=&l=london"
    print(f"Scraping jobs from {url}")

    driver = initialize_driver(headless=False)

    try:
        job = scrape_job_listing(driver, url, max_pages=1)

        if job:
            logging.info(f"Scraped {len(job)} job listings")
            for i, job in enumerate(job, start=1):
                print(f"\nJob {i}")
                for key, value in job.items():
                    print(f"{key.capitalize()}: {value}")
        else:
            logging.warning("No jobs listings found.")
    except Exception as e:
        logging.error(f"Error scraping job listings: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()