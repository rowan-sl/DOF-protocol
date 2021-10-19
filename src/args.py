import argparse, pathlib

parser = argparse.ArgumentParser()
parser.add_argument(
    "--io",
    dest="io_file",
    type=pathlib.Path,
    help="files for io. must be two seperate files.",
    required=True,
    metavar=("SRV_OUT", "SRV_STAT", "SRV_READ_SIG", "CLI_OUT", "CLI_STAT", "CLI_READ_SIG"),
    nargs=6,
)
args = parser.parse_args()