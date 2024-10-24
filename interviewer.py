

from openai_client import openai_client

from data_models import Interview, Objective

class Interviewer():
    def __init__(self, interview: Interview):
        self.interview: Interview = interview
        self.confirm_interview_end = False
        self.curr_objective_idx = -1

        # Simple prompt that provides the context and directions to use tools.
        self.conversation = [
            {
                'role': 'system',
                'content': "You are an interviewer assistant for a company interviewing a candidate for a job.\n" + \
                            "You are given the company profile, job description and user resume\n" + \
                            "Company Profile: " + interview.company_profile + "\n" + \
                            "Job Description: " + interview.job_description + "\n" + \
                            "Resume: " + interview.resume + "\n" + \
                            "Get objectives with the get_objective.\n tool complete all the objectives.\n" + \
                            "If there are no objectives left finish the interview with finish_interview tool.\n"
            }
        ]

        # Tool descriptions
        self.tools = [
                {
                    "type": "function",
                    "function": {
                        "name": "get_objective",
                        "description": "Gen new objective and a list of questions.",
                        "parameters": {
                            'type': 'object',
                            'properties': {},
                            "additionalProperties": False,
                            'required': []
                        },
                        'strict': True
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "finish_interview",
                        "description": "Notify that the interview finished.",
                        "parameters": {
                            'type': 'object',
                            'properties': {},
                            "additionalProperties": False,
                            'required': []
                        },
                        'strict': True
                    }
                }
            ]

    # Reminder prompt to guide LLM's behavior, more useful for smaller models like GPT-4o-mini.
    # It also mentions if there are more objectives to work on.    
    def dynamic_reminder_prompt(self):
        return "Use these questions to guide your discussion with the candidate about objective." +\
                "Ask one question at a time.\n" +\
                "Only discuss the questions you are provided with. For any queries about the company ask" +\
                "the candidate to contact the recruiter." +\
                "Investigate the candidate with all the questions to asses it better.\n" +\
                "Use tool finish_interview to end the interview." +\
                "Still there are more objectives left do not forget to call get objective after completing this one." \
                if len(self.interview.objectives)-1 > self.curr_objective_idx else \
                "This is the final objective let the candidate know you are ending the interview after completing it."

    def get_objective(self, objective_idx: int):
        if objective_idx < len(self.interview.objectives):
            objective: Objective = self.interview.objectives[objective_idx]
            result = "Objective: " + objective.title + "\n" + \
                    "Description: " + objective.description + "\n" + \
                    "Questions: \n" + '\n'.join(objective.questions)
        else:
            return 'No more objectives.'

        return result

    # Saving the conversation to the interview object.
    def save_to_objective(self):
        self.interview.objectives[self.curr_objective_idx].discussions += self.conversation[-2:]

    # Adding the candidate's response to the context.
    def add_response(self, response):
        self.conversation.append({
            'role': 'user',
            'content': response
        })

    # Main method to generate the interviewer messages.
    def generate_message(self, model='gpt-4o-mini'):
        reply = None
        if not self.confirm_interview_end:
            message_handled = False
            while not message_handled:
                response = openai_client.beta.chat.completions.parse(
                        model=model,
                        messages=self.conversation,
                        tools=self.tools
                )
                if response.choices[0].finish_reason == 'tool_calls':
                    for tool_call in response.choices[0].message.tool_calls:
                        if tool_call.function.name == 'get_objective':
                            self.confirm_interview_end = False
                            self.curr_objective_idx += 1
                            result = self.get_objective(self.curr_objective_idx)
                            function_call_result_message = {
                                "role": "tool",
                                "content": result,
                                "tool_call_id": response.choices[0].message.tool_calls[0].id
                            }
                            system_message = {
                                "role": "system",
                                "content": self.dynamic_reminder_prompt()
                            }
                            self.conversation += [response.choices[0].message,
                                                function_call_result_message,
                                                system_message]
                        elif tool_call.function.name == 'finish_interview':
                            # Confirming the end of interview if it has not covered all the objectives.
                            if self.curr_objective_idx + 1 < len(self.interview.objectives) and not self.confirm_interview_end:
                                self.confirm_interview_end = True
                                system_message = {
                                    "role": "system",
                                    "content":  "Do not end the interview pre-maturely." +\
                                                " If the candidate does not wish to continue call the finish_interview again" +\
                                                " There are remaining objectives, call get_objective to get them."
                                                
                                }
                                self.conversation.append(system_message)
                            else:
                                self.confirm_interview_end = True
                                message_handled = True
                                break

                else:
                    reply = response.choices[0].message.content

                    self.conversation += [
                        {
                            'role': 'assistant',
                            'content': reply
                        }
                    ]
                    message_handled = True
        return reply
