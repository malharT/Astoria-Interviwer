from typing import List
import threading

from openai_client import openai_client
from pydantic import BaseModel

from data_models import Interview, Objective


class Questions_temp(BaseModel):
    questions: List[str]


def add_questions(interview: Interview, object_idx: int, prompt: str, model = 'gpt-4o-mini')-> threading.Thread:
    response = openai_client.beta.chat.completions.parse(
            model=model,
            messages=[
                {
                    "role":"user",
                    "content": prompt
                }
            ],
            response_format=Questions_temp)
    
    questions = Questions_temp.model_validate_json(
        response.choices[0].message.content
    )

    for qs in questions.questions:
        interview.objectives[object_idx].questions.append(qs)


def generate_objective_wise_questions(interview: Interview, resume: str):
    interview.resume = resume
    threads = []
    for obj_idx, objective in enumerate(interview.objectives):
        prompt = "We have given a company profile, a job description and a candidates resume," + \
                 "based on the following objective generate two or three interview questions.\n" + \
                 "Company Profile: " + interview.company_profile + "\n" + \
                 "Job Description: " + interview.job_description + "\n" + \
                 "Objective: " + objective.model_dump_json(indent=4) + "\n" + \
                 "Resume: " + resume
        t = threading.Thread(target=add_questions,
                             args=[interview, obj_idx, prompt])
        t.start()
        threads.append(t)
    for t in threads:
        t.join()