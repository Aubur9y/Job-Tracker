# Use the official Apache Airflow image as the base image
FROM apache/airflow:2.10.4-python3.11

# Install system dependencies (as root)
USER root
RUN apt-get update && \
    apt-get install -y wget unzip && \
    rm -rf /var/lib/apt/lists/*

# Install Google Chrome browser
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/* && \
    echo "Installed Google Chrome version:" && \
    google-chrome --version

# Ensure the airflow group exists
RUN groupadd -g 1000 airflow || true

# Install ChromeDriver in a user-writable directory
RUN CHROMEDRIVER_VERSION=132.0.6834.83 && \
    wget -q -O /tmp/chromedriver.zip https://storage.googleapis.com/chrome-for-testing-public/132.0.6834.83/linux64/chromedriver-linux64.zip && \
    unzip -o /tmp/chromedriver.zip -d /tmp/ && \
    mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -rf /tmp/chromedriver.zip /tmp/chromedriver-linux64 && \
    echo "Installed ChromeDriver version:" && \
    /usr/local/bin/chromedriver --version

# Add the directory to PATH
ENV PATH="/home/airflow/.local/bin:${PATH}"

# Switch to the airflow user
USER airflow

# Install Python dependencies (as airflow user)
RUN pip install --no-cache-dir undetected-chromedriver
