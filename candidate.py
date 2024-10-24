
from openai_client import openai_client


class Candidate:
    def __init__(self, prompt, model = 'gpt-4o-mini'):
        self.conversation = [
            {
                'role': 'system',
                'content': prompt
            }
        ]
        self.model = model
    
    def get_response(self, question):
        self.conversation.append({
            'role': 'user',
            'content': question
        })
        response = openai_client.beta.chat.completions.parse(
            model=self.model,
            messages=self.conversation
        )
        answer = response.choices[0].message.content

        self.conversation.append({
            'role': 'assistant',
            'content': answer
        })

        return answer