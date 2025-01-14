import argparse

def parse_arguments():
    """
    Parse command-line arguments for filtering jobs.
    """
    parser = argparse.ArgumentParser(description="Job Tracker: Scrape and filter job listings.")
    parser.add_argument("--keyword", type=str, help="Filter jobs by keyword (e.g., AI, Software).")
    parser.add_argument("--location", type=str, default="London", help="Filter jobs by location (e.g., London, Remote).")
    parser.add_argument("--days-posted", type=int, choices=[1, 3, 7, 14], help="Filter jobs by how recently they were posted (1, 3, 7, 14 days).")
    parser.add_argument("--radius", type=int, default="10", help="Filter jobs by radius (e.g., 10, 25).")
    parser.add_argument("--sort", type=str, choices=["date"], help="Sort jobs by date posted.")
    parser.add_argument("--max-pages", type=int, default=3, help="Number of pages to scrape (default: 5).")
    return parser.parse_args()