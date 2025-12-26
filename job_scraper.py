import requests
from bs4 import BeautifulSoup
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from collections import Counter
import re

EMAIL_SENDER = "holuwaseuntemiloluwa@gmail.com"
EMAIL_PASSWORD = "${{ secrets.EMAIL_PASSWORD }}"
EMAIL_RECEIVER = "holuwaseuntemiloluwa@gmail.com"

SEARCH_TERMS = [
    "animal health",
    "veterinary",
    "livestock",
    "agriculture",
    "animal care",
    "programme officer"
]

def extract_keywords(text):
    text = re.sub(r"[^a-zA-Z ]", "", text.lower())
    words = text.split()
    stopwords = {"and","the","to","of","in","for","with","on","is"}
    filtered = [w for w in words if w not in stopwords and len(w) > 4]
    common = Counter(filtered).most_common(5)
    return ", ".join([w for w, _ in common])

def get_jobs():
    jobs = []
    url = "https://remoteok.com/remote-agriculture-jobs"
    soup = BeautifulSoup(requests.get(url, headers={"User-Agent":"Mozilla/5.0"}).text, "html.parser")

    for job in soup.select("tr.job"):
        title = job.get("data-position")
        company = job.get("data-company")
        link = job.get("data-url")

        if not title or not company or not link:
            continue

        if not any(term in title.lower() for term in SEARCH_TERMS):
            continue

        jobs.append({
            "Company": company,
            "Role": title,
            "Location": "Remote",
            "Apply Link": "https://remoteok.com" + link,
            "Salary": "₦200,000+ (estimated)",
            "Resume Keywords": extract_keywords(title)
        })

    return jobs

def send_email(jobs):
    if not jobs:
        return

    df = pd.DataFrame(jobs)
    html = df.to_html(index=False)

    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    msg["Subject"] = "Daily Remote Animal Health & Agriculture Jobs"

    msg.attach(MIMEText(f"<h3>Jobs for Today</h3>{html}", "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)

if __name__ == "__main__":
    jobs = get_jobs()
    send_email(jobs)
