# SPDX-FileCopyrightText: 2023-present Wytamma Wirth <wytamma.wirth@me.com>
#
# SPDX-License-Identifier: MIT
from pathlib import Path
from typing import List, Optional

import typer

from stem_rate import BeastXML
from stem_rate.__about__ import __version__

app = typer.Typer(
    name="stem_rate",
    help="A CLI for adding a fixed local clock stem model to BEAST XML files.",
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]}
)
# version callback
def version_callback(value: bool):
    if value:
        typer.echo(f"stem-rate: {__version__}")
        raise typer.Exit()

@app.command()
def flc(
        xml: Path = typer.Argument(..., help="Path to BEAST XML file"),
        stem: List[str] = typer.Option(..., "--stem", "-s", help="Group sequences containing this value to define a stem."),
        fasta: Optional[Path] = typer.Option(None, "--fasta", "-f", help="Sequences to add to XML in FASTA format. Dates must be in decimal year format."),
        delimiter: str = typer.Option("|", "--delimiter", "-d", help="Delimiter for date in FASTA header"),
        position: int = typer.Option(-1, "--position", "-p", help="Position of date in FASTA header"),
        output: Path = typer.Option(..., "--output", "-o", help="Path to output BEAST XML file"),
        version: Optional[bool] = typer.Option(None, "--version", "-v", callback=version_callback, is_eager=True, help="Print the version and exit."),
    ):
    """Add a fixed local clock stem model to BEAST1 XML file."""
    xml: BeastXML = BeastXML(xml)
    if fasta is not None:
        xml.add_fasta(fasta, date_delimiter=delimiter, date_position=position)
    for s in stem:
        group = xml.create_stem_group(s)
        xml.insert_after(xml.taxa, group)
        coalescent_simulator = xml.create_coalescent_simulator(s)
        xml.add_to_starting_tree(coalescent_simulator)

    for tree_statistic in xml.tree_statistics:
        xml.add_tree_statistic(tree_statistic)

    xml.add_local_clock(xml.local_clock)

    xml.add_rate_statistic(xml.coefficient_of_variation_statistic)
    xml.add_rate_statistic(xml.rate_covariance_statistic)

    for operator in xml.operators:
        xml.add_operator(operator)

    for prior in xml.priors:
        xml.add_prior(prior)

    xml.update_log()

    xml.write(output)
