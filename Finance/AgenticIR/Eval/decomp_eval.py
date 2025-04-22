import re
import nltk
from nltk.tokenize import sent_tokenize
from openai import OpenAI
from dotenv import load_dotenv
import os
load_dotenv()
nltk.download("punkt_tab")
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

class DecompEval:
    def __init__(self, model_name=None):
        self.model_name = model_name
    
    @retry(wait=wait_random_exponential(min=3, max=60), stop=stop_after_attempt(6))
    def ask_question_gpt(self, report, sentence, question, response):
        question_template = """Answer the following yes/no question.
        Given the financial report: {report}
        
        The summary of the report is as follow: {response}

        Question:\n{question}? 
        Sentence:\n{sentence}"""

        question_ = question_template.format(report=report, response=response, question=question, sentence=sentence)

        completion = client.chat.completions.create(
                        model=self.model_name,
                        messages=[
                            {"role": "system", "content": "You are a financial analyst."},
                            {
                                "role": "user",
                                "content": question_,
                            }
                        ],
                        temperature=0.1,
                    )
        return completion.choices[0].message.content


    def evaluate(self, report, response, question):
        results = []
        response_ = post_process_markdown(response)
        sentences = sent_tokenize(response_)

        for sentence in sentences:
            if len(sentence) < 10:
                continue
            answer = self.ask_question_gpt(report, sentence, question, response)
            results.append((sentence, answer))
        return results

    def get_final_score(self, results):
        coherent_count = sum(1 for _, answer in results if "yes" in answer.lower())
        if len(results) == 0:
            return 0.0
        return coherent_count / len(results)

def post_process_markdown(text):
    # Remove heading symbols (# and ##, etc.)
    text = re.sub(r'#+\s', '', text)

    # Remove bullet points numbers (1., 2., etc.)
    text = re.sub(r'\d+\.\s', '', text)
    
    # Remove bold asterisks (**)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    
    # Remove currency symbols, percentage signs, and similar formatting
    text = re.sub(r'[\$%]', '', text)
    
    # Remove extra line breaks and blank lines, merge paragraphs
    text = re.sub(r'\n+', '\n', text).strip()
    
    return text


class ChatEval:

    def __init__(self, model_name=None):
        self.model_name = model_name

    @retry(wait=wait_random_exponential(min=3, max=60), stop=stop_after_attempt(6))
    def ask_question_gpt(self, summary, question):
        question_template = """You are a financial analyst, and need to help me to evaluate the summary of the financial report. please return 1 ~ 5 number.

        {question}

        Summary:\n{summary}
        
        Please return the score and its reason.

        Return Format: Number. Reason
        """

        question_ = question_template.format(question=question, summary=summary)

        completion = client.chat.completions.create(
                        model=self.model_name,
                        messages=[
                            {"role": "system", "content": "You are a financial analyst."},
                            {
                                "role": "user",
                                "content": question_,
                            }
                        ],
                        temperature=0.1,
                    )
        return completion.choices[0].message.content
    
    def get_final_score(self, summary, question):
        response = self.ask_question_gpt(summary, question)
        
        if  '1' in response[:10]:
            return 1
        elif '2' in response[:10]:
            return 2
        elif '3' in response[:10]:
            return 3
        elif '4' in response[:10]:
            return 4
        elif '5' in response[:10]:
            return 5
        else:
            print("=== Error Chat Eval ===")
            return 'a'

    


