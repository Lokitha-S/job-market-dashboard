import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import os
from datetime import datetime
from dotenv import load_dotenv

# 1. Load Config (for local .env variables)
load_dotenv()

# 2. Database Connection Function
@st.cache_data(ttl=600)  # Cache data for 10 minutes to improve performance
def load_data():
    """Fetches data from Neon Cloud Database and ensures correct types."""
    db_url = os.getenv('DATABASE_URL')
    
    # Fallback for Streamlit Cloud (when we deploy later)
    if not db_url and "DATABASE_URL" in st.secrets:
        db_url = st.secrets["DATABASE_URL"]
    
    if not db_url:
        st.error("❌ Database URL not found. Check .env file or Streamlit Secrets.")
        return pd.DataFrame()

    try:
        engine = create_engine(db_url)
        df = pd.read_sql("SELECT * FROM jobs", engine)
        
        # Ensure the Date column is actually a datetime object, not a string
        df['Date_Scraped'] = pd.to_datetime(df['Date_Scraped'])
        return df
    except Exception as e:
        st.error(f"❌ DB Error: {e}")
        return pd.DataFrame()

# 3. Main Dashboard Layout
def main():
    st.set_page_config(page_title="Job Market Tracker", layout="wide", page_icon="📊")
    
    # --- Custom CSS for clearer metrics ---
    st.markdown("""
    <style>
    div.stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("📊 Python Job Market Intelligence")
    st.markdown("Automated scraper running daily on GitHub Actions • Data stored in Neon (PostgreSQL)")

    # Load Data
    with st.spinner('Fetching latest data from the cloud...'):
        df = load_data()

    if df.empty:
        st.warning("No data found. Please run the scraper first.")
        return

    # --- SIDEBAR: Controls & Filters ---
    st.sidebar.header("🔍 Filter Controls")
    
    # 1. Date Range Picker
    min_date = df['Date_Scraped'].min().date()
    max_date = df['Date_Scraped'].max().date()
    
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # 2. Company Filter
    company_list = ["All Companies"] + sorted(list(df['Company'].unique()))
    selected_company = st.sidebar.selectbox("Filter by Company", company_list)
    
    # 3. Keyword Search
    search_term = st.sidebar.text_input("Search Job Title (e.g., 'Senior', 'Backend')", "")

    # --- Apply Filters Logic ---
    # Filter by Date
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
        mask = (df['Date_Scraped'].dt.date >= start_date) & (df['Date_Scraped'].dt.date <= end_date)
        df_filtered = df.loc[mask]
    else:
        df_filtered = df 

    # Filter by Company
    if selected_company != "All Companies":
        df_filtered = df_filtered[df_filtered['Company'] == selected_company]

    # Filter by Keyword
    if search_term:
        df_filtered = df_filtered[df_filtered['Title'].str.contains(search_term, case=False, na=False)]

    # --- KPI Metrics Row (Updates based on filters) ---
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate delta (difference from total)
    total_jobs = len(df)
    filtered_jobs = len(df_filtered)
    
    col1.metric("Jobs Found", filtered_jobs, delta=f"{filtered_jobs - total_jobs} vs Total" if filtered_jobs != total_jobs else None)
    col2.metric("Active Companies", df_filtered['Company'].nunique())
    
    # Calculate Top Location safely
    if not df_filtered.empty:
        top_loc = df_filtered['Location'].mode()[0]
    else:
        top_loc = "N/A"
    col3.metric("Top Location", top_loc)
    
    col4.metric("Days Tracked", (max_date - min_date).days + 1)

    st.markdown("---")

    # --- Charts Row ---
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("📈 Hiring Trends")
        if not df_filtered.empty:
            # Group by date to count jobs per day
            daily_counts = df_filtered.groupby(df_filtered['Date_Scraped'].dt.date).size().reset_index(name='Count')
            # Create Area Chart
            fig_date = px.area(daily_counts, x='Date_Scraped', y='Count', markers=True, color_discrete_sequence=['#FF4B4B'])
            st.plotly_chart(fig_date, use_container_width=True)
        else:
            st.info("No data available for current filters.")

    with c2:
        st.subheader("📍 Location Hotspots")
        if not df_filtered.empty:
            # Get top 7 locations
            loc_counts = df_filtered['Location'].value_counts().head(7).reset_index()
            loc_counts.columns = ['Location', 'Count']
            # Create Pie Chart
            fig_loc = px.pie(loc_counts, names='Location', values='Count', hole=0.4)
            st.plotly_chart(fig_loc, use_container_width=True)
        else:
            st.info("No data available for current filters.")

    # --- Data Table & Download Section ---
    st.markdown("---")
    st.subheader("📋 Detailed Job List")
    
    col_search, col_download = st.columns([4, 1])
    
    with col_download:
        # CSV Download Button
        csv = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"job_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )

    st.dataframe(
        df_filtered[['Date_Scraped', 'Title', 'Company', 'Location', 'Link']],
        use_container_width=True,
        hide_index=True
    )

if __name__ == '__main__':
    main()