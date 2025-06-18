import requests
from dotenv import load_dotenv
import os
from serpapi import GoogleSearch  # Make sure you pip install serpapi
import trafilatura

load_dotenv()  # Load variables from .env
SERP_API_KEY = os.getenv("SERPAPI_KEY")



def search_web_snippets(query, max_results=2):
    url = "https://serpapi.com/search"
    params = {
        "q": query,
        "api_key": SERP_API_KEY,
        "engine": "google",
        "num": max_results
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        results = data.get("organic_results", [])[:max_results]
        return [r.get("snippet", "") for r in results if r.get("snippet")]
    except Exception as e:
        return [f"Error fetching search results: {e}"]
    


def search_web_pages(query, max_results=2):
    params = {
        "q": query,
        "api_key": SERP_API_KEY,
        "engine": "google",
        "num": max_results
    }
    search = GoogleSearch(params)
    results = search.get_dict()

    links = []
    for result in results.get("organic_results", []):
        link = result.get("link")
        if link:
            links.append(link)
    return links


def extract_clean_text(url):
    downloaded = trafilatura.fetch_url(url)
    if downloaded:
        return trafilatura.extract(downloaded)
    return ""

    
def fetch_youtube_videos(topic, target_duration=3600, max_results=2):
    import requests
    from dotenv import load_dotenv
    import os

    load_dotenv()
    SERP_API_KEY = os.getenv("SERPAPI_KEY")

    url = "https://serpapi.com/search"
    params = {
        "engine": "youtube",
        "search_query": topic,
        "api_key": SERP_API_KEY,
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        items = data.get("video_results", [])[:max_results]

        results = []
        total_duration = 0

        def parse_duration(duration_str):
            parts = list(map(int, duration_str.split(":")))
            if len(parts) == 3:
                return parts[0] * 3600 + parts[1] * 60 + parts[2]
            elif len(parts) == 2:
                return parts[0] * 60 + parts[1]
            elif len(parts) == 1:
                return parts[0]
            else:
                return 0

        for item in items:
            title = item.get("title")
            link = item.get("link")
            duration_str = item.get("length")

            if not title or not link or not duration_str:
                continue

            duration_sec = parse_duration(duration_str)

            # Skip videos longer than target duration
            if duration_sec > target_duration:
                continue

            # Stop if adding this would exceed the limit
            if total_duration + duration_sec > target_duration:
                continue

            results.append({
                "title": title,
                "link": link,
                "duration": duration_str
            })
            total_duration += duration_sec

            if total_duration >= target_duration:
                break

        return results

    except Exception as e:
        return [{"title": "Error", "link": "", "duration": str(e)}]

if __name__ == "__main__":
    from web_search import fetch_youtube_videos
    videos = fetch_youtube_videos("AI ethics", target_duration=3600)        
    total = 0
    for v in videos:
        print(f"{v['title']} – {v['duration']} – {v['link']}")
    print(f"Total videos: {len(videos)}")       