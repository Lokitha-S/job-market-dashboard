import os
import random
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def seed_database():
    print("🌱 Seeding database with fake historical data...")
    
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ Error: DATABASE_URL not found.")
        return

    engine = create_engine(db_url)
    
    # 1. Get the real data you scraped today
    try:
        df_real = pd.read_sql("SELECT * FROM jobs", engine)
    except Exception:
        print("❌ No data found. Run scraper.py first!")
        return

    if df_real.empty:
        print("⚠️ DataFrame is empty. Run scraper.py first.")
        return

    # 2. Create fake history for the last 7 days
    fake_data = []
    
    # We will simulate data for the past 7 days
    for i in range(1, 8):
        # Calculate the date: "i" days ago
        fake_date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        
        # Pick a random number of jobs to "have found" on that day (e.g., between 10 and 50)
        daily_sample = df_real.sample(n=random.randint(10, 50), replace=True)
        
        # Update the date for these rows
        daily_sample['Date_Scraped'] = fake_date
        
        # OPTIONAL: Make locations more repetitive so the bar chart looks better
        # We replace random locations with 'New York', 'Remote', etc.
        common_locations = ['Remote', 'New York, NY', 'San Francisco, CA', 'Austin, TX', 'Chicago, IL']
        daily_sample['Location'] = daily_sample['Location'].apply(
            lambda x: random.choice(common_locations) if random.random() > 0.5 else x
        )

        fake_data.append(daily_sample)

    # 3. Combine and Load
    if fake_data:
        df_history = pd.concat(fake_data)
        df_history.to_sql('jobs', engine, if_exists='append', index=False)
        print(f"✅ Successfully added {len(df_history)} rows of historical data.")
        print("🚀 Refresh your Streamlit dashboard now!")

if __name__ == '__main__':
    seed_database()