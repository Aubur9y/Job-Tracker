import time
import re
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app.database import save_to_mongo
from pymongo import MongoClient

def initialize_driver(browser="chrome", headless=True):
    """
    Initialize the Selenium WebDriver.
    """
    options = uc.ChromeOptions()
    if headless:
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
    driver = uc.Chrome(options=options)
    return driver

def build_url(keyword=None, location=None, days_posted=None, radius=None, sort=None):
    base_url = "https://uk.indeed.com/jobs?"
    params = []

    if keyword:
        params.append(f"q={keyword.replace(' ', '+')}")
    if location:
        params.append(f"l={location.replace(' ', '+')}")
    if days_posted:
        params.append(f"fromage={days_posted}")
    if radius:
        params.append(f"radius={radius}")
    if sort == "date":
        params.append("sort=date")

    return base_url + "&".join(params)

def query_jobs(keyword=None, location=None, min_salary=None, max_salary=None):
    client = MongoClient("mongodb+srv://auburyqx0215:Ww876973145@cluster0.0hv3r.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0", db_name="job_scraper", collection_name="jobs")
    db = client["job_tracker"]
    jobs_collection = db["jobs"]

    query = {}
    if keyword:
        query["job_title"] = {"$regex": rf"\b{keyword}\b", "$options": "i"}
    if location:
        query["location"] = {"$regex": location, "$options": "i"}
    if min_salary or max_salary:
        query["salary_numeric"] = {}
        if min_salary is not None:
            query["salary_numeric"]["$gte"] = min_salary
        if max_salary is not None:
            query["salary_numeric"]["$lte"] = max_salary
    
    results = list(jobs_collection.find(query))
    return results

def parse_salary(salary):
    if salary:
        numbers = re.findall(r"[\d,]+", salary)
        if len(numbers) == 2:  # if range provided
            min_salary = int(numbers[0].replace(",", ""))
            max_salary = int(numbers[1].replace(",", ""))
            return (min_salary + max_salary) // 2
        elif len(numbers) == 1:  # if single value provided
            return int(numbers[0].replace(",", ""))
    return None

def scrape_job_listing(driver, url, max_pages=5, db=None, company_name_filter=None, **filters):
    """
    Scrape the job listing from the given URL.
    """
    driver.get(url)
    time.sleep(5)

    try:
        # Handle cookie banner
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "onetrust-policy-text"))
            )
            accept_button = driver.find_element(By.ID, "onetrust-accept-btn-handler")
            accept_button.click()
            print("Cookie banner accepted.")
        except Exception as e:
            pass

    except Exception as e:
        print(f"Error handling cookie banner: {e}")

    job_listings = []
    current_page = 1

    while current_page <= max_pages:
        print(f"Scraping page {current_page}...")
        try:
            job_cards = driver.find_elements(By.CLASS_NAME, "job_seen_beacon")

            for job_card in job_cards:
                try:
                    # Extract job title
                    job_title = job_card.find_element(By.CLASS_NAME, "jobTitle").text

                    # Extract company name
                    try:
                        company_name = job_card.find_element(By.CSS_SELECTOR, '[data-testid="company-name"]').text
                    except:
                        company_name = "Not provided"

                    if company_name_filter is not None:
                        if company_name and company_name_filter.lower() not in (company_name or "").lower():
                            continue

                    # Extract job link
                    try:
                        job_link = job_card.find_element(By.TAG_NAME, "a").get_attribute("href")
                    except:
                        job_link = "Not provided"

                    # Extract location
                    try:
                        location = job_card.find_element(By.CSS_SELECTOR, '[data-testid="text-location"]').text
                    except:
                        location = "Not provided"

                    salary, job_type, schedule = None, None, None
                    try:
                        metadata_items = job_card.find_elements(By.CSS_SELECTOR, '[data-testid="attribute_snippet_testid"]')
                        salary = metadata_items[0].text if len(metadata_items) > 0 else "Not provided"
                        job_type = metadata_items[1].text if len(metadata_items) > 1 else "Not provided"
                        schedule = metadata_items[2].text if len(metadata_items) > 2 else "Not provided"
                    except Exception:
                        salary = job_type = schedule = "Not provided"

                    job_data = {
                        "job_title": job_title,
                        "company_name": company_name,
                        "job_link": job_link,
                        "location": location,
                        "salary": salary,
                        # "salary_numeric": parse_salary(salary),
                        "job_type": job_type,
                        "schedule": schedule,
                    }

                    if db is not None:  # Explicit comparison
                        save_to_mongo(db, "jobs", job_data)  # Save to MongoDB with deduplication
                    job_listings.append(job_data)
                    
                except Exception as e:
                    print(f"Error while scraping a job card: {e}")
                    continue  # Move to the next job card
            
            try:
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="pagination-page-next"]'))
                )
                driver.execute_script("arguments[0].scrollIntoView();", next_button)  # Ensure visibility
                next_button.click()
                time.sleep(5)  # Wait for the next page to load
                current_page += 1
            except Exception as e:
                print(f"Next button not found or error clicking it: {e}")
                break  # Exit loop if no "Next" button is found
        
        except Exception as e:
            print(f"Error while scraping job listings: {e}")
            break
        
    return job_listings