"""
🔍 JOB HUNTER AGENT v2 - Amit Sharma
Finds AI/ML jobs, verifies links, matches resume, sends Telegram + Email alerts.
"""

import csv
import time
import os
from dataclasses import asdict
from models import Job
from config import SEARCH_QUERIES
from sources import fetch_google_jobs, fetch_remotive, fetch_arbeitnow
from processors import verify_job_link, classify_job, match_resume, send_telegram_alert, send_email_alert


class JobAgent:
    def __init__(self):
        self.jobs: dict[str, Job] = {}
        os.makedirs("output", exist_ok=True)

    def collect(self):
        print("🤖 Job Agent starting...\n")
        for q in SEARCH_QUERIES:
            print(f"  🔎 {q}")
            found = fetch_google_jobs(q) + fetch_remotive(q) + fetch_arbeitnow(q)
            for job in found:
                self.jobs.setdefault(job.key(), job)
            print(f"     → {len(found)} found | {len(self.jobs)} unique\n")
            time.sleep(1)

    def process(self) -> list[Job]:
        jobs = list(self.jobs.values())
        print("🏷️  Classifying...")
        jobs = [classify_job(j) for j in jobs]
        
        print("🔗 Verifying top 20 links...")
        for j in jobs[:20]:
            verify_job_link(j)
            time.sleep(0.5)
            
        print("📄 Matching resume...")
        jobs = [match_resume(j) for j in jobs]
        return self.rank(jobs)

    def rank(self, jobs: list[Job]) -> list[Job]:
        def score(j: Job):
            s = 0
            text = f"{j.title} {j.description}".lower()
            if any(k in text for k in ["fresher", "intern", "entry level"]): 
                s += 10
            if j.verification_status == "verified": 
                s += 8
            if j.verification_status == "expired": 
                s -= 100
            s += j.match_score // 5
            if any(k in text for k in ["senior", "lead", "principal"]): 
                s -= 30
            return s
        return sorted(jobs, key=score, reverse=True)

    def show(self, jobs: list[Job], n=10):
        icons = {"verified": "✅", "likely_real": "🟡", "expired": "❌", "unverified": "⬜"}
        print(f"\n{'═' * 60}\n🏆 TOP {min(n, len(jobs))} PICKS\n{'═' * 60}")
        for i, j in enumerate(jobs[:n], 1):
            ic = icons.get(j.verification_status, "⬜")
            print(f"\n{i}. {j.title} ({j.match_score}% Match)")
            print(f"   🏢 {j.company} | 📍 {j.location} | 🏷️ {j.category.upper()}")
            print(f"   {ic} {j.verification_status} | 💰 {j.salary or '—'}")
            print(f"   🔗 {j.link}")

    def export(self, jobs: list[Job]):
        if not jobs: 
            return
        filename = f"output/jobs_{time.strftime('%Y%m%d_%H%M')}.csv"
        with open(filename, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(asdict(jobs[0]).keys()))
            w.writeheader()
            for j in jobs:
                row = asdict(j)
                row["match_reasons"] = "; ".join(row["match_reasons"])
                w.writerow(row)
        print(f"\n💾 Saved → {filename}")

    def run(self):
        """Main pipeline: Collect → Process → Show → Export → Alert"""
        self.collect()
        
        if not self.jobs:
            print("😕 No jobs found.")
            return
        
        ranked = self.process()
        self.show(ranked)
        self.export(ranked)

        # ── SEND TELEGRAM ALERTS (Lowered threshold for freshers) ──
        print("\n📱 Sending Telegram alerts...")
        telegram_jobs = [j for j in ranked[:5] if j.match_score >= 50]
        for job in telegram_jobs:
            send_telegram_alert(job)
            time.sleep(1)
        print(f"✅ {len(telegram_jobs)} Telegram alert(s) sent!")

        # ── SEND EMAIL ALERTS (Lowered threshold for freshers) ──
        print("\n📧 Sending email summary...")
        email_jobs = [j for j in ranked if j.match_score >= 40]
        send_email_alert(email_jobs)


if __name__ == "__main__":
    JobAgent().run()