from dataclasses import dataclass, field, asdict
from datetime import datetime

@dataclass
class Job:
    title: str
    company: str
    location: str
    source: str
    link: str
    salary: str = ""
    description: str = ""
    scraped_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))
    posted_at: str = ""
    verification_status: str = "unverified"
    last_verified: str = ""
    category: str = "other"
    match_score: int = 0
    match_reasons: list = field(default_factory=list)

    def key(self):
        # Unique key includes location to avoid merging different offices
        return f"{self.title.lower().strip()}|{self.company.lower().strip()}|{self.location.lower().strip()}"