from collections import OrderedDict

chat_evaluate_prompt_dict = OrderedDict([
    ("Financial takeaways", """Evaluate the provided summary on the dimension of 'Financial Takeaways.' To what extent does the summary contain key financial figures or numerical statistics, such as revenue, profit, margins, growth percentages, or other performance indicators? Assign a score from 1 to 5, where:
1 = No financial figures or statistics present.
2 = Minimal numerical information, with vague or limited relevance.
3 = Some financial figures present, though not comprehensive or detailed.
4 = Clear and relevant financial figures included, providing meaningful insights.
5 = Extensive, detailed, and highly relevant financial figures that strongly reflect the company's performance."""),
    ("Financial context", """Evaluate the provided summary on the dimension of 'Financial Context.' To what extent does the summary provide contextual information that helps to better understand the company's financial performance, such as references to previous quarters, market conditions, or other relevant factors? Assign a score from 1 to 5, where:
1 = No contextual information provided.
2 = Minimal context, with limited relevance or clarity.
3 = Some contextual information present, though lacking depth or clarity.
4 = Clear and relevant contextual details that enhance understanding.
5 = Extensive, detailed, and highly relevant context that provides a comprehensive understanding of the company's financial performance."""),
    ("Reasoning correctness", """Evaluate the provided summary on the dimension of 'Reasoning Correctness.' To what extent does the summary accurately explain or provide logical reasoning behind the company's financial performance, aligning with the information in the financial report? Assign a score from 1 to 5, where:
1 = No reasoning or completely inaccurate explanation.
2 = Minimal or weak reasoning with questionable accuracy.
3 = Some reasoning present, but lacking clarity or partial accuracy.
4 = Clear and mostly accurate reasoning that aligns well with the financial report.
5 = Highly accurate, detailed, and logically consistent reasoning that fully reflects the financial report."""),
    ("Management expectation", """Evaluate the provided summary on the dimension of 'Management Expectation.' To what extent does the summary mention future goals, forecasts, or strategic plans for the next quarter or beyond, based on the financial report? Assign a score from 1 to 5, where:
1 = No mention of future goals or plans.
2 = Minimal reference to future expectations, with limited detail.
3 = Some mention of future goals, though lacking specificity or clarity.
4 = Clear, relevant, and informative references to future goals and strategies.
5 = Detailed, well-defined, and highly relevant expectations that strongly reflect the company's future direction.""")
])  