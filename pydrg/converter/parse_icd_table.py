import re
import json
from datetime import datetime


def expand_code_range(start_code, end_code):
    """
    Expands a range of ICD codes.
    Example: expand_code_range("H02.101", "H02.106")
    Returns: ["H02.101", "H02.102", "H02.103", "H02.104", "H02.105", "H02.106"]
    """
    # Find the common prefix and the numeric suffixes
    common_prefix = ""
    min_len = min(len(start_code), len(end_code))
    for i in range(min_len):
        if start_code[i] == end_code[i]:
            common_prefix += start_code[i]
        else:
            break

    start_suffix_str = start_code[len(common_prefix) :]
    end_suffix_str = end_code[len(common_prefix) :]

    if start_suffix_str.isdigit() and end_suffix_str.isdigit():
        start_suffix = int(start_suffix_str)
        end_suffix = int(end_suffix_str)
        num_digits = len(start_suffix_str)

        return [
            f"{common_prefix}{str(i).zfill(num_digits)}"
            for i in range(start_suffix, end_suffix + 1)
        ]
    else:
        # Fallback for complex cases, just return start and end
        return [start_code, end_code]


def parse_icd_conversion_table(file_path):
    """
    Parses the ICD-10-CM conversion table and returns a list of dictionaries.
    """
    parsed_data = []
    with open(file_path, "r") as f:
        lines = f.readlines()

    # Find the header row to start processing from the next line
    header_index = -1
    for i, line in enumerate(lines):
        if "Current code assignment" in line and "Previous Code(s) Assignment" in line:
            header_index = i
            break

    if header_index == -1:
        raise ValueError("Could not find the header row in the file.")

    for line in lines[header_index + 1 :]:
        line = line.strip()
        if not line:
            continue

        # Split the line into columns based on multiple spaces or a tab
        parts = re.split(r"\s{2,}|\t", line, maxsplit=2)
        if len(parts) < 3:
            continue

        current_code, effective_date_str, prev_codes_str = parts
        current_code = current_code.strip()
        effective_date_str = effective_date_str.strip()
        prev_codes_str = prev_codes_str.strip()

        # Skip rows based on the conditions
        if "none" in prev_codes_str.lower() or "categories" in prev_codes_str.lower():
            continue

        try:
            # If it's a year like '2017'
            year = int(effective_date_str)
            effective_date = f"{year}-10-01"
        except ValueError:
            # If it's a date like '01/01/21'
            try:
                dt_obj = datetime.strptime(effective_date_str, "%m/%d/%y")
                effective_date = dt_obj.strftime("%Y-%m-%d")
            except ValueError:
                # Fallback if the format is unexpected
                effective_date = effective_date_str

        # Clean and parse the "Previous Code(s) Assignment" column
        prev_codes_str = prev_codes_str.replace('"', "").replace(" and ", ", ")

        raw_codes = re.split(r"[;,]", prev_codes_str)
        final_codes = []

        for code in raw_codes:
            code = code.strip()
            if not code:
                continue

            if "-" in code:
                range_parts = code.split("-")
                if len(range_parts) == 2:
                    start_code, end_code = [p.strip() for p in range_parts]
                    # Handle cases where the end code is just a suffix
                    if len(end_code) < len(start_code):
                        end_code = start_code[: -len(end_code)] + end_code
                    final_codes.extend(expand_code_range(start_code, end_code))
                else:
                    final_codes.append(code)  # Not a simple range
            else:
                final_codes.append(code)

        parsed_data.append(
            {
                "current_code": current_code,
                "effective_date": effective_date,
                "previous_codes": final_codes,
            }
        )

    return parsed_data


if __name__ == "__main__":
    file_path = "//path/to/icd_conversion_table.txt"
    parsed_data = parse_icd_conversion_table(file_path)
    with open("parsed_icd_conversion_table.json", "w") as out_file:
        for record in parsed_data:
            json.dump(record, out_file)
            out_file.write("\n")
