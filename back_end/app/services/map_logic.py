import os


def get_files_in_dir(directory):
    file_data = []

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            with open(file_path, "r") as f:
                content = f.read().strip()
                file_data.append({"id": filename, "d": content})

    return file_data
