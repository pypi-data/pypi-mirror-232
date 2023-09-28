# -*- coding: utf-8 -*-

import click
import ast
import os
import sys
from copy import deepcopy
from ARS_Test.semantic_test import run_semantic_test
from pkg_resources import get_distribution, DistributionNotFound
from warnings import simplefilter
# ignore all future warnings
simplefilter(action='ignore', category=FutureWarning)

try:
    __version__ = get_distribution("ARS_Test").version
except DistributionNotFound:
     # package is not installed
    pass
            
            
@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.version_option(version=__version__)
@click.option('--env', type=click.Choice(['dev', 'ci', 'test', 'prod'], case_sensitive=False))
@click.option('--query_type', type=click.STRING, help='default: treats(cretive)', default='treats(creative)')
@click.argument('input_curie', type=click.STRING, default='')
@click.argument('output_curie', type=click.STRING, default='')
@click.option('--expected_output', type=click.Choice(['TopAnswer', 'Acceptable', 'BadButForgivable', 'NeverShow'], case_sensitive=False))




def main(env, query_type, input_curie, output_curie, expected_output):

    click.echo(f"performing ARS_test analysis")

    #pylint: disable=too-many-arguments
    pipeline = run_semantic_test(env, query_type, input_curie, output_curie, expected_output)
    return pipeline
