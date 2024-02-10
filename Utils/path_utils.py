import os

# Check if the file exists, if not, create it
def check_and_create_file(filename):
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            pass


def get_relative_path(relative_path: str, fileName: str):
    # Get the current file path
    current_file_path = os.path.realpath(fileName)
    
    # Get the directory of the current file
    current_directory = os.path.dirname(current_file_path)
    
    # Append the relative path
    new_path = os.path.join(current_directory, relative_path)
    
    return new_path