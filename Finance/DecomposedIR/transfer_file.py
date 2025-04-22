import json
import os

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
    


