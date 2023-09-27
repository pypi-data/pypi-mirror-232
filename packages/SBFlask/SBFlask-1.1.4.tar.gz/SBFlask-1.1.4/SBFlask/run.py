import sys
import logging
import traceback
from .FlaskMain import create_app


def main(args):
    if 'webserver' in str(args).lower():
        create_app()


if __name__ == "__main__":
    main(sys.argv[1:])