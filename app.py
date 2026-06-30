import re
import requests
import pandas as pd
import streamlit as st
from bs4 import BeautifulSoup

st.set_page_config(page_title="Custom Weekly Lead Generator", page_icon="🔍")
st.title("📋 Advanced Weekly Lead & Name Scraper")
st.write("Paste your target website links below to extract names, titles, and email addresses.")

urls_input = st.text_area("Enter URLs (one per line):", height=150)

if st.button("Launch Advanced Scraper"):
    if not urls_input.strip():
        st.warning("Please add at least one URL.")
    else:
        urls = [url.strip() for url in urls_input.split("\n") if url.strip()]
        results = []
        
        progress_bar = st.progress(0)
        
        for index, url in enumerate(urls):
            progress_bar.progress((index + 1) / len(urls))
            
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                response = requests.get(url, headers=headers, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for 'mailto' links first (best way to find names tied to emails)
                mailtos = soup.select('a[href^=mailto]')
                found_emails = set()
                
                for link in mailtos:
                    email = link['href'].replace('mailto:', '').strip().split('?')[0]
                    # Regex check to ensure it's a valid email structure
                    if re.match(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', email):
                        # Contextual Guessing: Look at the text inside the link or the block containing it
                        surrounding_text = link.find_parent().get_text(separator=" | ").strip() if link.find_parent() else link.get_text().strip()
                        
                        # Clean up text chunks
                        clean_context = " ".join(surrounding_text.split())
                        
                        results.append({
                            "Source URL": url, 
                            "Detected Email": email,
                            "Context / Name & Title Data": clean_context[:150] # Grabs the closest 150 characters
                        })
                        found_emails.add(email)
                
                # Fallback: Plain text regex search for pages without 'mailto' hyperlinks
                email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                all_text_emails = set(re.findall(email_pattern, response.text))
                
                # Add plain text emails that weren't caught in links
                leftover_emails = all_text_emails - found_emails
                for email in leftover_emails:
                    results.append({
                        "Source URL": url, 
                        "Detected Email": email,
                        "Context / Name & Title Data": "Found in plain text (No nearby HTML structure)"
                    })
                    
                if not found_emails and not leftover_emails:
                    results.append({"Source URL": url, "Detected Email": "No emails found", "Context / Name & Title Data": "N/A"})
                    
            except Exception as e:
                results.append({"Source URL": url, "Detected Email": "Error: Could not load site", "Context / Name & Title Data": str(e)})

        # Process and display dataframe
        df = pd.DataFrame(results)
        st.success(f"Scraping complete! Found data across {len(urls)} sites.")
        st.dataframe(df)
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Rich Lead List as CSV",
            data=csv,
            file_name="weekly_rich_marketing_leads.csv",
            mime="text/csv",
        )
