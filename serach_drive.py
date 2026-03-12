import os
from google.colab import drive
drive.mount('/content/drive')

def find_file_path(filename, search_directory='/content/drive/MyDrive'):
    """Recursively searches for a file by name within a specified directory.
    
    Args:
        filename (str): The name of the file to search for.
        search_directory (str): The starting directory for the search.

    Returns:
        str or None: The full path to the file if found, otherwise None.
    """
    for root, dirs, files in os.walk(search_directory):
        if filename in files:
            return os.path.join(root, filename)
    return None

file_to_find = str(input("Enter the name of your dataset file: "))
found_path = find_file_path(file_to_find)

if found_path:
    print(f"Found your dataset at: {found_path}")
    # You can now copy this path and use it in your pd.read_csv command
else:
    print(f"File '{file_to_find}' not found in your Google Drive.")
    print("Please ensure the file name is correct and it's within '/content/drive/MyDrive'.")