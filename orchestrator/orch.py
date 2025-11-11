'''
    This is the main entry point of our orchestrator.
    In here we have sure to start the message handling process and set up the logging level to INFO.
    Feel free to change the logging level to DEBUG if you want to see more detailed logs.
'''
from messaging import start_handling_messages
import logging
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Orchestrator for handling code block messages")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging")
    return parser.parse_args()

def set_logging_level(verbose):
    if verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )


def main():
    args = parse_args()
    set_logging_level(args.verbose)
    start_handling_messages()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Exiting the program")
        exit(0)