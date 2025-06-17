from asammdf import MDF
from pathlib import Path
import logging
from datetime import datetime, timezone
from dateutil import parser as date_parser
import argparse
import sys

LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# Custom datetime parser for flexible formats


def parse_datetime(value):
    try:
        dt = date_parser.parse(value, fuzzy=True)
        user_timezone = datetime.now().astimezone().tzinfo
        dt = dt.replace(second=0, microsecond=0, tzinfo=user_timezone)
        return dt
    except ValueError as e:
        raise argparse.ArgumentTypeError(f"Invalid datetime format: {e}")


def convert_to_utc(local_time):
    user_timezone = datetime.now().astimezone().tzinfo

    if local_time.tzinfo is None:
        local_time = local_time.replace(tzinfo=user_timezone)

    return local_time.astimezone(timezone.utc)


def get_filtered_mdfs(mf4_files, start_time, end_time):
    mdfs = [MDF(file, process_bus_logging=False) for file in mf4_files]

    # Util function for filtering mdfs
    def is_within_timeframe(mdf):
        current_time = datetime.strptime(
            str(mdf.start_time), '%Y-%m-%d %H:%M:%S%z')
        return start_time <= current_time <= end_time

    filtered_mdfs = list(filter(is_within_timeframe, mdfs))
    return filtered_mdfs


def combine_and_decode_mf4(mdfs, dbc_paths) -> MDF:
    if len(mdfs) > 1:
        logging.info(f"Merging all .mf4 files into one.")
        combined_mdf = MDF.concatenate(mdfs, sync=False, version='4.0.0')
    elif len(mdfs) == 1:
        combined_mdf = mdfs[0]
    else:
        logging.error("No MF4 files are within the specified region")
        sys.exit(1)

    database_files = {
        "CAN": [(i, 0) for i in dbc_paths],  # 0 specifies any bus channel
    }

    combined_mdf = combined_mdf.extract_bus_logging(
        database_files=database_files,
        version='4.0.0',
        ignore_value2text_conversion=True,
    )

    return combined_mdf


def main():
    logging.basicConfig(
        format=LOG_FORMAT,
        level=LOG_LEVEL
    )

    parser = argparse.ArgumentParser(
        description="Decode and combine MF4 files within the timeframe")

    parser.add_argument(
        "folder",
        type=str,
        help="The folder containing the MF4 files to process"
    )

    parser.add_argument(
        "dbc_paths",
        nargs='+',  # Accept one or more values
        type=str,
        help="One or more DBC file paths (space-separated)"
    )

    parser.add_argument(
        "--start",
        type=parse_datetime,
        required=True,
        help="Enter date and time (e.g. '2025-06-16 14:45')"
    )

    parser.add_argument(
        "--end",
        type=parse_datetime,
        required=True,
        help="Enter date and time (e.g. '2025-06-16 14:45')"
    )

    parser.add_argument(
        "--filename",
        type=str,
        required=False,
        help="Decoded file name"

    )

    parser.usage = "python main.py <folder> <dbc_paths...> --start <start_time> --end <end_time> --filename <decoded_filename>"

    args = parser.parse_args()
    start_time = convert_to_utc(args.start)
    end_time = convert_to_utc(args.end)
    decoded_filename = "Decoded.MF4"

    if args.filename:
        decoded_filename = args.filename

    folder = Path(args.folder)
    dbc_paths = map(Path, args.dbc_paths)

    mf4_files = [str(file) for file in Path(folder).rglob('*.mf4')]
    logging.info(f"Number of MF4 files found: {len(mf4_files)}")

    if not mf4_files:
        logging.error("No MF4 files found")

    mdfs = get_filtered_mdfs(mf4_files, start_time, end_time)
    logging.info(
        f"Number of MF4 files found within given timeframe: {len(mdfs)}")

    decoded_mdf = combine_and_decode_mf4(mdfs, dbc_paths)

    logging.info(f"Saving decoded file as: {decoded_filename}")
    decoded_mdf.save(Path.cwd().joinpath(decoded_filename))


if __name__ == "__main__":
    main()
