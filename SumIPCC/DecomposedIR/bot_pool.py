from langchain_openai import ChatOpenAI 
import openai
import os
import torch
from bot_pool_prompt import prompt_dict
from dotenv import load_dotenv
load_dotenv()

def load_llm(model_name):

    if model_name == "gpt-4o-mini":
        openai.api_key = os.getenv("OPENAI_API_KEY")

        openai.api_base = "https://api.openai.com"

        llm = ChatOpenAI(model_name=model_name, openai_api_key=openai.api_key, temperature=0.5)

        return llm


def generate_result_with_retrieved_chunk(query, relevant_chunks):
    llm = load_llm("gpt-4o-mini")

    generation_prompt = prompt_dict["generation"].replace("#QUESTION#", query).replace("#CONTEXT#", relevant_chunks)

    response = llm.invoke(generation_prompt)

    return response

def update_numerber_with_statement_json(query, initial_answer, statement_json):
    llm = load_llm("gpt-4o-mini")

    generation_prompt = prompt_dict["update number"].replace("#QUESTION#", query).replace("#FINANCIAL_STATEMENT_JSON#", statement_json).replace("#INITIAL ANSWER#", initial_answer).replace("#STATEMENT JSON#", statement_json)

    response = llm.invoke(generation_prompt)

    return response

def summarize(query_and_answer, key_aspect):
    llm = load_llm("gpt-4o-mini")

    generation_prompt = prompt_dict["summary"].replace("#QUESTIONS_AND_ANSWERS#", query_and_answer).replace("#KEY_ASPECT#", key_aspect)

    response = llm.invoke(generation_prompt)

    return response

def reflection(question, answer):
    llm = load_llm("gpt-4o-mini")
    generation_prompt = prompt_dict["reflection"].replace("QUESTION", question).replace("ANSWER", answer)

    response = llm.invoke(generation_prompt)

    return response

def re_generate_result_with_retrieved_chunk(query, answer, relevant_chunks, feedback):
    llm = load_llm("gpt-4o-mini")

    generation_prompt = prompt_dict["re_generation"].replace("#QUESTION#", query).replace("#CONTEXT#", relevant_chunks).replace("#ANSWER#", answer).replace("FEEDBACK#", feedback)

    response = llm.invoke(generation_prompt)

    return response