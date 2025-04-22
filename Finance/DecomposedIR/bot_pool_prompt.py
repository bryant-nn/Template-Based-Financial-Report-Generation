from collections import OrderedDict

prompt_dict = OrderedDict([

("generation", """You are a senior financial analyst. Based on the provided context (earnings call transcript) and financial statement JSON,\
 try to answer the question and the numerical value as precise as possible based on the provided context.\
 Ensure clarity and CONCISENESS in the response.
 
Transcript Relevant Context:
#CONTEXT#

Financial Statement JSON:
#FINANCIAL_STATEMENT_JSON#

Question:
#QUESTION#

Answer: """),

 ("update number", """You are a senior financial analyst. Your task is to verify and, if necessary, correct the numerical values in the provided initial answer by cross-referencing the financial statement JSON. Focus on identifying and replacing any inaccurate numbers with the correct values from the JSON and to answer the question. Do not alter the reasoning or structure of the initial answer unless updating the numerical values requires minor adjustments for clarity. If the initial answer is already accurate, return it unchanged.

Financial Statement JSON:
#FINANCIAL_STATEMENT_JSON#

Initial Answer:
#INITIAL_ANSWER#

Question:
#QUESTION#

Answer:"""),

("summary", """I will provide several questions along with their corresponding answers and the reasoning behind those answers, as well as the key aspect to summarize.\
Please summarize the answers into a single cohesive response focused on this aspect, and consolidate the reasoning into a concise explanation.\
Ensure that all numerical data is accurately preserved and aligned with the key aspect. Do not include any external or speculative information.\
The final summarized response and explanation must be logically consistent, focused on the key aspect, and aligned with the provided content.

 You must give as short an answer as possible.
 
 Questions and Answers:
 #QUESTIONS_AND_ANSWERS#

 Key Aspect to Summarize:
 #KEY_ASPECT#
 """),


("reflection", """Review the following financial report question and answer:
###
Question:
#QUESTION#

Answer:
#ANSWER#
###
Your job is to analyze the financial report answer and identify missing elements based on the following criteria:"
1. Provide key financial details or numbers (e.g., revenue, profit, earnings)."
2. Provide context for the company's financial performance.
3. Provide reasoning or explanations for trends or changes.
4. Mention expectations or guidances for future performance.

If any improvements are needed, provide a short suggestion for how to improve it."""

),

("re_generation", """You are a senior financial analyst. Based on the provided context (earnings call transcript) and financial statement JSON,\
try to answer the question and the numerical value as precise as possible based on the provided context.\
Ensure clarity and CONCISENESS in the response.

Transcript Relevant Context:
#CONTEXT#

Financial Statement JSON:
#FINANCIAL_STATEMENT_JSON#

###
Question:
#QUESTION#

Answer:
#ANSWER#

###
The previous financial report answer needs improvement based on the following suggestion

Feedback:
#FEEDBACK#
###
Please follow the feedback to improve the financial report answer.""")

])