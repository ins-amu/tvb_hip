import argparse
import logging
from dataclasses import dataclass
import typed_args as ta
from . import tools

logger = logging.getLogger(__name__)

_store_true = lambda *a, **kw: ta.add_argument(*a, action='store_true', **kw)

@dataclass
class Args(ta.TypedArgs):
    verbose: bool = _store_true('-v', '--verbose')
    site_check: bool = _store_true('-s', '--site-check')


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--requirements', action='store_true')
    parser.add_argument('--site-check', action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true')
    return parser


def main():
    # get started
    args = Args.from_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)
    logging.debug("cli args %s", args)
    # now do stuff
    if args.site_check:
        assert tools.Local().all_ok
        logger.info('All tools found.')
    else:
        logger.info("nothing to do, bye!")

