import sys


from objectives_generator import generate_objectives
from questions_generator import generate_objective_wise_questions
from interviewer import Interviewer
from candidate import Candidate
from data_models import Interview

# Solution:
# A job interview is conducted to understand the candidate's
# alignment with the position and the company.
# The criteria for alignment should be same for
# all the candidates.

# 1) Hence, the first step of planning an interview is to
# identify the specific interviewing objectives independent
# of the candidate.

# 2) In the second step we shall align the objectives and
# with the candidate's experience to develop the questions.
# These questions would investigate the candidate
# for the pre-defined objective instead of just chatting around.

# 3) Lastly, these questions only act as a rough script
# the interviewer might need to add or drop the questions
# based on the candidate's answer's. The act of interview
# should be more of a discussion where interviewer guides
# the candidate to best understand their experience.

# Model choice:
# This solution is built using GPT-4o especially for
# its 'Tool Calling' (previously know as 'function calling')
# and 'Structured Output' (successor of 'JSON mode') features.

# *The 'Tool Calling' feature eases ingesting information
# into the model.

# *The Structured Output feature takes away
# the efforts for parsing the model outputs.

##############################INTPUTS#########################################
#Fetching the company profile
with open('data/company_profile.txt') as f:
    cp = f.read()

#Fetching the job description
with open('data/job_description.txt') as f:
    jd = f.read()

#Fetching the resume of the candidate
with open('data/resume.txt') as f:
    resume = f.read()


###########################INTERVIEW SCRIPT PREP###############################
#Generate objectives for the interview
interview: Interview = generate_objectives(
    company_profile=cp,
    job_description=jd)

#Generate questions for each objective
generate_objective_wise_questions(
    interview=interview,
    resume=resume)


###########################VIRTUAL CANDIDATE##################################
# We can engineer this prompt to imitate a wide range of candidate behaviors.
# This will help us easily test our interviewing system.
candidate_prompt = "You are interviewing for a job in a company." +\
                     " Give very short answers for all the questions." +\
                     "You are given your resume, job description, and company description.\n" +\
                     "Resume: " + resume + "\n" +\
                     "Job Description: "+ jd + "\n" +\
                     "Company Profile: " + cp

candidate = Candidate(candidate_prompt)


#########################CANDIDATE TYPE SELECTION#############################
candidate_type = sys.argv[1] if len(sys.argv) > 1 else 'auto'


############################VIRTUAL INTERVIEWER###############################
interviewer = Interviewer(interview)


################################INTERVIEW#####################################
while not interviewer.confirm_interview_end:
    message = interviewer.generate_message()
    if message:
        print("Interviewer:")
        print(message)
        print("Candidate:")
        if candidate_type == 'auto':
            candidate_response = candidate.get_response(message)
            print(candidate_response)
        else:
            candidate_response = input()
        print()
        interviewer.add_response(candidate_response)
        interviewer.save_to_objective()

with open('interview_log.json', 'w') as interview_log:
    interview_log.write(interview.model_dump_json(indent=4))
