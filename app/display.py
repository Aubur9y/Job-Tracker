import logging

def display_jobs(jobs):
    """
    Display jobs in a user-friendly format.
    """
    if jobs:
        logging.info(f"Found {len(jobs)} jobs:")
        for i, job in enumerate(jobs, start=1):
            print(f"\nJob {i}:")
            for key, value in job.items():
                print(f"{key.capitalize()}: {value}")
    else:
        logging.warning("No jobs found.")
