from sqlmodel import Session, create_engine, select

from .models import Job, SQLModel

DATABASE_URL = "sqlite:///./jobs.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


def init_db():
    SQLModel.metadata.create_all(engine)


def save_jobs(jobs):
    """jobs: list of dicts"""
    saved = []
    with Session(engine) as session:
        for j in jobs:
            # egyszerű deduplikáció: URL vagy (source+remote_id)
            existing = None
            if j.get("remote_id"):
                existing = session.exec(
                    select(Job).where(Job.source == j["source"]).where(Job.remote_id == j["remote_id"])
                ).first()
            if not existing:
                existing = session.exec(select(Job).where(Job.url == j["url"]).limit(1)).first()
            if existing:
                continue
            job = Job(**j)
            session.add(job)
        session.commit()
    return True


def query_recent_jobs(days=7, location=None, keywords=None):
    # Egyszerű lekérdezés a DB-ből (későbbi kiterjesztéshez)
    with Session(engine) as session:
        q = select(Job)
        if location:
            q = q.where(Job.location.contains(location))
        results = session.exec(q).all()
        return [r.dict() for r in results]
