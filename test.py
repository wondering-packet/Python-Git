import os
import re


def rename_files_to_three_digit_padding(directory="."):
    """
    Renames Python files in the specified directory from 'N-name.py' to 'NNN--name.py'.

    Examples:
    '1-variables.py'       -> '001--variables.py'
    '10-functions.py'      -> '010--functions.py'
    '100-classes.py'       -> '100--classes.py'

    Args:
        directory (str): The directory to scan for files. Defaults to current directory.
    """
    print(f"Scanning directory: {os.path.abspath(directory)}\n")

    # Regex to capture the initial number and the rest of the filename
    # group1: num_str (e.g., '1', '10', '100')
    # group2: rest_of_name (e.g., 'variables.py', 'functions.py')
    filename_pattern = re.compile(r"^(\d+)-(.*\.py)$")

    files_to_rename = []

    for filename in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, filename)) and filename.endswith(".py"):
            match = filename_pattern.match(filename)
            if match:
                num_str, rest_of_name = match.groups()

                # 1. Zero-pad the number to three digits
                num_padded = f"{int(num_str):03d}"

                # 2. Construct the new filename with double hyphen
                new_filename = f"{num_padded}--{rest_of_name}"

                if new_filename != filename:  # Only add if a change is actually proposed
                    files_to_rename.append((filename, new_filename))
            else:
                print(
                    f"Skipping '{filename}': Does not match the expected 'N-name.py' pattern.")

    if not files_to_rename:
        print("No files found matching the pattern that need reformatting.")
        return

    print("Proposed file renames:")
    for old_name, new_name in files_to_rename:
        print(f"  '{old_name}' -> '{new_name}'")

    confirmation = input(
        "\nDo you want to proceed with these renames? (yes/no): ").lower().strip()

    if confirmation == 'yes':
        for old_name, new_name in files_to_rename:
            old_path = os.path.join(directory, old_name)
            new_path = os.path.join(directory, new_name)
            try:
                os.rename(old_path, new_path)
                print(f"Renamed: '{old_name}' to '{new_name}'")
            except OSError as e:
                print(f"Error renaming '{old_name}' to '{new_name}': {e}")
        print("\nFile reformatting complete.")
    else:
        print("File reformatting cancelled.")


if __name__ == "__main__":
    # Run the script from within the directory containing the files, or specify the path:
    # Example: if your files are in a subfolder called 'my_files'
    # rename_files_to_three_digit_padding("my_files")
    rename_files_to_three_digit_padding(
        "Python-Meraki")  # Runs in the current directory
    # rename_files_to_final_format("Python-Meraki")
    # rename_files_to_final_format() # Runs in the current directory
