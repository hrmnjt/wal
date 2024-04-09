"""
wal
wal open [YY[MM[DD]]]
wal sync [--message "custom"]
wal find
"""

import argparse


def open_log(args):
    print("opening logs")


def sync_log(args):
    print("syncing logs")


def find_log(args):
    print("finding logs")


def cli():
    parser = argparse.ArgumentParser(
        prog="wal",
        description="your personal write-ahead log",
    )
    subparsers = parser.add_subparsers(dest="subparser", help="sub-commands")

    parser_open = subparsers.add_parser("open", help="open logs")
    parser_open.add_argument(
        "date",
        type=str,
        metavar="[YY[MM[DD]]]",
        help="open or create a log for input date",
    )
    parser_open.set_defaults(func=open_log)

    parser_sync = subparsers.add_parser("sync", help="sync logs")
    parser_sync.add_argument(
        "-m",
        "--message",
        type=str,
        metavar="message",
        help="sync logs with custom message",
    )
    parser_sync.set_defaults(func=sync_log)

    parser_find = subparsers.add_parser("find", help="find logs")
    parser_find.set_defaults(func=find_log)

    args = parser.parse_args()

    if args.subparser:
        args.func(args)
    else:
        print("defaulting program")

    print(f"args are: {args}")

    return None


if __name__ == "__main__":
    cli()
