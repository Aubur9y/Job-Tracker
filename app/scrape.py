import time
import re
import undetected_chromedriver as uc
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app.database import save_to_mongo
from pymongo import MongoClient
from fake_useragent import UserAgent

def initialize_driver(browser="chrome", headless=True, proxy=None):
    """
    Initialize the Selenium WebDriver with anti-bot features.
    """
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    ]

    options = uc.ChromeOptions()
    ua_string = random.choice(user_agents)
    options.add_argument(f"user-agent={ua_string}")
    print(f"Using User-Agent: {ua_string}")

    # Headless mode settings
    if headless:
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")

    # Proxy support
    if proxy:
        options.add_argument(f"--proxy-server={proxy}")

    # Add extra headers to mimic real user behavior
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-dev-shm-usage")

    # Enable browser debugging (optional)
    options.add_argument("--remote-debugging-port=9222")

    # Launch the driver
    driver = uc.Chrome(options=options)

    # Inject additional headers
    headers = {
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
    }
    driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": headers})

    return driver

def build_url(keyword=None, location=None, days_posted=None, radius=None, sort_by=None, min_salary=None):
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
    if sort_by == "date":
        params.append("sort=date")
    if min_salary:
        salary_param = f"£{min_salary:,}".replace(",", "%2C")
        params.append(f"salaryType={salary_param}")

    return base_url + "&".join(params)

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
                        salary = next((item.text for item in metadata_items if "£" in item.text or "hour" in item.text or "day" in item.text or "month" in item.text or "year" in item.text), "Not provided")
                        job_type = next((item.text for item in metadata_items if "Permanent" in item.text or "Contract" in item.text or "Temporary" in item.text), "Not provided")
                        schedule = next((item.text for item in metadata_items if "Part-time" in item.text or "Full-time" in item.text or "Shift" in item.text), "Not provided")
                    except Exception as e:
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