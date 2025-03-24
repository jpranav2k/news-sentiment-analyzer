import streamlit as st
import requests

st.set_page_config(page_title="Company News Sentiment Analyzer", layout="wide")
st.title("📰 Company News Sentiment Analyzer with Hindi TTS")

BASE_URL = "http://127.0.0.1:8000"  # FastAPI running locally

company_name = st.text_input("Enter a Company Name", "")

if st.button("Analyze News"):
    if not company_name.strip():
        st.warning("Please enter a company name.")
    else:
        with st.spinner("Fetching and analyzing articles from API..."):
            try:
                # Step 1: Fetch news links
                news_links_response = requests.get(f"{BASE_URL}/get-news", params={"company": company_name})
                news_links_response.raise_for_status()
                news_links = news_links_response.json().get("news_links", [])

                if not news_links:
                    st.warning("No news articles found. Try a different company.")
                else:
                    # Step 2: Format links for backend
                    formatted_links = [{"title": title, "url": url} for title, url in news_links]

                    # Step 3: Send for analysis
                    response = requests.post(f"{BASE_URL}/analyze", json={"news_links": formatted_links})
                    response.raise_for_status()
                    results = response.json()

                    if "error" in results:
                        st.warning(results["error"])
                    else:
                        for title, data in results.items():
                            with st.expander(title):
                                st.markdown(f"🔗 [Read Full Article]({data['url']})")
                                st.write("**Summary:**", data["summary"])
                                st.write("**Sentiment:**", data["sentiment"])
                                st.write("**Topics:**", data["topics"])
                                st.write("**Analysis:**", data["analysis"])
                                if data["audio"]:
                                    audio_url = f"{BASE_URL}/{data['audio']}"
                                    st.audio(audio_url, format="audio/mp3", start_time=0)

            except requests.exceptions.RequestException as e:
                st.error(f"Network error: {e}")
            except Exception as e:
                st.error(f"Failed to fetch data from backend: {e}")
