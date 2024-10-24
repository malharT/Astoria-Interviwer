# Astoria Interviewer

Astoria_Interviewer is a console based AI interviewing application. I takes in the company profile, job description and resume as the text files. You can run the interview against a virtual candidate which is itself an AI agent or you can run it for yourself (Interact using console).

# Steps to run the project:

1. Create a virtual environment with python 3.11.
2. [Install poetry](https://python-poetry.org/docs/#installation.)
3. Open command prompt in the project directory.
4. Run 'poetry install' to install all the python dependencies.
5. Check and edit files company_profile.txt, job_description.txt and resume.txt under data/ if needed.
6. Set the OpenAI api key in openai_client.py
8. Run the main.py file:
    6.1 Run 'python main.py auto' to run interview with the virtual candidate.
    6.2 Run 'python main.py manual' to run interview with yourself.
9. Check the interview log file at /interview_log.json