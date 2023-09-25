"""The syncdir entry point."""
import argparse
import time

import schedule

from syncdirs import SyncDir


def interval(value):
    try:
        int_value = int(value)
        if int_value < 0:
            raise argparse.ArgumentTypeError(
                f"{value} is not a positive integer"
            )
        return int_value
    except ValueError:
        raise argparse.ArgumentTypeError(f"{value} is not a valid integer")


def parse_args() -> argparse.Namespace:
    """
    The `parse_args` function is used to parse command line arguments and
    return them as a `Namespace` object.

    Returns:
        The function `parse_args()` returns an `argparse.Namespace` object.
    """
    parser = argparse.ArgumentParser(
        description="Periodical synchronization of 2 folders"
    )
    parser.add_argument(
        "SOURCE", help="The path to the source file or directory"
    )
    parser.add_argument(
        "REPLICA", help="The path to the replica file or directory"
    )
    parser.add_argument(
        "--logfile",
        default="syncdir.log",
        help="Name of a log file. Default is syncdir.log",
    )
    parser.add_argument(
        "--interval",
        type=interval,
        default="60",
        help="Interval of synchronization in seconds. Default is 60s",
    )
    return parser.parse_args()


def main():
    """
    The main function sets up a directory synchronization process and schedules
    it to run at regular intervals.
    """
    args = parse_args()
    synchronizer = SyncDir(args.SOURCE, args.REPLICA, args.logfile)
    synchronizer.sync()

    schedule.every(args.interval).seconds.do(synchronizer.sync)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
