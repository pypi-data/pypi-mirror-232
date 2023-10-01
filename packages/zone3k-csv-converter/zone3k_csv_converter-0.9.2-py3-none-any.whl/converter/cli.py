import argparse
import sys

from .core import csv_converter


def positive_int_type(value: str) -> int:
    if not value.isdigit():
        raise argparse.ArgumentTypeError("Invalid value.")

    return_value = int(value)

    if return_value < 0:
        raise argparse.ArgumentTypeError("Value may not be less than 0.")

    return return_value


argument_parser = argparse.ArgumentParser(prog="converter")

argument_parser.add_argument(
    "-f",
    "--format",
    dest="output_format",
    choices=["json"],
    default="json",
    help="Determine the format of conversion.",
)

argument_parser.add_argument(
    "-s",
    "--skip",
    dest="skip_rows",
    type=positive_int_type,
    default=None,
    help="Determine how many rows to skip.",
)

argument_parser.add_argument(
    "-t",
    "--take",
    dest="take_rows",
    type=positive_int_type,
    default=None,
    help="Determine how many rows to take.",
)


def main() -> int:
    args = argument_parser.parse_args()
    result = csv_converter.convert(
        sys.stdin,
        output_format=args.output_format,
        skip_rows=args.skip_rows,
        take_rows=args.take_rows,
    )
    sys.stdout.write(result)
    return 0
