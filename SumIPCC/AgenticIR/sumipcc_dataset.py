from collections import defaultdict, OrderedDict
import os
import re
from datasets import load_from_disk

# load dataset
dataset = load_from_disk("../../data/SumIPCC/all_data")

# initialize dictionaries
topic_dict = defaultdict(lambda: defaultdict(list))
paragraphs_by_section = defaultdict(list)
groundtruth_by_id = {} 

# process dataset
groundtruth_list = []
for sample in dataset["test"]:
    section = sample["section_topic"].strip()
    paragraph = sample["paragraph_topic"].strip()
    summary = sample["summary_topic"].strip()
    full_paragraphs = sample["full_paragraphs"]
    groundtruth_summary = sample["summary"].strip()
    identifier = sample["ID"]  # 唯一識別 ID

    groundtruth_list.append(groundtruth_summary)
    topic_dict[section][paragraph].append(summary)

    for para in full_paragraphs:
        if para not in paragraphs_by_section[section]:
            paragraphs_by_section[section].append(para)

    groundtruth_by_id[identifier] = {
        "paragraph": paragraph,
        "summary_topic": summary,
        "groundtruth": groundtruth_summary
    }

# ensure unique summaries
ordered_result = OrderedDict()
for section in sorted(topic_dict.keys()):
    ordered_paragraphs = []
    for paragraph in sorted(topic_dict[section].keys()):
        summaries = sorted(set(topic_dict[section][paragraph]))
        ordered_paragraphs.append((paragraph, summaries))
    ordered_result[section] = ordered_paragraphs

output_dir = "../../data/SumIPCC/process_data/"

# output report_template.py and groundtruth.py
for section in ordered_result.keys():
    safe_filename = re.sub(r'[^a-zA-Z0-9_-]', '_', section)
    report_path = os.path.join(output_dir + safe_filename, "report_template.py")
    groundtruth_path = os.path.join(output_dir + safe_filename, "groundtruth.py")

    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    # write report_template.py
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("from collections import OrderedDict\n\n")
        f.write("ordered_result = OrderedDict([\n")
        for paragraph, summaries in ordered_result[section]:
            f.write(f"    (\"{paragraph}\", {summaries}),\n")
        f.write("])")

    # write groundtruth.py
    with open(groundtruth_path, "w", encoding="utf-8") as f:
        f.write("from collections import OrderedDict\n\n")
        f.write("groundtruth_summary = OrderedDict([\n")
        for paragraph, summaries in ordered_result[section]:
            for summary_topic in summaries:
                # based on the paragraph and summary_topic, find the corresponding groundtruth
                matching_ids = [
                    id for id, data in groundtruth_by_id.items()
                    if data["paragraph"] == paragraph and data["summary_topic"] == summary_topic
                ]
                for identifier in matching_ids:
                    groundtruth = groundtruth_by_id[identifier]["groundtruth"]
                    f.write(f"    ((\"{paragraph}\", \"{summary_topic}\"), \"{groundtruth}\"),\n")
        f.write("])")

# output full_paragraphs
for section, paragraphs in paragraphs_by_section.items():
    safe_filename = re.sub(r'[^a-zA-Z0-9_-]', '_', section)
    paragraph_path = os.path.join(output_dir + safe_filename, "full_paragraphs.txt")

    os.makedirs(os.path.dirname(paragraph_path), exist_ok=True)

    with open(paragraph_path, "w", encoding="utf-8") as f:
        f.write("\n".join(paragraphs))
