# 📊 Automated Job Market Intelligence Dashboard

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/) 
![Python](https://img.shields.io/badge/Python-3.9-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-NeonDB-green)
![Status](https://img.shields.io/badge/Status-Live-success)

## 🚀 Project Overview
This project is an end-to-end **ETL (Extract, Transform, Load) pipeline** that tracks Python job market trends. It automatically scrapes job listings daily, stores them in a cloud database, and visualizes the data through an interactive dashboard.

**✨ Key Features
Automated Data Extraction: A Python script runs automatically every 24 hours via GitHub Actions to scrape new job listings.

Cloud Data Persistence: Data is cleaned (Pandas) and stored securely in a PostgreSQL (Neon) database, preventing data loss on app restarts.

Interactive Dashboard: Built with Streamlit, featuring:

📅 Date Range Filtering

🔍 Keyword Search (e.g., "Backend", "Junior")

📊 Interactive Charts (Plotly)

📥 CSV Data Export

Security: Uses environment variables and GitHub Secrets to protect database credentials.

🛠️ Tech Stack
Language: Python 3.9

Web Scraping: BeautifulSoup4, Requests

Data Manipulation: Pandas, NumPy

Database: PostgreSQL (hosted on Neon.tech), SQLAlchemy

Visualization: Streamlit, Plotly Express

DevOps/Automation: GitHub Actions (CI/CD), Streamlit Cloud

**🤖 Automation (GitHub Actions)
The scraping process is automated using a YAML workflow file located in .github/workflows/daily_scrape.yml.

Trigger: Scheduled Cron Job (Runs daily at 02:00 UTC).

Process: Sets up Python environment -> Installs dependencies -> Runs scraper.py -> Closes connection.

---

## 🏗️ Architecture
The system follows a modern serverless architecture:

```mermaid
graph LR
    A[GitHub Actions \n(Daily Automation)] -->|Runs Scraper| B(Python Script \n BeautifulSoup + Pandas)
    B -->|ETL Process| C[(Neon PostgreSQL \n Cloud Database)]
    D[Streamlit Cloud] -->|Queries Data| C
    D -->|Displays| E[Interactive Web Dashboard]


