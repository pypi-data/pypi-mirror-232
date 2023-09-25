#!/usr/bin/env python
"""print gists.json"""
import json
import os
import click
from github_gists_json import get_data

MODULE_NAME = __name__.split('.')[0]
USAGE = 'python -m %s [login]' % MODULE_NAME
PROG_NAME = 'python -m %s ' % USAGE


@click.command()
def _cli(login=None):
    data = list(filter(lambda d:d['public']==False,get_data()))
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    _cli()
