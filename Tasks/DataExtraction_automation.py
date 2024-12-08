import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime
import json
import uuid
import g4f  # Import the g4f library
import random
import time

# Setup Selenium WebDriver
def setup_selenium():
    # Configure Chrome options
    options = Options()
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--disable-gpu')  # Disable GPU
    options.add_argument('--no-sandbox')  # Bypass OS security model
    options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems

    # Initialize the WebDriver
    driver = webdriver.Chrome(options=options)
    return driver

# Function to generate summary using g4f
def generate_summary_g4f(text):
    try:
        # Generate summary using g4f
        response = g4f.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": f"Summarize the following text: {text}"}]
        )
        summary = response.choices[0].message.content
        return summary
    except Exception as e:
        print(f"Error generating summary with g4f: {str(e)}")
        return None

# Function to extract information from HTML content
def extract_information(html_content):
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        # Extract title
        title = soup.title.text.strip() if soup.title else "No Title"
        # Extract description meta tag
        description_tag = soup.find('meta', attrs={'name': 'description'})
        description = description_tag['content'].strip() if description_tag else ""
        # Extract additional attributes
        additional_info = {}
        return title, description, additional_info
    except Exception as e:
        print(f"Error extracting information: {str(e)}")
        return None, None, None

# Function to standardize data according to Table 2
def standardize_data(title, description, additional_info, url):
    aug_id = str(uuid.uuid4())  # Generate UUID
    country_name = "United States"
    country_code = "USA"
    map_coordinates = {"type": "Point", "coordinates": [-122.4, 37.8]}  # Default coordinates for demonstration
    region_name = "California"
    region_code = "CA"
    status = additional_info.get("status", random.choice(["Open", "Closed"]))
    stages = additional_info.get("stages", random.choice(["Planning", "Execution"]))
    date = datetime.now().strftime("%Y-%m-%d")  # Current date
    procurement_method = additional_info.get("procurementMethod", random.choice(["Design and Build", "Request for Proposal"]))
    budget = additional_info.get("budget", random.uniform(100000.0, 10000000.0))  # Random budget
    currency = additional_info.get("currency", "USD")
    buyer = additional_info.get("buyer", random.choice(["Public", "Private"]))
    sector = additional_info.get("sector", "Construction")
    subsector = additional_info.get("subsector", random.choice(["Building Construction", "Infrastructure Development"]))

    # Construct standardized data as dictionary
    standardized_data = {
        "aug_id": aug_id,
        "country_name": country_name,
        "country_code": country_code,
        "map_coordinates": map_coordinates,
        "url": url,
        "region_name": region_name,
        "region_code": region_code,
        "title": title,
        "description": description,
        "status": status,
        "stages": stages,
        "date": date,
        "procurementMethod": procurement_method,
        "budget": budget,
        "currency": currency,
        "buyer": buyer,
        "sector": sector,
        "subsector": subsector
    }
    return standardized_data

# Function to write standardized data to CSV file
def write_to_csv(data_list, filename):
    try:
        with open(filename, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=data_list[0].keys())
            writer.writeheader()
            for data in data_list:
                writer.writerow(data)
        print(f"Data written to {filename} successfully.")
    except Exception as e:
        print(f"Error writing to CSV: {str(e)}")

# Main function
def main():
    driver = setup_selenium()  # Setup Selenium WebDriver
    urls = [
        "https://dot.ca.gov/",
        "https://www.constructionbidsource.com/",
        "https://www.construction.com/",
        "https://www.bidclerk.com/",
        "https://www.enr.com/topics/212-california-construction-projects",
        "https://www.constructconnect.com/construction-near-me/california-construction-projects",
        "https://www.j360.info/en/tenders/north-america/united-states/california/?act=infrastructure-works-engineering&q=collecte",
        "https://www.tendersinfo.com/esearch/process?search_text=California+bids",
        "https://www.ci.richmond.ca.us/1404/Major-Projects",
        "https://www.cityofwasco.org/311/Current-Projects"
    ]

    # Initialize list to store standardized data
    standardized_data_list = []

    for url in urls:
        print(f"Navigating to {url}...")
        try:
            driver.get(url)
            html_content = driver.page_source
            title, description, additional_info = extract_information(html_content)
            if title and description:
                standardized_data = standardize_data(title, description, additional_info, url)
                standardized_data_list.append(standardized_data)
                print(f"Standardized Data for {url}:", standardized_data)
            else:
                print(f"Failed to extract information from {url}")
        except Exception as e:
            print(f"Error navigating to {url}: {str(e)}")

    driver.quit()  # Close the browser
    # Write standardized data to CSV
    if standardized_data_list:
        write_to_csv(standardized_data_list, 'standardized_data.csv')
    else:
        print("No data to write.")

if __name__ == "__main__":
    while True:
        print("Running data scraping and standardization process...")
        main()
        print("Waiting for next execution...")
        time.sleep(86400)  # Delay for 24 hours (86400 seconds)
