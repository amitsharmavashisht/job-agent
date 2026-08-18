"""
processors.py - Job verification, classification, resume matching & alerts
"""

import requests
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from models import Job
from config import (
    MY_RESUME_SKILLS, 
    MY_STRONG_SKILLS, 
    FRESHER_KEYWORDS,
    TELEGRAM_BOT_TOKEN, 
    TELEGRAM_CHAT_ID,
    EMAIL_SENDER,
    EMAIL_PASSWORD,
    EMAIL_RECEIVER
)

# ═══════════════════════════════════════════════
# CATEGORY KEYWORDS
# ═══════════════════════════════════════════════

CATEGORY_KEYWORDS = {
    "ai_ml": [
        "machine learning", "deep learning", "nlp", "computer vision", 
        "llm", "pytorch", "tensorflow", "rag", "langchain", "generative ai",
        "data scientist", "ml engineer", "transformer", "neural network"
    ],
    "software": [
        "software engineer", "developer", "full stack", "backend", 
        "frontend", "api", "microservice", "devops", "sre", "flask", "fastapi"
    ],
    "data": [
        "data analyst", "data engineer", "etl", "sql", "dashboard", 
        "tableau", "power bi", "data pipeline", "warehouse", "pandas"
    ],
    "design": [
        "ux", "ui", "product design", "figma", "user research"
    ],
    "automation": [
        "automation", "n8n", "workflow", "bot", "rpa", "scripting"
    ]
}

# ═══════════════════════════════════════════════
# JOB VERIFICATION
# ═══════════════════════════════════════════════

def verify_job_link(job: Job) -> Job:
    """Check if the job URL is still live."""
    try:
        r = requests.head(job.link, timeout=10, allow_redirects=True)
        job.last_verified = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        if r.status_code == 200:
            try:
                page = requests.get(job.link, timeout=10)
                text = page.text.lower()
                expired_markers = [
                    "position filled", "no longer accepting",
                    "application period has ended", "job has been closed",
                    "this position is no longer available"
                ]
                if any(m in text for m in expired_markers):
                    job.verification_status = "expired"
                else:
                    job.verification_status = "verified"
            except Exception:
                job.verification_status = "likely_real"
        elif r.status_code in (403, 404, 410):
            job.verification_status = "expired"
        else:
            job.verification_status = "likely_real"
            
    except Exception as e:
        job.verification_status = "unverified"
        job.last_verified = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    return job

# ═══════════════════════════════════════════════
# JOB CLASSIFICATION
# ═══════════════════════════════════════════════

def classify_job(job: Job) -> Job:
    """Categorize the job based on title + description."""
    text = f"{job.title} {job.description}".lower()
    best_cat, best_score = "other", 0
    
    for cat, kws in CATEGORY_KEYWORDS.items():
        s = sum(1 for kw in kws if kw in text)
        if s > best_score:
            best_score, best_cat = s, cat
    
    job.category = best_cat
    return job

# ═══════════════════════════════════════════════
# RESUME MATCHING
# ═══════════════════════════════════════════════

def match_resume(job: Job) -> Job:
    """Score how well this job matches your resume (0-100)."""
    text = f"{job.title} {job.description}".lower()
    
    matched = [s for s in MY_RESUME_SKILLS if s.lower() in text]
    strong_matched = [s for s in MY_STRONG_SKILLS if s.lower() in text]

    # Base score: proportion of skills matched (max 50)
    base = int((len(matched) / max(len(MY_RESUME_SKILLS), 1)) * 50)
    
    # Bonus for strong skills (max 40)
    strong_bonus = min(len(strong_matched) * 15, 40)
    
    # Fresher bonus
    fresher_bonus = 15 if any(k in text for k in FRESHER_KEYWORDS) else 0
    
    # Senior penalty
    senior_penalty = 25 if any(k in text for k in ["5 years", "7 years", "10 years", "senior", "lead", "principal"]) else 0

    job.match_score = max(0, min(100, base + strong_bonus + fresher_bonus - senior_penalty))
    job.match_reasons = matched[:5]
    
    return job

# ═══════════════════════════════════════════════
# TELEGRAM ALERTS
# ═══════════════════════════════════════════════

def send_telegram_alert(job: Job):
    """Send a message to Telegram if a high-match job is found."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("  ⚠️  Telegram not configured (skip)")
        return

    message = f"""
🚀 <b>New High-Match Job Alert!</b>

📍 <b>Role:</b> {job.title}
🏢 <b>Company:</b> {job.company}
📍 <b>Location:</b> {job.location}
🏷️ <b>Category:</b> {job.category.upper()}
💰 <b>Salary:</b> {job.salary or 'Not disclosed'}
📄 <b>Match Score:</b> {job.match_score}%
🔗 <b>Skills:</b> {', '.join(job.match_reasons[:3]) or 'N/A'}

🔗 <a href="{job.link}">Apply Here</a>
    """

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        r = requests.post(url, json=payload, timeout=10)
        if r.status_code == 200:
            print(f"  ✅ Alert sent for: {job.title}")
        else:
            print(f"  ⚠️  Telegram API error: {r.status_code}")
    except Exception as e:
        print(f"  ⚠️  Telegram alert failed: {e}")

# ═══════════════════════════════════════════════
# EMAIL ALERTS
# ═══════════════════════════════════════════════

def send_email_alert(jobs: list[Job]):
    """Send email with top job matches."""
    if not EMAIL_SENDER or not EMAIL_PASSWORD or not EMAIL_RECEIVER:
        print("  ⚠️  Email not configured (skip)")
        return
    
    if not jobs:
        print("  ℹ️  No jobs to email")
        return

    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <h2 style="color: #2563eb;">🚀 New Job Alerts for Amit Sharma</h2>
        <p>Found <strong>{len(jobs)}</strong> high-match jobs today.</p>
        
        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
            <tr style="background: #f3f4f6;">
                <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Role</th>
                <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Company</th>
                <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Match</th>
                <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Apply</th>
            </tr>
    """
    
    for job in jobs[:10]:
        color = '#22c55e' if job.match_score >= 80 else '#eab308' if job.match_score >= 50 else '#ef4444'
        html += f"""
            <tr>
                <td style="padding: 10px; border: 1px solid #ddd;">{job.title}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{job.company}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">
                    <span style="background: {color}; color: white; padding: 4px 8px; border-radius: 4px;">
                        {job.match_score}%
                    </span>
                </td>
                <td style="padding: 10px; border: 1px solid #ddd;">
                    <a href="{job.link}" style="color: #2563eb;">Apply →</a>
                </td>
            </tr>
        """
    
    html += """
        </table>
        <p style="color: #6b7280; font-size: 12px;">
            Sent by Amit's Job Agent | Built with Python
        </p>
    </body>
    </html>
    """

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🚀 {len(jobs)} New Job Matches Found"
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER
        msg.attach(MIMEText(html, "html"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        server.quit()

        print(f"  ✅ Email sent to {EMAIL_RECEIVER}")
    except Exception as e:
        print(f"  ⚠️  Email failed: {e}")