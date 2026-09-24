import requests
from bs4 import BeautifulSoup
import datetime
import os
import google.generativeai as genai

# Setup directories and keys
CLIPPINGS_DIR = "daily_clippings"
os.makedirs(CLIPPINGS_DIR, exist_ok=True)

API_KEY = os.getenv("GEMINI_API_KEY", "")
if API_KEY:
    genai.configure(api_key=API_KEY)

# Keywords for Marathi appointments and elections
KEYWORDS = [
    "निवड", "बिनविरोध", "अध्यक्ष", "उपाध्यक्ष", "सरपंच", 
    "उपसरपंच", "संचालक", "नियोजन", "ग्रामपंचायत", "जिल्हा परिषद", 
    "पंचायत समिती", "बँक", "सोसायटी", "नियुक्ती"
]

def fetch_daily_pudhari_kolhapur():
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    print(f"[{today_str}] Accessing Daily Pudhari Kolhapur edition...")
    
    # Official Pudhari Kolhapur online portal
    url = "https://pudhari.news/kolhapur"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            print("Failed to fetch Pudhari website.")
            return

        soup = BeautifulSoup(response.text, "html.parser")
        articles = soup.find_all("a")
        
        captured_count = 0
        for article in articles:
            text = article.get_text()
            # Check if article contains appointment keywords
            if any(keyword in text for keyword in KEYWORDS):
                link = article.get("href")
                if link and not link.startswith("http"):
                    link = "https://pudhari.news" + link
                
                print(f"Found relevant appointment news: {text.strip()[:50]}...")
                
                # Save item details to clippings folder
                file_name = f"{CLIPPINGS_DIR}/pudhari_{today_str}_{captured_count+1}.txt"
                with open(file_name, "w", encoding="utf-8") as f:
                    f.write(f"Title: {text.strip()}\nURL: {link}\nDate: {today_str}\n")
                
                captured_count += 1
                if captured_count >= 5: # Limit to top 5 relevant daily news items
                    break
                    
        print(f"Successfully processed {captured_count} news items from Daily Pudhari.")
        
    except Exception as e:
        print(f"Error fetching Daily Pudhari: {e}")

if __name__ == "__main__":
    fetch_daily_pudhari_kolhapur()
  
