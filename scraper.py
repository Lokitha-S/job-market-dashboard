import os
import requests
import pandas as pd
import datetime
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from dotenv import load_dotenv

# 1. Load environment variables from .env file
load_dotenv()

def scrape_jobs():
    """Fetches job listings from the practice site to avoid 403 blocks."""
    url = "https://realpython.github.io/fake-jobs/"
    print(f"🔍 Scraping data from: {url}")
    
    # Headers to mimic a real browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status() # Raises error for 404 or 403
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching page: {e}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    job_listings = []

    # Find the specific container for job cards
    results_container = soup.find(id="ResultsContainer")
    if not results_container:
        print("❌ Could not find the results container on the page.")
        return []

    job_cards = results_container.find_all("div", class_="card-content")

    for card in job_cards:
        try:
            # Extract title
            title_element = card.find("h2", class_="title")
            title = title_element.text.strip()
            
            # Extract company
            company_element = card.find("h3", class_="company")
            company = company_element.text.strip()
            
            # Extract location
            location_element = card.find("p", class_="location")
            location = location_element.text.strip()
            
            # Extract link (The second <a> tag usually contains the 'Apply' link)
            link_element = card.find_all("a")[1]['href']

            job_listings.append({
                'Title': title,
                'Company': company,
                'Location': location,
                'Link': link_element,
                'Date_Scraped': datetime.date.today().strftime('%Y-%m-%d')
            })
        except Exception as e:
            # If one card fails, print error but continue to the next one
            print(f"⚠️ Skipping a job card due to error: {e}")
            continue

    print(f"✅ Successfully scraped {len(job_listings)} jobs.")
    return job_listings

def transform_data(data):
    """Converts the list of dictionaries into a DataFrame and cleans it."""
    if not data:
        return pd.DataFrame() 

    df = pd.DataFrame(data)
    
    # Simple Cleaning: remove duplicates if the same job title/company appears twice
    df.drop_duplicates(subset=['Title', 'Company'], keep='first', inplace=True)
    
    print(f"✅ Data transformed. {len(df)} unique records ready to load.")
    return df

def load_data(df, table_name='jobs'):
    """Loads the transformed DataFrame into the Neon Cloud Database."""
    if df.empty:
        print("⚠️ No data to load.")
        return

    # Get the URL from the .env file
    db_url = os.getenv('DATABASE_URL')
    
    if not db_url:
        print("❌ Error: DATABASE_URL not found. Did you create the .env file?")
        return

    try:
        # Create connection engine
        print("🔌 Connecting to Neon database...")
        engine = create_engine(db_url)
        
        # Write data to the cloud (append mode keeps old data)
        df.to_sql(table_name, engine, if_exists='append', index=False)
        print("✅ Success! Data loaded into Neon Database.")
        
    except Exception as e:
        print(f"❌ Database Error: {e}")

if __name__ == '__main__':
    # 1. Extract
    raw_data = scrape_jobs()
    
    # 2. Transform
    clean_df = transform_data(raw_data)
    
    # 3. Load
    load_data(clean_df)