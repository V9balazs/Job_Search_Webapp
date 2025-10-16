import asyncio
import datetime

import httpx
from bs4 import BeautifulSoup

ONE_WEEK = datetime.timedelta(days=7)


async def fetch_from_lever(keywords, location, days=7):
    companies = ["bitrise", "prezi", "seon"]
    out = []
    async with httpx.AsyncClient(timeout=20) as client:
        for c in companies:
            url = f"https://api.lever.co/v0/postings/{c}?limit=50"
            try:
                r = await client.get(url)
                r.raise_for_status()
                data = r.json()
            except Exception:
                continue

            for job in data:
                created = job.get("createdAt", "")
                if created:
                    try:
                        dobj = datetime.datetime.fromisoformat(created.split("T")[0])
                        if datetime.datetime.utcnow() - dobj > datetime.timedelta(days=days):
                            continue
                    except Exception:
                        pass

                locs = job.get("categories", {}).get("location", "")
                if location and location.lower() not in str(locs).lower():
                    continue
                text = job.get("text", "") + job.get("description", "")
                if keywords and keywords.lower() not in text.lower():
                    continue

                out.append(
                    {
                        "source": "lever",
                        "remote_id": job.get("id"),
                        "title": job.get("text"),
                        "company": c,
                        "location": locs,
                        "url": job.get("hostedUrl") or job.get("applyUrl"),
                        "posted_date": created,
                        "description": job.get("description"),
                    }
                )
    return out


async def fetch_from_greenhouse(keywords, location, days=7):
    companies = ["shapr3d", "rapidminer"]
    out = []
    async with httpx.AsyncClient(timeout=20) as client:
        for c in companies:
            url = f"https://boards.greenhouse.io/{c}/jobs"
            try:
                r = await client.get(url)
                r.raise_for_status()
            except Exception:
                continue

            soup = BeautifulSoup(r.text, "html.parser")
            for job_elem in soup.select(".opening"):
                title = job_elem.text.strip()

                link = job_elem.find("a")
                href = "https://boards.greenhouse.io" + link["href"] if link else None
                if location and location.lower() not in title.lower():
                    continue
                if keywords and keywords.lower() not in title.lower():
                    continue

                out.append(
                    {
                        "source": "greenhouse",
                        "remote_id": href,
                        "title": title,
                        "company": c,
                        "location": location,
                        "url": href,
                        "posted_date": None,
                        "description": None,
                    }
                )
    return out


async def fetch_from_profession(keywords, location, days=7):
    out = []
    async with httpx.AsyncClient(timeout=20) as client:
        q = keywords or ""
        loc = location or "budapest"
        url = f"https://www.profession.hu/allasok/{q}/{loc}"
        try:
            r = await client.get(url)
            r.raise_for_status()
        except Exception:
            return out

        soup = BeautifulSoup(r.text, "html.parser")
        for item in soup.select(".job-row"):
            title_el = item.select_one(".job-title")
            if not title_el:
                continue
            href = title_el.find("a")["href"]
            posted_el = item.select_one(".job-date")
            posted = posted_el.text.strip() if posted_el else None

            out.append(
                {
                    "source": "profession",
                    "remote_id": href,
                    "title": title_el.text.strip(),
                    "company": None,
                    "location": loc,
                    "url": "https://www.profession.hu" + href,
                    "posted_date": posted,
                    "description": None,
                }
            )
    return out


async def fetch_from_smartrecruiters(keywords, location, days=7):
    companies = ["otpbank", "bosch"]
    out = []
    async with httpx.AsyncClient(timeout=20) as client:
        for c in companies:
            url = f"https://api.smartrecruiters.com/v1/companies/{c}/postings"
            try:
                r = await client.get(url)
                r.raise_for_status()
                data = r.json()
            except Exception:
                continue

            for job in data:
                locs = ", ".join([l.get("name", "") for l in job.get("locations", [])])
                posted = job.get("creationDate")
                if posted:
                    try:
                        dobj = datetime.datetime.fromisoformat(posted.replace("Z", "+00:00"))
                        if datetime.datetime.utcnow() - dobj > datetime.timedelta(days=days):
                            continue
                    except Exception:
                        pass

                if location and location.lower() not in locs.lower():
                    continue
                if keywords and keywords.lower() not in (job.get("name", "") + job.get("description", "")).lower():
                    continue

                out.append(
                    {
                        "source": "smartrecruiters",
                        "remote_id": job.get("id"),
                        "title": job.get("name"),
                        "company": c,
                        "location": locs,
                        "url": job.get("applyUrl") or job.get("shortenedUrl"),
                        "posted_date": posted,
                        "description": job.get("description"),
                    }
                )
    return out


async def fetch_from_workday(keywords, location, days=7):
    companies = ["telekom", "ibm", "eon"]  # Példa cégek Workday rendszerrel
    out = []
    async with httpx.AsyncClient(timeout=30) as client:
        for c in companies:
            base_url = f"https://{c}.wd3.myworkdayjobs.com/wday/cxs/{c}/careers/jobs"
            params = {"from": 0, "to": 50}
            try:
                r = await client.get(base_url, params=params)
                r.raise_for_status()
                data = r.json().get("jobPostings", [])
            except Exception:
                continue

            for job in data:
                title = job.get("title", "")
                posted = job.get("postedDate")
                if posted:
                    try:
                        dobj = datetime.datetime.fromisoformat(posted.replace("Z", "+00:00"))
                        if datetime.datetime.utcnow() - dobj > datetime.timedelta(days=days):
                            continue
                    except Exception:
                        pass

                locs = ", ".join([l.get("descriptor", "") for l in job.get("locations", [])])
                if location and location.lower() not in locs.lower():
                    continue
                if keywords and keywords.lower() not in title.lower():
                    continue

                url = f"https://{c}.wd3.myworkdayjobs.com/en-US/careers{job.get('externalPath')}"
                out.append(
                    {
                        "source": "workday",
                        "remote_id": job.get("externalPath"),
                        "title": title,
                        "company": c,
                        "location": locs,
                        "url": url,
                        "posted_date": posted,
                        "description": job.get("externalPath"),
                    }
                )
    return out


async def fetch_from_recruitee(keywords, location, days=7):
    companies = ["bitninja", "emarsys", "codecool"]
    out = []
    async with httpx.AsyncClient(timeout=20) as client:
        for c in companies:
            url = f"https://{c}.recruitee.com/api/offers/"
            try:
                r = await client.get(url)
                r.raise_for_status()
                data = r.json().get("offers", [])
            except Exception:
                continue

            for job in data:
                posted = job.get("created_at")
                if posted:
                    try:
                        dobj = datetime.datetime.fromisoformat(posted.replace("Z", "+00:00"))
                        if datetime.datetime.utcnow() - dobj > datetime.timedelta(days=days):
                            continue
                    except Exception:
                        pass

                loc = job.get("location") or ""
                if location and location.lower() not in loc.lower():
                    continue
                title = job.get("title", "")
                if keywords and keywords.lower() not in title.lower():
                    continue

                out.append(
                    {
                        "source": "recruitee",
                        "remote_id": job.get("slug"),
                        "title": title,
                        "company": c,
                        "location": loc,
                        "url": job.get("careers_url"),
                        "posted_date": posted,
                        "description": job.get("description"),
                    }
                )
    return out


async def fetch_all_sources(keywords, location, days=7):
    from app.scrapers import fetch_from_greenhouse, fetch_from_lever, fetch_from_profession, fetch_from_smartrecruiters

    tasks = [
        fetch_from_lever(keywords, location, days),
        fetch_from_greenhouse(keywords, location, days),
        fetch_from_smartrecruiters(keywords, location, days),
        fetch_from_profession(keywords, location, days),
        fetch_from_workday(keywords, location, days),
        fetch_from_recruitee(keywords, location, days),
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)
    jobs = []
    for r in results:
        if isinstance(r, Exception):
            continue
        jobs.extend(r)
    return jobs
