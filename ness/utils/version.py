import ness
import os

def get_version() -> str:

    ness_directory = os.path.dirname(ness.__file__)
    version_file_path = os.path.join(ness_directory, 'version.txt')
    with open(version_file_path) as reader:
        return reader.read()
