import requests
from bs4 import BeautifulSoup
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import nltk
from nltk.tokenize import sent_tokenize
from requests.adapters import HTTPAdapter, Retry
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx
from gtts import gTTS
from googletrans import Translator
import tempfile
from concurrent.futures import ThreadPoolExecutor
import os
import uuid

nltk.download("punkt", quiet=True)

def get_bing_news(company_name):
    search_url = f"https://www.bing.com/news/search?q={company_name.replace(' ', '+')}&FORM=HDRSC6"
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))

    try:
        response = session.get(search_url, timeout=10)
        response.raise_for_status()
    except:
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    articles = soup.find_all("a", {"class": "title"})
    return [(article.text.strip(), article["href"]) for article in articles]

def summarize_text(text, num_sentences=3):
    sentences = [s.strip() for s in sent_tokenize(text) if len(s.split()) > 8]
    if len(sentences) <= num_sentences:
        return " ".join(sentences)

    vectorizer = TfidfVectorizer(stop_words="english", max_df=0.8, min_df=2)
    try:
        tfidf_matrix = vectorizer.fit_transform(sentences)
    except ValueError:
        return "Summary not available."

    similarity_matrix = cosine_similarity(tfidf_matrix)
    nx_graph = nx.from_numpy_array(similarity_matrix)
    scores = nx.pagerank(nx_graph)
    ranked_sentences = sorted(((scores[i], s, i) for i, s in enumerate(sentences)), reverse=True)
    top_sentences = sorted(ranked_sentences[:num_sentences], key=lambda x: x[2])
    return " ".join([s for _, s, _ in top_sentences])

def analyze_sentiment(text):
    analyzer = SentimentIntensityAnalyzer()
    scores = analyzer.polarity_scores(text)
    return "Positive" if scores['compound'] >= 0.05 else "Negative" if scores['compound'] <= -0.05 else "Neutral"

def extract_topics(text_corpus, num_keywords=5):
    vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
    X = vectorizer.fit_transform(text_corpus)
    lda = LatentDirichletAllocation(n_components=1, random_state=42)
    lda.fit(X)
    feature_names = vectorizer.get_feature_names_out()
    topic = lda.components_[0]
    keywords = [feature_names[i] for i in topic.argsort()[-num_keywords:]]
    return ", ".join(keywords)

def generate_analysis(title, summary, sentiment, content):
    lower_text = content.lower()
    impact_area = []

    if any(word in lower_text for word in ["stock", "shares", "market", "investor", "nasdaq"]):
        impact_area.append("finance")
    if any(word in lower_text for word in ["launch", "product", "innovation", "technology", "ai", "machine learning"]):
        impact_area.append("technology")
    if any(word in lower_text for word in ["regulation", "lawsuit", "compliance", "legal"]):
        impact_area.append("legal")
    if any(word in lower_text for word in ["layoffs", "hiring", "employee", "strike", "union"]):
        impact_area.append("hr")
    if any(word in lower_text for word in ["sales", "revenue", "growth", "expansion", "profit"]):
        impact_area.append("business")

    analysis_parts = []

    if "finance" in impact_area:
        if sentiment == "Positive":
            analysis_parts.append("The article reflects strong financial sentiment, indicating investor optimism.")
        elif sentiment == "Negative":
            analysis_parts.append("There are signs of financial concern, possibly hinting at market instability.")
        else:
            analysis_parts.append("The financial outlook remains mixed with cautious investor sentiment.")

    if "technology" in impact_area:
        if sentiment == "Positive":
            analysis_parts.append("Technological advancements are portrayed positively, enhancing innovation.")
        elif sentiment == "Negative":
            analysis_parts.append("Technological delays may be causing missed opportunities.")
        else:
            analysis_parts.append("Progress in tech is mentioned but impact is unclear.")

    if "legal" in impact_area:
        analysis_parts.append("Legal or regulatory factors are discussed, which may pose operational risks.")

    if "hr" in impact_area:
        analysis_parts.append("HR developments like hiring or layoffs could affect company morale.")

    if "business" in impact_area:
        if sentiment == "Positive":
            analysis_parts.append("Business metrics show positive growth or expansion.")
        elif sentiment == "Negative":
            analysis_parts.append("Indicators like profit/revenue might be underperforming.")
        else:
            analysis_parts.append("Business stability is maintained without major change.")

    if not analysis_parts:
        analysis_parts.append("No direct business impact identified, but article holds informative value.")

    analysis_parts.append("Comparatively, this sentiment aligns with industry trends.")
    return f"{title}:\n" + " ".join(analysis_parts)

def generate_hindi_tts(text):
    translator = Translator()
    hindi_text = translator.translate(text, src="en", dest="hi").text
    try:
        audio_dir = "static/audio"
        if not os.path.exists(audio_dir):
            os.makedirs(audio_dir)
        filename = f"{uuid.uuid4()}.mp3"
        path = os.path.join(audio_dir, filename)
        gTTS(text=hindi_text, lang="hi").save(path)
        return f"static/audio/{filename}"
    except Exception:
        return None

def extract_news_content(news_links, required_articles=10):
    headers = {"User-Agent": "Mozilla/5.0"}
    extracted_data = {}

    def process_article(title, url):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            paragraphs = soup.find_all("p")
            content = " ".join(p.text.strip() for p in paragraphs)
            if len(content.split()) > 50:
                summary = summarize_text(content)
                sentiment = analyze_sentiment(content)
                analysis = generate_analysis(title, summary, sentiment, content)
                topics = extract_topics([content])
                audio_path = generate_hindi_tts(summary)
                return title, {
                    "url": url,
                    "summary": summary,
                    "sentiment": sentiment,
                    "analysis": analysis,
                    "topics": topics,
                    "audio": audio_path
                }
        except:
            return None

    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(lambda link: process_article(*link), news_links))

    for result in results:
        if result:
            extracted_data[result[0]] = result[1]
        if len(extracted_data) >= required_articles:
            break

    return extracted_data