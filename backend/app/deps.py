from fastapi import Depends, HTTPException, status
from sqlmodel import Session

from .db import engine
from .models import Job


def get_session():
    with Session(engine) as session:
        yield session


def paginate(items, page: int = 1, per_page: int = 20):
    start = (page - 1) * per_page
    end = start + per_page
    return items[start:end]


def filter_jobs(session: Session, keywords: str = None, location: str = None):
    query = session.query(Job)
    if keywords:
        query = query.filter(Job.title.ilike(f"%{keywords}%") | Job.description.ilike(f"%{keywords}%"))
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    return query.all()
