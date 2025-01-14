from celery import Celery
from celery.schedules import crontab

# Initialize the Celery app with the Redis broker
app = Celery("tasks", broker="redis://localhost:6379/0")

# Celery configuration
app.conf.update(
    include=["task"],  # Include the tasks module
    enable_utc=True,  # Ensure UTC time is used
    timezone="UTC",   # Set the timezone
)

# Define periodic tasks with celery-beat
app.conf.beat_schedule = {
    "scrape-every-1-minute": {
        "task": "task.scrape_and_notify",
        "schedule": 60.0,  # Every 1 minute
    },
}
