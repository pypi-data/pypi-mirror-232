import os
import subprocess
import sys


def main():
    sys.exit(subprocess.call([
        os.path.join(os.path.dirname(__file__), "binary/tes"),
        *sys.argv[1:]
    ]))
