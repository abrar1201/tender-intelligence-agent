# import requests
# import asyncio
# import json
# import os
# from bs4 import BeautifulSoup
# from apscheduler.schedulers.asyncio import AsyncIOScheduler
# from sentence_transformers import SentenceTransformer, util
# from email.mime.text import MIMEText
# import smtplib
# from dotenv import load_dotenv
# FILE_NAME = "tenders.json"

# def load_existing():
#     if not os.path.exists(FILE_NAME):
#         return []

#     try:
#         with open(FILE_NAME, "r", encoding="utf-8") as f:
#             content = f.read().strip()
#             if not content:
#                 return []
#             return json.loads(content)
#     except:
#         return []


# def save_tenders(new_tenders):
#     existing = load_existing()
#     existing_titles = {t["title"] for t in existing}

#     for tender in new_tenders:
#         if tender["title"] not in existing_titles:
#             existing.append(tender)

#     with open(FILE_NAME, "w", encoding="utf-8") as f:
#         json.dump(existing, f, indent=2)


# load_dotenv()

# EMAIL_USER = os.getenv("EMAIL_USER")
# EMAIL_PASS = os.getenv("EMAIL_PASS")

# # ==============================
# # RELEVANCE PROFILE
# # ==============================

# PROFILE = """
# Enterprise software including CRM, ERP, SCM, HCM,
# EAM, digital transformation, enterprise systems.
# """

# model = SentenceTransformer("all-MiniLM-L6-v2")
# profile_embedding = model.encode(PROFILE, convert_to_tensor=True)

# def is_relevant(text):
#     embedding = model.encode(text, convert_to_tensor=True)
#     score = util.cos_sim(profile_embedding, embedding).item()
    
#     print(f"Similarity: {score:.3f} | {text}")  # Debug line
    
#     return score > 0.40   # lowered threshold



# # ==============================
# # EMAIL ALERT
# # ==============================

# def send_email(source, title, deadline, url):
#     body = f"""
# Source: {source}
# Title: {title}
# Deadline: {deadline}
# URL: {url}
# """

#     msg = MIMEText(body)
#     msg["Subject"] = f"🚨 Relevant Tender ({source})"
#     msg["From"] = EMAIL_USER
#     msg["To"] = EMAIL_USER

#     with smtplib.SMTP("smtp.gmail.com", 587) as server:
#         server.starttls()
#         server.login(EMAIL_USER, EMAIL_PASS)
#         server.send_message(msg)


# # ==============================
# # TED (EU)
# # ==============================

# def scrape_ted():
#     print("Checking TED...")
    
#     url = "https://ted.europa.eu/api/notice-search"
    
#     payload = {
#         "query": "software OR ERP OR CRM",
#         "page": 1,
#         "size": 20
#     }

#     try:
#         response = requests.post(url, json=payload, timeout=15)
#         data = response.json()

#         tenders = []

#         for item in data.get("notices", []):
#             tenders.append({
#                 "title": item.get("title", ""),
#                 "deadline": item.get("deadline", ""),
#                 "link": f"https://ted.europa.eu/udl?uri=TED:NOTICE:{item.get('noticeNumber')}"
#             })

#         return tenders

#     except Exception as e:
#         print("TED error:", e)
#         return []


# # ==============================
# # UK CONTRACTS FINDER
# # ==============================

# def scrape_uk():
#     print("Checking UK...")

#     url = "https://www.contractsfinder.service.gov.uk/Search/Results"
#     params = {
#         "keyword": "enterprise OR asset management OR fleet management system OR ERP implementation OR CRM platform OR SaaS solution OR digital transformation programme",
#         "page": 1
#     }

#     headers = {"User-Agent": "Mozilla/5.0"}
#     tenders = []

#     try:
#         response = requests.get(url, params=params, headers=headers, timeout=15)
#         soup = BeautifulSoup(response.text, "html.parser")

#         results = soup.select(".search-result")

#         for r in results:
#             title_tag = r.select_one("h2 a")
#             deadline_tag = r.select_one(".search-result-sub-header")

#             if not title_tag:
#                 continue

#             href = title_tag["href"]

#             if href.startswith("http"):
#                 link = href
#             elif href.startswith("/"):
#                 link = "https://www.contractsfinder.service.gov.uk" + href
#             else:
#                 link = "https://www.contractsfinder.service.gov.uk" + href

#             tenders.append({
#                 "title": title_tag.text.strip(),
#                 "deadline": deadline_tag.text.strip() if deadline_tag else "Unknown",
#                 "link": link
#             })

#         return tenders

#     except Exception as e:
#         print("UK error:", e)
#         return []




# # ==============================
# # AUSTRALIA AUSTENDER
# # ==============================

# def scrape_australia():
#     print("Checking Australia...")
#     tenders = []


#     url = "https://www.tenders.gov.au/api/atm"
    
#     try:
#         response = requests.get(url, timeout=15)
#         if "application/json" in response.headers.get("Content-Type", ""):

#             data = response.json()
#         else:
#             print("Invalid JSON response from Australia API")
#             return []
#         for item in data.get("data", []):
#             tenders.append({
#                 "title": item.get("title", ""),
#                 "deadline": item.get("closeDate", ""),
#                 "link": item.get("url", "")
#             })

#         return tenders

#     except Exception as e:
#         print("Australia error:", e)
#         return []


# # ==============================
# # CANADA
# # ==============================

# def scrape_canada():
#     print("Checking Canada...")

#     url = "https://buyandsell.gc.ca/procurement-data/tenders.json"

#     try:
#         response = requests.get(url, timeout=15)
#         if "application/json" in response.headers.get("Content-Type", ""):
#             data = response.json()
#         else:
#             print("Invalid JSON response from Canada API")
#             return []

#         tenders = []

#         for item in data:
#             tenders.append({
#                 "title": item.get("title", ""),
#                 "deadline": item.get("closingDate", ""),
#                 "link": item.get("url", "")
#             })

#         return tenders

#     except Exception as e:
#         print("Canada error:", e)
#         return []



# # ==============================
# # MAIN AGENT
# # ==============================

# async def run_agent():
#     print("Running Tender Agent...\n")

#     uk = scrape_uk()

#     print("UK scraped:", len(uk))

#     relevant = []

#     for tender in uk:
#         if is_relevant(tender["title"]):
#             relevant.append(tender)
#             print("Relevant:", tender["title"])

#     save_tenders(relevant)

#     print(f"Saved {len(relevant)} relevant tenders.")
#     print("\nCycle complete.\n")






# # ==============================
# # 24/7 SCHEDULER
# # ==============================

# async def main():
#     scheduler = AsyncIOScheduler()
#     scheduler.add_job(run_agent, "interval", minutes=2)  # use minutes for testing
#     scheduler.start()

#     print("🚀 Tender Agent Running 24/7...")
    
#     # Run first cycle immediately
#     await run_agent()

#     # Keep alive forever
#     await asyncio.Event().wait()


# if __name__ == "__main__":
#     asyncio.run(main())
