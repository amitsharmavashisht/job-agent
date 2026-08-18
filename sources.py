import requests
from datetime import datetime
from models import Job
from config import SERPAPI_KEY, LOCATION, DATE_POSTED, RESULTS_PER_Q

def fetch_google_jobs(query: str) -> list[Job]:
    if not SERPAPI_KEY:
        return []
    params = {
        "engine": "google_jobs",
        "q": f"{query} in {LOCATION}",
        "hl": "en",
        "api_key": SERPAPI_KEY,
        "chips": f"date_posted:{DATE_POSTED}",
    }
    try:
        r = requests.get("https://serpapi.com/search", params=params, timeout=30)
        r.raise_for_status()
        jobs = []
        for j in r.json().get("jobs_results", [])[:RESULTS_PER_Q]:
            opts = j.get("detected_extensions", {})
            link = j.get("share_link", "")
            if j.get("related_links"):
                link = j["related_links"][0].get("link", link)
            jobs.append(Job(
                title=j.get("title", ""),
                company=j.get("company_name", ""),
                location=j.get("location", ""),
                source=f"Google Jobs · {j.get('via', '')}",
                link=link,
                salary=opts.get("salary", ""),
                description=j.get("description", "")[:500],
                posted_at=opts.get("posted_at", ""),
            ))
        return jobs
    except Exception as e:
        print(f"  ⚠️  Google Jobs error: {e}")
        return []

def fetch_remotive(query: str) -> list[Job]:
    try:
        r = requests.get("https://remotive.com/api/remote-jobs",
                         params={"search": query, "limit": RESULTS_PER_Q}, timeout=30)
        r.raise_for_status()
        return [Job(
            title=j.get("title", ""),
            company=j.get("company_name", ""),
            location=j.get("candidate_required_location", "Remote"),
            source="Remotive",
            link=j.get("url", ""),
            salary=j.get("salary", ""),
            posted_at=j.get("publication_date", "")[:10],
        ) for j in r.json().get("jobs", [])]
    except Exception as e:
        print(f"  ⚠️  Remotive error: {e}")
        return []

def fetch_arbeitnow(query: str) -> list[Job]:
    try:
        r = requests.get("https://www.arbeitnow.com/api/job-board-api", timeout=30)
        r.raise_for_status()
        words = query.lower().split()
        jobs = []
        for j in r.json().get("data", []):
            text = f"{j.get('title', '')} {' '.join(j.get('tags', []))}".lower()
            if any(w in text for w in words):
                jobs.append(Job(
                    title=j.get("title", ""),
                    company=j.get("company_name", ""),
                    location=j.get("location", ""),
                    source="Arbeitnow",
                    link=j.get("url", ""),
                    posted_at=datetime.fromtimestamp(j.get("created_at", 0)).strftime("%Y-%m-%d"),
                ))
        return jobs[:RESULTS_PER_Q]
    except Exception as e:
        print(f"  ⚠️  Arbeitnow error: {e}")
        return []