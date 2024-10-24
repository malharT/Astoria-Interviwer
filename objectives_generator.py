from typing import List

from openai_client import openai_client
from pydantic import BaseModel

from data_models import Interview, Objective


class Objective_Temp(BaseModel):
    title: str
    description: str

class Objectives(BaseModel):
    objectives: List[Objective_Temp]


def generate_objectives(company_profile: str, job_description: str, model = 'gpt-4o-mini') -> Interview:

    prompt = "Given the company profile, and the job description" + \
             " generate a few but concise objectives to interview and assess the candidate.\n" + \
             "Company Profile: " + company_profile + "\n" + \
             "Job Description: " + job_description + "\n" + \
             "First objective to know candidate's experience beyond the resume."
    response = openai_client.beta.chat.completions.parse(
            model=model,
            messages=[
                {
                    "role":"user",
                    "content": prompt
                }
            ],
            response_format=Objectives
    )
    objectives = Objectives.model_validate_json(
        response.choices[0].message.content
    )
    new_objectives = []
    for obj in objectives.objectives:
        new_objectives.append(Objective(
            title=obj.title,
            description=obj.description))
    
    return Interview(objectives=new_objectives,
                     company_profile=company_profile,
                     job_description=job_description)