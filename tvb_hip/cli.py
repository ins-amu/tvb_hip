import argparse
import logging


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--requirements', action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true')
    return parser


def main():
    # get started
    parser = build_parser()
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)
    logging.debug("cli args %s", args)
    # now do stuff
    logging.info("nothing to do, bye!")

