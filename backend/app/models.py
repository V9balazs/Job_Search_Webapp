from typing import Optional

from sqlmodel import Field, SQLModel


class Job(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    source: str
    remote_id: Optional[str] = None  # az eredeti hirdetés azonosítója
    title: str
    company: Optional[str]
    location: Optional[str]
    url: str
    posted_date: Optional[str]
    description: Optional[str]
