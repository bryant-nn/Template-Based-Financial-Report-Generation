from collections import OrderedDict

prompt_dict = OrderedDict([

("generation", """You are a senior climate analyst. Based on the provided context (climate report chunks),\
 try to answer the question and the numerical value as precise as possible based on the provided context.\
 Ensure clarity and CONCISENESS in the response.
 
Climate Context:
#CONTEXT#

Question:
#QUESTION#

Answer: """),

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

("reflection", """Review the following climate report question and answer:
###
Question:
#QUESTION#

Answer:
#ANSWER#
###
Your job is to analyze the climate report answer and identify missing elements based on the following criteria:"
1. Ensure the inclusion of specific numerical data such as temperature changes (with ranges), greenhouse gas emissions (historical and current values), and sea-level rise rates.
2. Assess the impact of human activities on climate change with specific quantitative estimates, such as contributions to global warming, CO₂ concentration increases, and historical emission trends.
3. Evaluate the wide-ranging impacts of climate change, including effects on ecosystems (species loss, ocean acidification), human health (heatwaves, diseases), food and water security, economic stability, and social inequalities.
4. Discuss future climate projections across different emission scenarios (e.g., low-emission vs. high-emission pathways), including projected temperature increases, sea-level rise, and potential tipping points.
5. Assess adaptation and mitigation strategies, including policy responses, technological advancements (e.g., carbon capture, renewable energy), and social initiatives aimed at reducing vulnerability.

If any improvements are needed, provide a short suggestion for how to improve it."""
     
),

("re_generation", """You are a senior climate analyst. Based on the provided context (climate report chunks),\
try to answer the question and the numerical value as precise as possible based on the provided context.\
Ensure clarity and CONCISENESS in the response.
        
Climate Context:
#CONTEXT#

The previous climate report answer needs improvement based on the following suggestion
###
Question:
#QUESTION#

Answer:
#ANSWER#

###
Feedback:
#FEEDBACK#
###
Please follow the feedback to improve the climate report answer.""")

])