import openai
from openai import Completion

class GPTWrapper:

    def __init__(self):
        self.model = "gpt-3.5-turbo-instruct"
        openai.api_key = "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"

    def complete(self, prompt
                 ):
        return Completion.create(
            model=self.model,
            prompt=prompt,
            stop = ["."]
        )