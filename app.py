from flask import Flask, jsonify, request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import uuid
import json
import random
import g4f
import time
from flask_cors import CORS

# Initialize Flask App
app = Flask(__name__)
CORS(app)
# Setup Selenium WebDriver
def setup_selenium():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    return driver

# Function to generate summary using g4f
def generate_summary_g4f(text):
    try:
        response = g4f.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": f"Summarize the following text: {text}"}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating summary: {str(e)}"

# Function to extract information from HTML content
def extract_information(html_content):
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        title = soup.title.text.strip() if soup.title else "No Title"
        description_tag = soup.find('meta', attrs={'name': 'description'})
        description = description_tag['content'].strip() if description_tag else "No Description"
        additional_info = {}
        return title, description, additional_info
    except Exception as e:
        return None, None, None

# Function to standardize data
def standardize_data(title, description, additional_info, url):
    aug_id = str(uuid.uuid4())
    standardized_data = {
        "aug_id": aug_id,
        "country_name": "United States",
        "country_code": "USA",
        "map_coordinates": {"type": "Point", "coordinates": [-122.4, 37.8]},
        "url": url,
        "region_name": "California",
        "region_code": "CA",
        "title": title,
        "description": description,
        "status": additional_info.get("status", random.choice(["Open", "Closed"])),
        "stages": additional_info.get("stages", random.choice(["Planning", "Execution"])),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "procurementMethod": additional_info.get("procurementMethod", random.choice(["Design and Build", "Request for Proposal"])),
        "budget": additional_info.get("budget", random.uniform(100000.0, 10000000.0)),
        "currency": "USD",
        "buyer": additional_info.get("buyer", random.choice(["Public", "Private"])),
        "sector": "Construction",
        "subsector": random.choice(["Building Construction", "Infrastructure Development"])
    }
    return standardized_data

# Function to write data to CSV
def write_to_csv(data_list, filename):
    try:
        with open(filename, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=data_list[0].keys())
            writer.writeheader()
            writer.writerows(data_list)
        return f"Data successfully exported to {filename}"
    except Exception as e:
        return f"Error writing to CSV: {str(e)}"

# Unified route for all functionalities
@app.route('/process', methods=['GET'])
def process_data():
    urls =["https://dot.ca.gov/",
        "https://www.constructionbidsource.com/",
        "https://www.construction.com/",
        "https://www.bidclerk.com/",
        "https://www.enr.com/topics/212-california-construction-projects",
        "https://www.constructconnect.com/construction-near-me/california-construction-projects",
        "https://www.j360.info/en/tenders/north-america/united-states/california/?act=infrastructure-works-engineering&q=collecte",
        "https://www.tendersinfo.com/esearch/process?search_text=California+bids",
        "https://www.ci.richmond.ca.us/1404/Major-Projects",
        "https://www.cityofwasco.org/311/Current-Projects"]
    if not urls:
        return jsonify({"error": "No URLs provided"}), 400

    driver = setup_selenium()
    standardized_data_list = []
    summaries = []

    for url in urls:
        try:
            driver.get(url)
            html_content = driver.page_source
            title, description, additional_info = extract_information(html_content)
            if title and description:
                standardized_data = standardize_data(title, description, additional_info, url)
                standardized_data_list.append(standardized_data)
                
                # Generate summary for the description
                #summary = generate_summary_g4f(description)
                #summaries.append({"url": url, "summary": summary})
        except Exception as e:
            return jsonify({"error": f"Failed to process {url}: {str(e)}"}), 500

    driver.quit()

    # Export data to CSV
    if standardized_data_list:
        export_message = write_to_csv(standardized_data_list, 'standardized_data.csv')
    else:
        export_message = "No data to export."

    return jsonify({
        "standardized_data": standardized_data_list,
        "summaries": summaries,
        "export_message": export_message
    }), 200

if __name__ == '__main__':
    app.run(debug=True)
