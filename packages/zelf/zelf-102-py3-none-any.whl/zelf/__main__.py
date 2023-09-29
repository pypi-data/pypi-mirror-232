# This file is placed in the Public Domain.
#
# pylint: disable=E0402


"main"


from .run import main, wrap


if __name__ == "__main__":
    wrap(main)
