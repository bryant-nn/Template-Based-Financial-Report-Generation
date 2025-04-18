import json
import re


def convert_to_json(input_string, output_path, report_template_dict):
    """
    Parses a structured text string, normalizes it, and converts it to JSON format.
    
    Args:
        input_string (str): The input string containing sub-sections and content.
        output_path (str): The file path to save the output JSON.
    
    Returns:
        None
    Raises:
        ValueError: If a sub-section is missing or does not match predefined keys.
    """
    report_template_dic = {}
    for i, (key, sub_sections) in enumerate(report_template_dict.items()):
        for j, sub_section in enumerate(sub_sections):
            report_template_dic[f"sub section {i+1}.{j+1}"] = sub_section
    
    # Use regex to find all sub-sections and their content
    sections = re.findall(r"sub section (\d+\.\d+): (.*?)(?=sub section \d+\.\d+:|$)", 
                      input_string, re.DOTALL | re.IGNORECASE)

    if len(sections) > len(report_template_dic.keys()):
        print(f"Error: {len(sections)} sections found, but only {len(report_template_dic.keys())} sections are defined in the template.")
        raise ValueError(f"Error")
    
    # Check if the number of sections matches the number of keys in report_template_dic
    elif len(sections) < len(report_template_dic.keys()):
        result = []
        j = 0
        for i, string_key in enumerate(report_template_dic.keys()):
            if j >= len(sections):
                if i <= len(report_template_dic.keys()) - 1:
                    result.append({string_key: "Missing"})
                    continue
                    
            key = f"sub section {sections[j][0].strip()}"
            if key != string_key:
                result.append({string_key: "Missing"})
                continue
            else:
                content = sections[j][1].strip()
                result.append({string_key: content})
                j += 1
    else:
        result = []
        for section_id, content in sections:
            key = f"sub section {section_id.strip()}"
            value = content.strip() 
            result.append({key: value})
        
    # Write the JSON object to the specified path
    with open(output_path, 'w', encoding='utf-8') as json_file:
        json.dump(result, json_file, indent=4, ensure_ascii=False)


