from datetime import date
from math import log10
import argparse
import configparser
import os


DEFAULT_CONFIG_PATH = "~/.config/wal/config.ini"
DEFAULT_LOG_DIR = "~/.local/share/wal"
DEFAULT_EDITOR = "nvim"


def open_log(log_date: int):
    print("opening logs")

    if log_date > 0:
        num_digits = int(log10(log_date)) + 1
    else:
        raise ValueError("incorrect date format, YYYYMMDD, MMDD or DD expected")

    current_year = date.today().year
    current_month = date.today().month

    if num_digits == 8:
        year_part = int(log_date / 10000)
        month_part = int((log_date % 10000) / 100)
        date_part = int(log_date % 100)
    elif num_digits in [3, 4]:
        year_part = current_year
        month_part = int(log_date / 100)
        date_part = int(log_date % 100)
    elif num_digits in [1, 2]:
        year_part = current_year
        month_part = current_month
        date_part = log_date
    else:
        raise ValueError("incorrect date format, YYYYMMDD, MMDD or DD expected")

    try:
        expanded_date = date(year_part, month_part, date_part).strftime("%Y%m%d")
    except ValueError as e:
        raise ValueError(f"incorrect date format; {e}")

    print(f"opening {expanded_date}.md")

    return None


def sync_log():
    print("syncing logs")

    return None


def find_log():
    print("finding logs")

    return None


def open_subcommand(args):
    print(args)
    open_log(args.date)

    return None


def sync_subcommand(args):
    print(args)
    sync_log()

    return None


def find_subcommand(args):
    print(args)
    find_log()

    return None


def parse_configuration(arg_config):
    default_config_path = os.path.expanduser(DEFAULT_CONFIG_PATH)
    config_path = arg_config if arg_config else default_config_path

    config = configparser.ConfigParser()
    if not os.path.exists(config_path):
        config["DEFAULT"] = {"LOG_DIR": DEFAULT_LOG_DIR, "EDITOR": DEFAULT_EDITOR}
        with open(config_path, "w") as config_file:
            config.write(config_file)
    else:
        config.read(config_path)

    # TODO: configuration validation - all required keys should be present

    return config


def parse_cli_arguments():
    parser = argparse.ArgumentParser(
        prog="wal",
        description="your personal write-ahead log",
    )
    parser.add_argument(
        "-c", "--config", type=str, help="specify a custom configuration file path"
    )
    subparsers = parser.add_subparsers(dest="subparser", help="sub-commands")

    parser_open = subparsers.add_parser("open", help="open logs")
    parser_open.add_argument(
        "date",
        type=int,
        metavar="[YYYY[MM[DD]]]",
        help="open or create a log for input date",
    )
    parser_open.set_defaults(func=open_subcommand)

    parser_sync = subparsers.add_parser("sync", help="sync logs")
    parser_sync.add_argument(
        "-m",
        "--message",
        type=str,
        metavar="message",
        help="sync logs with custom message",
    )
    parser_sync.set_defaults(func=sync_subcommand)

    parser_find = subparsers.add_parser("find", help="find logs")
    parser_find.set_defaults(func=find_subcommand)

    return parser.parse_args()


def main():
    args = parse_cli_arguments()

    config = parse_configuration(args.config)

    if config:
        print(config["DEFAULT"]["LOG_DIR"])
        print(config["DEFAULT"]["EDITOR"])

    if args.subparser:
        args.func(args)
    else:
        print("defaulting program")

    print(f"args are: {args}")

    return None


if __name__ == "__main__":
    main()
