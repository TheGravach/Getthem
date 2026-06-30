import re
import requests
import pandas as pd
import streamlit as str

# App interface styling
str.set_page_config(page_title="Custom Weekly Lead Generator", page_icon="🔍")
str.title("📋 Weekly Email & Lead Scraper")
str.write("Paste your target website links below to extract email addresses into a clean spreadsheet.")

# User Input Box
urls_input = str.text_area("Enter URLs (one per line):", height=150)

# Run Button
if str.button("Launch Scraper & Extract Emails"):
    if not urls_input.strip():
        str.warning("Please add at least one URL.")
    else:
        urls = [url.strip() for url in urls_input.split("\n") if url.strip()]
        results = []
        
        progress_bar = str.progress(0)
        
        for index, url in enumerate(urls):
            # Update progress
            progress_bar.progress((index + 1) / len(urls))
            
            try:
                # Add a browser-like header to prevent instant blocks
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                response = requests.get(url, headers=headers, timeout=10)
                
                # Extract all unique emails
                email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                emails = list(set(re.findall(email_pattern, response.text)))
                
                if emails:
                    for email in emails:
                        results.append({"Source URL": url, "Detected Email": email})
                else:
                    results.append({"Source URL": url, "Detected Email": "No emails found"})
                    
            except Exception as e:
                results.append({"Source URL": url, "Detected Email": f"Error: Could not load site"})

        # Output Data Frame
        df = pd.DataFrame(results)
        str.success(f"Scraping complete! Found data across {len(urls)} sites.")
        str.dataframe(df)
        
        # Turn data into a downloadable Excel/CSV file button
        csv = df.to_csv(index=False).encode('utf-8')
        str.download_button(
            label="📥 Download Leaddist as CSV",
            data=csv,
            file_name="weekly_marketing_leads.csv",
            mime="text/csv",
        )
