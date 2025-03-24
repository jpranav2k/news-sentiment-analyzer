---
title: News Sentiment Analyzer
emoji: 📰
colorFrom: indigo
colorTo: blue
sdk: streamlit
app_file: streamlit_app.py
pinned: false
---

# 📰 News Sentiment Analyzer with Hindi TTS

This web application fetches news articles related to a company, analyzes their sentiment, extracts key topics, summarizes them, and generates Hindi audio using Text-to-Speech (TTS).

---

## ✅ Features

- Fetches real-time news using Bing News
- Summarizes articles using TF-IDF and PageRank (TextRank)
- Performs sentiment analysis using VADER
- Extracts topics using Latent Dirichlet Allocation (LDA)
- Generates Hindi audio summaries using gTTS + Google Translate
- Streamlit-based user interface
- FastAPI backend serving analysis through APIs

---

## 💻 Tech Stack

- **Frontend**: Streamlit
- **Backend**: FastAPI
- **Web Scraping**: BeautifulSoup
- **NLP**: VADER, NLTK, LDA, TF-IDF
- **TTS**: gTTS, googletrans
- **Deployment**: Hugging Face Spaces


## 📁 Project Structure
```
News-Sentiment-Analyzer/
│
├── Backend/
│   ├── main.py           # FastAPI app
│   ├── utils.py          # Utility functions (NLP, scraping, TTS)
│   └── static/audio/     # Audio file storage
│
├── streamlit_app.py      # Streamlit frontend
├── requirements.txt      # Python dependencies
└── README.md             # This file
```


## ⚙️ Setup Instructions

### 1. Clone the repository

git clone https://github.com/jpranav2k/news-sentiment-analyzer.git


### 2. Install dependencies
pip install -r requirements.txt

---

## 🚀 Running Locally

### Start the FastAPI Backend

cd Backend uvicorn main:app --reload

### Start the Streamlit Frontend (in another terminal)

streamlit run streamlit_app.py

Open your browser at: `http://localhost:8501`

---

## 🚀 Deploying on Hugging Face Spaces

1. Push this project to a GitHub repository
2. Go to https://huggingface.co/spaces → Create New Space
3. Choose:
   - SDK: **Streamlit**
   - Link your GitHub repo
4. Ensure your `requirements.txt` includes all dependencies
5. Hugging Face will auto-run `streamlit_app.py`

---

## ℹ️ Notes

- Ensure that the backend is running before accessing the frontend.
- All generated Hindi TTS files are stored in `static/audio/` and served via FastAPI.
- The API endpoints include:
  - `GET /get-news?company=<company_name>`
  - `POST /analyze` (with list of title-URL pairs)

---

## 📬 Author

Developed by **Pranav J**

GitHub: [jpranav2k](https://github.com/jpranav2k)


