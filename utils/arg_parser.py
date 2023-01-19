import argparse

def parse_args():
    parser = argparse.ArgumentParser(
        description="Watch movies or anime from api.consumet.org"
    )

    parser.add_argument(
        "-q",
        "--quality",
        action="store",
        required=False,
        default="auto",
    )
    parser.add_argument(
        "-H",
        "--history",
        required=False,
        dest="history",
        action="store_true",
    )
    parser.add_argument(
        "-d",
        "--download",
        required=False,
        dest="download",
        action="store_true",
    )
    parser.add_argument(
        "-u",
        "--update",
        required=False,
        dest="update",
        action="store_true",
    )
    parser.add_argument(
        "-C",
        "--continue",
        required=False,
        dest="continue",
        action="store_true",
    )
    parser.add_argument(
        "-c",
        "--config",
        required=False,
        dest="config",
        action="store_true",
    )
    parser.add_argument(
        "-v",
        "--vlc",
        required=False,
        dest="vlc",
        action="store_true",
    )
    parser.add_argument(
        "-s",
        "--sources",
        required=False,
        dest="sources",
        action="store_true",
    )

    return parser.parse_args()