This project automates job searching and automatically scrapes job listings from Indeed (for now) at user specification. The scraper can be set to scrape the website at a regular interval (only locally right now, TODO: deploy the program onto a server) and send report (currently set to calculate how many new jobs appeared) to a linked telegram bot.

[![Youtube Demo](readme-image1.png)](https://www.youtube.com/watch?v=9vKHdG9doUk)

TODOs:
1. Create a front end (dashboard) to allow users to view job postings
2. Enable the user to customize parameters without using the command line or modifying the code directly
3. Clean up redundant code and optimize project structure
4. Bypass human verification (not sure how to do this yet)
5. Dockerize the code
6. Other job sites (LinkedIn, Glassdoor etc.)
7. Integrate RAG (extract user intention from sentences)
