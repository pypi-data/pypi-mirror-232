import argparse

from configuration import Configuration


def parse_command_line_flags() -> Configuration:
    """Parse sys.argv into something meaningful.  This will be getting
    replaced with `typeR` later."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--region",
        "-r",
        dest="region",
        action="store",
        required=True,
        help="The region to look up rds instances within",
    )
    parser.add_argument(
        "--period",
        "-p",
        action="store",
        type=int,
        help="The period in (seconds) which to query metrics for, defaulting to 1 minute",
        default=60,
    )
    return Configuration(**vars(parser.parse_args()))
