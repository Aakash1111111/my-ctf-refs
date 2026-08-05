# !/usr/bin/env python3
"""picoCTF Web API initialization script."""

from argparse import ArgumentParser
import api
import api.submissions


def main():
    """Parse web API startup flags."""
    parser = ArgumentParser(description="CTF API configuration")
    parser.add_argument(
        "-p",
        "--port",
        action="store",
        help="port the server should listen on.",
        type=int,
        default=8000,
    )
    parser.add_argument(
        "-l",
        "--listen",
        action="store",
        help="host the server should listen on.",
        default="0.0.0.0",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="run the server in debug mode.",
        default=False,
    )
    parser.add_argument(
        "-k",
        "--debug-key",
        action="store",
        help="debug key for problem grading; only applies if debug is enabled",
        type=str,
        default=None,
    )
    args = parser.parse_args()

    if args.debug:
        api.submissions.DEBUG_KEY = args.debug_key

    api.create_app().run(
        host=args.listen, port=args.port, debug=args.debug,
    )


main()
