from asammdf import MDF
from pathlib import Path
import logging
from datetime import datetime


# Recursive function to collect all MF4 from the directory and subdirectories
def collectMF4s(current_folder: str):
    current_folder = Path(current_folder)

    mf4_files = list(filter(lambda file: file.suffix == ".MF4", current_folder.iterdir()))
    subdirectories = [file for file in current_folder.iterdir() if file.is_dir()]

    if not subdirectories:
        return mf4_files
    else:
        for subdir in subdirectories:
            mf4_files += collectMF4s(subdir)
        return mf4_files

LOG_LEVEL = 'INFO'

def main():
    logging.basicConfig(
        level='INFO'
    )
    folder = "/home/default/work/mdfParser/test_folder" #TODO: Use argaparse for this later
    start_time = ""
    end_time = ""

    mf4_files = collectMF4s(folder)
    if not mf4_files:
        logging.error("No MF4 files found")

    mdfs = [MDF(file, lazy=True) for file in mf4_files]

    for mdf in mdfs:
        print(f"File: {mdf.name}, Start Time: {datetime.strptime(str(mdf.start_time), '%Y-%m-%d %H:%M:%S%z').time()}")


if __name__ == "__main__":
    main()
