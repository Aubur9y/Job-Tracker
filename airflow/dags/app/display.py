import logging

def display_jobs(jobs):
    """
    Display jobs in a user-friendly format, showing the current job number and the total number of jobs.
    """
    total_jobs = len(jobs)
    if jobs:
        logging.info(f"Found {total_jobs} jobs:")
        for i, job in enumerate(jobs, start=1):
            print(f"\nJob {i} of {total_jobs}:")  # Add "of XX" format
            for key, value in job.items():
                print(f"{key.capitalize()}: {value}")
    else:
        logging.warning("No jobs found.")
