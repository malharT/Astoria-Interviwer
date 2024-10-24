from typing import List


from pydantic import BaseModel


class Objective(BaseModel):
    title: str = None
    description: str
    questions: List[str] = []
    discussions: List[dict] = []

class Interview(BaseModel):
    company_profile: str = None
    job_description: str = None
    resume: str = None
    objectives: List[Objective] = []
    