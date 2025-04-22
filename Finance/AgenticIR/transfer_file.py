import json
import os
import re


def export_json_of_time(time, filenames):
    all_data = ""
    for filename in filenames:
        with open(f'{filename}') as f:
            data = json.load(f)

            for i in range(len(data['report'])):
                if data['report'][i]['calendarYear'] == time['calendarYear'] and data['report'][i]['period'] == time['period']:
                    all_data += json.dumps(data['report'][i])
                    break
    return all_data

def get_previous_and_next_quarter(current_quarter):
    """
    # Example
    previous, next_ = get_previous_and_next_quarter("2024 Q2")
    print("Previous:", previous)  # Previous: 2024 Q1
    print("Next:", next_)      # Next: 2024 Q3
    """
    year, quarter = current_quarter.split()
    year = int(year)
    quarter = int(quarter[1])
    
    # previous quarter
    if quarter == 1:
        prev_quarter = f"{year - 1} Q4"
    else:
        prev_quarter = f"{year} Q{quarter - 1}"
    
    # next quarter
    if quarter == 4:
        next_quarter = f"{year + 1} Q1"
    else:
        next_quarter = f"{year} Q{quarter + 1}"
    
    return prev_quarter, next_quarter

def find_files_with_company(path, keyword):
    """
    Finds all files in the specified directory that start with a given keyword.

    Parameters:
    path (str): Directory path
    keyword (str): Company to match file names

    Returns:
    list: A list of file names that start with the given keyword
    """
    try:
        # Ensure the directory exists
        if not os.path.isdir(path):
            raise ValueError("file path not exists")

        # Traverse the directory and find files that match the criteria
        files = [f for f in os.listdir(path) if f.startswith(keyword) and os.path.isfile(os.path.join(path, f))]
        return files

    except Exception as e:
        print(f"Error: {e}")
        return []


def convert_to_json(input_string, output_path):
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
    section_to_string = {
        'sub section 1.1': 'YOUR SUBSECTION',
        'sub section 1.2': 'YOUR SUBSECTION',
        'sub section 2.1': 'YOUR SUBSECTION',
        'sub section 2.2': 'YOUR SUBSECTION',
    }
    
    # Use regex to find all sub-sections and their content
    sections = re.findall(r"sub section (\d+\.\d+): (.*?)(?=sub section \d+\.\d+:|$)", 
                      input_string, re.DOTALL | re.IGNORECASE)

    if len(sections) > len(section_to_string.keys()):
        print('Error')
        raise ValueError(f"Error")
    
    # Check if the number of sections matches the number of keys in section_to_string
    elif len(sections) < len(section_to_string.keys()):
        result = []
        j = 0
        for i, string_key in enumerate(section_to_string.keys()):
            if j >= len(sections):
                if i <= len(section_to_string.keys()) - 1:
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



