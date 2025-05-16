import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import pandas as pd
import json
import warnings
import re

# Suppress SSL warnings (optional: for local dev only)
warnings.filterwarnings("ignore", message="Unverified HTTPS request")

# Configure Gemini API
genai.configure(api_key="#############")  # Replace with your actual Gemini API key

# Function to scrape data from a webpage
def scrape_data(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        }
        response = requests.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(response.content, 'html.parser')
        text_data = soup.get_text(separator=' ', strip=True)
        return text_data
    except Exception as e:
        return f"Error during scraping: {e}"


# Function to extract information using Gemini
def extract_information_with_gemini(text_data):
    model = genai.GenerativeModel('gemini-2.0-flash')
    prompt = f"""
    Extract the following information from the given text and return it as a raw JSON dictionary.
    Do not include any formatting (no markdown or backticks).
    
    Fields: vendor, series,Exterior Design,Technology and Connectivity,Sustainability,Convenience,
    Customization Options

    Text:
    {text_data}
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating response: {e}"
    
# Streamlit App
st.title("Web Scraping and Gemini Extraction App")

url = st.text_input("Enter the URL to scrape:")
if st.button("Scrape and Extract"):
    if url:
        with st.spinner('Scraping data...'):
            text_data = scrape_data(url)
        st.success('Data scraped successfully!')

        st.write("### Scraped Text (Preview):")
        st.text(text_data[:1000])  # Show partial text

        with st.spinner('Extracting information using Gemini...'):
            extracted_data = extract_information_with_gemini(text_data)

        if "Error" in extracted_data:
            st.error(extracted_data)
        else:
            st.success('Information extracted successfully!')
            st.write("### Extracted JSON (Raw):")
            st.text(extracted_data)

            # Clean Gemini output to remove markdown formatting if any
            cleaned_json = re.sub(r"(?:json)?", "", extracted_data).strip()
            cleaned_json = cleaned_json.rstrip("").strip()

            try:
                # Parse JSON string to dict
                data_dict = json.loads(cleaned_json)
                df = pd.DataFrame([data_dict])
                st.write("### Extracted Table:")
                st.write(df)

                # Download as CSV
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download data as CSV",
                    data=csv,
                    file_name='extracted_data.csv',
                    mime='text/csv',
                )
            except json.JSONDecodeError as e:
                st.error(f"Could not parse JSON: {e}")
    else:
        st.error("Please enter a URL.")