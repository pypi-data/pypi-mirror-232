from pathlib import Path

from aevol.models.environment import Environment
from aevol.models.individual import Individual
from aevol.visual.grid_view import GridView
from aevol.visual.phenotype_view import PhenotypeView
from aevol.visual.rna_view import RnaView
from aevol.visual.gene_view import GeneView

default_fnames = {
    "rnas": "RNAs.svg",
    "genes": "Genes.svg",
    "phenotype": "Phenotype.svg",
    "grid": "Grid.svg",
}


def draw_all(
    indivfile,
    envfile,
    gridfile,
    outdir: Path,
    display_legend=True,
    fnames=default_fnames,
    verbose=True,
):
    """
    Draw and save to file those views whose required data have been provided

    Args:
        indivfile: individual json file
        envfile: environment json file
        gridfile: grid json file
        outdir (Path): output directory
        display_legend (bool): whether to display legends on the figures
        fnames (dict): output filenames. keys: {"rnas", "genes", "phenotype", "grid"}
        verbose (bool): whether to be verbose
    """
    individual = Individual.from_json_file(indivfile) if indivfile else None
    environment = Environment.from_json_file(envfile) if envfile else None

    # build those views whose required data have been provided
    if individual:
        rna_view = RnaView()
        rna_view.draw(individual, display_legend)
        rna_view.save(outdir / fnames["rnas"], verbose=verbose)

        gene_view = GeneView()
        gene_view.draw(individual, display_legend)
        gene_view.save(outdir / fnames["genes"], verbose=verbose)

    if individual and environment:
        phenotype_view = PhenotypeView()
        phenotype_view.draw(individual, environment, display_legend)
        phenotype_view.save(outdir / fnames["phenotype"], verbose=verbose)

    if gridfile:
        grid_view = GridView()
        grid_view.draw(gridfile, display_legend)
        grid_view.save(outdir / fnames["grid"], verbose=verbose)
