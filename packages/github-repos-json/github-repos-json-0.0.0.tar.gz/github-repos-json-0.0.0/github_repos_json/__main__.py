#!/usr/bin/env python
"""print repos.json"""
import json
import os
import click
from github_repos_json import get_data

MODULE_NAME = __name__.split('.')[0]
USAGE = 'python -m %s [login]' % MODULE_NAME
PROG_NAME = 'python -m %s ' % USAGE


@click.command()
@click.argument('login',required=False)
@click.option('--type',required=False)
@click.option('--visibility',required=False)
def _cli(login,**options):
    data = get_data(login,**options)
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    _cli()
