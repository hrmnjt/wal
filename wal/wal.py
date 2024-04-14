from argparse import ArgumentParser
from configparser import ConfigParser
from configparser import NoOptionError
from configparser import NoSectionError
from datetime import date
from datetime import datetime
from math import log10
import os
import subprocess


DEFAULT_CONFIG_PATH = "~/.config/wal/config.ini"
DEFAULT_LOG_DIR = "~/.local/share/wal"
DEFAULT_EDITOR = "nvim"
# FIXME: remove personal info
DEFAULT_GIT_REMOTE_URL = "git@github.com:hrmnjt/wal-test-2.git"
# FIXME: remove personal info
DEFAULT_GIT_USER_NAME = "hrmnjt"
# FIXME: remove personal info
DEFAULT_GIT_USER_EMAIL = "harman@hrmnjt.dev"
DEFAULT_GIT_COMMIT_MESSAGE_PREFIX = "lge: updates at"


def run_command(command, working_dir):
    try:
        result = subprocess.run(
            command,
            cwd=working_dir,
            text=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e.stderr}")
        return None


def open_log(log_date: int, config):
    print("opening logs")

    log_dir = os.path.expanduser(config["DEFAULT"]["LOG_DIR"])
    editor = config["DEFAULT"]["EDITOR"]

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

    os.makedirs(log_dir, exist_ok=True)

    log_file_path = os.path.join(log_dir, f"{expanded_date}.md")
    with open(log_file_path, "a"):
        pass
    subprocess.run([editor, log_file_path])

    return None


def sync_log(message, config):
    print(f"syncing logs using {config} and {message}")

    log_dir = os.path.expanduser(config["DEFAULT"]["LOG_DIR"])
    git_remote_url = config["SYNC"]["GIT_REMOTE_URL"]
    git_user_name = config["SYNC"]["GIT_USER_NAME"]
    git_user_email = config["SYNC"]["GIT_USER_EMAIL"]
    git_commit_message_prefix = config["SYNC"]["GIT_COMMIT_MESSAGE_PREFIX"]

    git_dir = os.path.join(log_dir, ".git")

    default_message = f"{git_commit_message_prefix} \
        {datetime.now().strftime("%Y%m%d%H%M%S")}"
    commit_message = message if message else default_message

    if not os.path.exists(git_dir):
        print("initializing Git repository...")
        init_result = run_command(["git", "init"], log_dir)
        if init_result:
            print(init_result)

        print(f"setting remote repository to {git_remote_url}")
        set_remote_result = run_command(
            ["git", "remote", "add", "origin", git_remote_url], log_dir
        )
        if set_remote_result:
            print(set_remote_result)

        print("configuring user name and email for repository")
        run_command(["git", "config", "user.name", git_user_name], log_dir)
        run_command(["git", "config", "user.email", git_user_email], log_dir)

    os.chdir(log_dir)

    print("adding all changes to staging area...")
    run_command(["git", "add", "."], log_dir)

    print("committing changes...")
    commit_result = run_command(["git", "commit", "-m", commit_message], log_dir)
    if commit_result:
        print(commit_result)

    print("pushing changes to remote repository...")
    push_result = run_command(["git", "push", "-u", "origin", "main"], log_dir)
    if push_result:
        print(push_result)

    return None


def parse_configuration(arg_config):
    default_config_path = os.path.expanduser(DEFAULT_CONFIG_PATH)
    config_path = arg_config if arg_config else default_config_path

    config = ConfigParser()
    if not os.path.exists(config_path):
        config["DEFAULT"] = {"LOG_DIR": DEFAULT_LOG_DIR, "EDITOR": DEFAULT_EDITOR}
        config["SYNC"] = {
            "GIT_REMOTE_URL": DEFAULT_GIT_REMOTE_URL,
            "GIT_USER_NAME": DEFAULT_GIT_USER_NAME,
            "GIT_USER_EMAIL": DEFAULT_GIT_USER_EMAIL,
            "GIT_COMMIT_MESSAGE_PREFIX": DEFAULT_GIT_COMMIT_MESSAGE_PREFIX,
        }
        with open(config_path, "w") as config_file:
            config.write(config_file)
    else:
        config.read(config_path)

    required_sections = {
        "DEFAULT": ["LOG_DIR", "EDITOR"],
        "SYNC": [
            "GIT_REMOTE_URL",
            "GIT_USER_NAME",
            "GIT_USER_EMAIL",
            "GIT_COMMIT_MESSAGE_PREFIX",
        ],
    }

    for section, keys in required_sections.items():
        if section not in config:
            raise NoSectionError(f"missing section {section}")
        else:
            for key in keys:
                if key not in config[section]:
                    raise NoOptionError(f"missing key {key}", f"in section {section}")

    return config


def parse_cli_arguments():
    parser = ArgumentParser(
        prog="wal",
        description="your personal write-ahead log",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        help="specify a custom configuration file path",
    )
    subparsers = parser.add_subparsers(dest="subparser", help="sub-commands")

    parser_open = subparsers.add_parser("open", help="open logs")
    parser_open.add_argument(
        "date",
        type=int,
        metavar="[YYYY[MM[DD]]]",
        help="open or create a log for input date",
    )

    parser_sync = subparsers.add_parser("sync", help="sync logs")
    parser_sync.add_argument(
        "-m",
        "--message",
        type=str,
        metavar="message",
        help="sync logs with custom message",
    )

    return parser.parse_args()


def main():
    args = parse_cli_arguments()

    config = parse_configuration(args.config)

    if args.subparser:
        if args.subparser == "open":
            open_log(args.date, config)
        elif args.subparser == "sync":
            sync_log(args.message, config)
        else:
            args.func(args)
    else:
        print("defaulting program")

    print(f"args are: {args}")

    return None


if __name__ == "__main__":
    main()
