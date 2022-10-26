#!/usr/bin/env python

"""Process a scheduled set of events."""

import logging
import sys

from tapo_schedule.schedule import Schedule

logging.basicConfig(level=logging.DEBUG)


def main():
    """Run."""
    schedule = Schedule(sys.argv[1])
    schedule.run()


if __name__ == "__main__":
    main()
