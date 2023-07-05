import os
import openai
import sys
import json
import tiktoken
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())
openai.api_key = os.environ['OPENAI_API_KEY_NIKI']

MODEL = "gpt-3.5-turbo"
TEMPERATURE = 0.2
MAX_TOKENS = 600

delimiter = "####"


def get_completion_from_messages(messages,
                                 model=MODEL,
                                 temperature=TEMPERATURE,
                                 max_tokens=MAX_TOKENS):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    print(response)
    return response.choices[0].message["content"]


class Explanator():
    """
    This class is used for explaining product comparison results to users.
    """

    def __init__(self, comparison_or_kisusscore_result="", knowledge_base_type="empty", user_preferences=""):
        """
        Initialize the Explanator object.
        """
        self.comparison_or_kisusscore_result = comparison_or_kisusscore_result
        self.knowledge_base_type = knowledge_base_type
        self.user_preferences = user_preferences

    def get_answer(self, user_question):
        """
        This function provides semantic search using embeddings.
        Search the chunks and find the k most similar chunks based on the query.
        """

        return
