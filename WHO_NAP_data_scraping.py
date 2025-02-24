import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin, urlparse
import re

# Define the URL of the WHO page
BASE_URL = "https://www.who.int/teams/surveillance-prevention-control-AMR/national-action-plan-monitoring-evaluation/library-of-national-action-plans"

# Define a folder to save the PDFs
SAVE_FOLDER = "C:/Users/georginahw/Documents/CGPS/NAPs/downloaded_files"
os.makedirs(SAVE_FOLDER, exist_ok=True)

# Get page content
response = requests.get(BASE_URL)
soup = BeautifulSoup(response.text, "html.parser")

# Define regex pattern for WHO publication pages
pattern = r"https://www\.who\.int/publications/m/item/[^\"\']+"

# Extract all 'href' attributes
links = [a["href"] for a in soup.find_all("a", href=True)]

# Filter links using regex (WHO publication pages)
publication_links = [link for link in links if re.search(pattern, link)]

print(f"Found {len(publication_links)} matching WHO publication pages.")
for pub_link in publication_links:
    print(f"Processing: {pub_link}")

    # Visit the WHO publication page
    page_response = requests.get(pub_link)
    if page_response.status_code != 200:
        print(f"Failed to access: {pub_link}")
        continue

    page_soup = BeautifulSoup(page_response.text, "html.parser")

    # Find the actual download link (PDF)
    pdf_link = None

    # Look for buttons or links that could contain the PDF
    for a_tag in page_soup.find_all("a", href=True):
        href = a_tag["href"]
        if ".pdf" in href.lower():  # PDF download link
            pdf_link = urljoin(pub_link, href)
            break

    if not pdf_link:
        print(f"No direct PDF found on: {pub_link}")
        continue

    # Fix the file name issue by cleaning the URL
    parsed_url = urlparse(pdf_link)
    pdf_name = os.path.basename(parsed_url.path)  # Extract filename, ignoring parameters
    pdf_name = pdf_name.split("?")[0]  # Remove query parameters
    pdf_path = os.path.join(SAVE_FOLDER, pdf_name)

    print(f"Downloading: {pdf_name} from {pdf_link}...")
    pdf_response = requests.get(pdf_link, stream=True)
    if pdf_response.status_code == 200:
        with open(pdf_path, "wb") as f:
            for chunk in pdf_response.iter_content(1024):
                f.write(chunk)
        print(f"Saved: {pdf_path}")
    else:
        print(f"Failed to download: {pdf_link}")

print("Download process completed.")
