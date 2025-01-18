# Use the official Apache Airflow image as the base
FROM apache/airflow:2.6.0

# Switch to root user to install system packages
USER root

# Install Chromium and wget
RUN apt-get update && \
    apt-get install -y chromium wget unzip && \
    rm -rf /var/lib/apt/lists/*

# Install ChromiumDriver (matching the installed Chromium version)
RUN CHROMIUM_VERSION=$(chromium --version | grep -oP '\d+\.\d+\.\d+\.\d+' | cut -d'.' -f1) && \
    echo "Chromium major version: ${CHROMIUM_VERSION}" && \
    CHROMEDRIVER_VERSION=$(wget -q -O - https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROMIUM_VERSION}) && \
    echo "ChromeDriver version: ${CHROMEDRIVER_VERSION}" && \
    wget -q -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    rm /tmp/chromedriver.zip

# Install additional Python dependencies
RUN pip install undetected-chromedriver pymongo python-dotenv fake_useragent requests redis dnspython

# Switch back to the airflow user
USER airflow