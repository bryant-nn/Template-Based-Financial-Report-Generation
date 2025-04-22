from collections import OrderedDict

evaluate_prompt_dict = OrderedDict([
    ("Financial takeaways", "The following sentence is extracted from the summary of the financial report. Does it contain key financial figures or numerical statistics, such as revenue, profit, margins, or growth percentages, etc., that reflect the company's performance for this quarter based on the given financial report?"),
    ("Financial context", "The following sentence is extracted from the summary of the financial report. Does it provide contextual information that helps to better understand the company's current financial performance, such as references to previous quarters, market conditions, or other relevant factors based on the given financial report?"),
    ("Reasoning correctness", "The following sentence is extracted from the summary of the financial report. Does it accurately explain or provide logical reasoning behind the company's financial performance this quarter, aligning with the information provided in the given financial report?"),
    ("Management expectation", "The following sentence is extracted from the summary of the financial report. Does it mention any future goals, forecasts, or strategic plans for the next quarter or beyond based on the given financial report?")
])  