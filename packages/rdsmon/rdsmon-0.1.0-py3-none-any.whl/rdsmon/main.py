import boto3
from commandline import parse_command_line_flags
from const import CLOUD_WATCH_SERVICE_NAME
from const import LIBRARY_NAME
from loguru import logger
from pkg_resources import get_distribution


def main() -> int:
    """The core entrypoint to rdsmon."""
    logger.info(f"Rdsmon has been loaded. (version: {get_distribution(LIBRARY_NAME).version})")
    _ = parse_command_line_flags()
    _ = boto3.client(CLOUD_WATCH_SERVICE_NAME)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
