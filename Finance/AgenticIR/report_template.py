from collections import OrderedDict

report_template_dict = OrderedDict([
("P&L (profit and loss statement) highlights result for #TIME#", 
     ["Revenue results, QoQ changes, YoY changes with reasons, revenue results  v.s. guidance from #LAST_QUARTER# with reasons",
      "wafer sales and the breakdown to wafer quanty and ASP for #TIME#",]),

("Segment or Platform highlights for #TIME#", 
    ["sales by segment or platforms, their respective margin levels, and their respective management comments",
    "sales guidance, forecast, or trend by segment #NEXT_QUARTER# or full year"]),
])