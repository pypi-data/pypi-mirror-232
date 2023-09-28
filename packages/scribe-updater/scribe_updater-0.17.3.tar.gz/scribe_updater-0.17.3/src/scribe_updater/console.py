import os

import click

from scribe_updater.updater import Updater
from scribe_updater.utils import load_json, make_lower, read_csv
from . import __version__


@click.command()
@click.version_option(version=__version__)
@click.option("-t", "--target", help="financial instutions ground truth", required=True)
@click.option("-g", "--ground", help="master ground truth", required=True)
@click.option(
    "-v", "--variables", help="path for the variables csv or json", required=False
)
@click.option("-o", "--output", help="output path for the result", required=True)
@click.option(
    "-m",
    "--mappings",
    help="version mappings json file for finie versions, see docs for available mappings",
    required=False,
)
@click.option(
    "-a",
    "--authtype",
    help="select pba or vba, default is pba",
    required=False,
)
def main(target, ground, output, variables=None, mappings=None, authtype="pba"):
    """A tool to update scribe competency configurations."""
    try:
        target = make_lower(load_json(target))
        ground = make_lower(load_json(ground))
        v = None
        is_csv = False
        if variables:
            if str(variables).endswith(".csv"):
                is_csv = True
                v = read_csv(variables)
            else:
                is_csv = False
                v = load_json(variables)
        version_map = {}
        path = f"src/scribe_updater/version_mapping/{mappings}"
        if os.path.isfile(path):
            version_map = load_json(path)
        else:
            version_map = {}

        updater = Updater(ground, target, v, output, version_map, is_csv)

        updater.prep_output_pba()
        updater.update()
        updater.output_to_json()
        updater.get_change_log()
    except Exception as e:
        click.echo(f"error from updater script : {e}")
