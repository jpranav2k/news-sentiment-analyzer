from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
from utils import get_bing_news, extract_news_content

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ArticleLink(BaseModel):
    title: str
    url: str

class NewsLinks(BaseModel):
    news_links: List[ArticleLink]

@app.get("/")
def home():
    return {"message": "FastAPI backend is running."}

@app.get("/get-news")
def get_news(company: str = Query(..., description="Company name")):
    links = get_bing_news(company)
    return {"news_links": links}

@app.post("/analyze")
def analyze_news(data: NewsLinks):
    try:
        formatted_links = [(item.title, item.url) for item in data.news_links]
        results = extract_news_content(formatted_links)
        return results
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error during analysis: {str(e)}")
