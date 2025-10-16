import asyncio
from typing import List, Optional

from app.db import init_db, query_recent_jobs, save_jobs
from app.scrapers import fetch_from_greenhouse, fetch_from_lever, fetch_from_profession, fetch_from_smartrecruiters
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Job Aggregator")


class SearchRequest(BaseModel):
    keywords: Optional[str] = None
    location: Optional[str] = None
    days: int = 7


@app.on_event("startup")
async def startup_event():
    init_db()


@app.post("/search")
async def search_jobs(req: SearchRequest):
    # Egyszerű orchestration: pár platform párhuzamosan
    tasks = [
        fetch_from_lever(req.keywords, req.location, req.days),
        fetch_from_greenhouse(req.keywords, req.location, req.days),
        fetch_from_smartrecruiters(req.keywords, req.location, req.days),
        fetch_from_profession(req.keywords, req.location, req.days),
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    all_jobs = []
    for r in results:
        if isinstance(r, Exception):
            # hibakezelés: logolás helyett most csak folytatjuk
            continue
        all_jobs.extend(r)

    # mentés az adatbázisba (duplikációt figyelembe véve)
    saved = save_jobs(all_jobs)

    # visszaadjuk a friss találatokat (nem a teljes DB-t)
    return {"count": len(all_jobs), "jobs": all_jobs}
