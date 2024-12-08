import requests
from bs4 import BeautifulSoup
import g4f
from g4f.client import Client

client = Client()

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

# Function to fetch content from a URL and remove HTML tags
def fetch_content(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            # Remove HTML tags and extract text
            text = soup.get_text(separator=' ')
            return text
        else:
            print(f"Failed to fetch URL: {url}")
            return None
    except Exception as e:
        print(f"Error processing URL {url}: {str(e)}")
        return None

# Function to generate summary using GPT
def generate_summary(text):
    try:
        # Truncate the text to avoid token overflow
        truncated_text = text[:1000]  # Adjust as needed
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": f"Summarize the following text: {truncated_text}"}]
        )
        # Assuming response is a dictionary containing the completion text
        summary = response.choices[0].message.content
        return summary
    except Exception as e:
        print(f"Error generating summary: {str(e)}")
        return None

# Fetch content, generate summaries, and select top links based on relevance
summaries = []
for url in urls:
    print(f"Processing {url}...")
    content = fetch_content(url)
    if content:
        summary = generate_summary(content)
        if summary:
            summaries.append((url, summary))

# Assess relevance of summaries and assign scores
scores = []
for url, summary in summaries:
    score = 0
    # Check for keywords related to construction, infrastructure, projects, tenders, and California
    if "construction" in summary.lower():
        score += 1
    if "infrastructure" in summary.lower():
        score += 1
    if "projects" in summary.lower():
        score += 1
    if "tenders" in summary.lower():
        score += 1
    if "california" in summary.lower():
        score += 1
    scores.append((url, score))

# Sort links based on scores in descending order
scores.sort(key=lambda x: x[1], reverse=True)

# Select top 10 links with highest scores
top_links = [link[0] for link in scores[:min(10, len(scores))]]

# Print top links
print("Top 5 to 10 Relevant Links:")
for link in top_links:
    print(link)
