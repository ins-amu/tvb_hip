import argparse
import logging
from . import tools

logger = logging.getLogger(__name__)

# command handlers
def handle_recon(args):
    logger.info('handling recon command')

def handle_inference(args):
    logger.info('handling inference command')

# create arg parser
def add_common_arguments(parser):
    parser.add_argument('--subject', '-s', help='subject ID')
    parser.add_argument('--subjects-directory', '-d', help='FreeSurfer $SUBJECTS_DIR')

# subparsers
def add_recon_command(subparsers):
    parser = subparsers.add_parser('recon', help='reconstruct a virtual brain from data')
    add_common_arguments(parser)
    parser.set_defaults(func=handle_recon)

def add_inference_command(subparsers):
    parser = subparsers.add_parser(
            'inference',
            help='perform inference with a virtual brain')
    parser.add_argument(
            '--fast', '-f',
            action='store_true',
            help='do inference quickly')
    add_common_arguments(parser)
    parser.set_defaults(func=handle_inference)

def build_resection_parser():
    return

def build_atlas_parser():
    return

def build_hpc_parser():
    return

def build_util_parser():
    return

def build_main_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--requirements', action='store_true')
    parser.add_argument('--site-check', action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true')

    subparsers = parser.add_subparsers(help='workflow commands')
    add_recon_command(subparsers)
    add_inference_command(subparsers)
    return parser

def main():
    # get started
    parser = build_main_parser()
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)
    logging.debug("cli args %s", args)
    # now do stuff
    if args.site_check:
        assert tools.Local().all_ok
        logger.info('All tools found.')
    elif hasattr(args, 'func'):
        args.func(args)
    else:
        logger.info("nothing to do, bye!")

