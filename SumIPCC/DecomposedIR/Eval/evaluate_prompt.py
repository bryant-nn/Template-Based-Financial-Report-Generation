from collections import OrderedDict

evaluate_prompt_dict = OrderedDict([
    ("Climate Statistics & Trends", "The following sentence is extracted from the summary of the climate report. Does it include key numerical statistics or trends? for example,  global temperature, greenhouse gas emissions, sea level rise, or other climate indicators based on the given climate report?"),
    ("Human Influence on Climate Change", "The following sentence is extracted from the summary of the climate report. Does it attribute climate change to human activities, such as greenhouse gas emissions and land-use changes with the given climate report?"),
    ("Impacts on Ecosystems and Human Systems", "The following sentence is extracted from the summary of the climate report. Does it describe the impacts of climate change on ecosystems, human health, economies, or vulnerable communities accordance with the given climate report?"),
    ("Future Projections & Scenarios", "The following sentence is extracted from the summary of the climate report. Does it include projections of future climate risks, such as extreme weather events or long-term environmental changes with the given climate report?")
])  