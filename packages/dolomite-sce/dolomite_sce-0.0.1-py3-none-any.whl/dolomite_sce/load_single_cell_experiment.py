from typing import Any
from dolomite_se import load_summarized_experiment


def load_single_cell_experiment(meta: dict[str, Any], project):
    # TODO: actually load an SCE once the SCE package has cleaned up its shit.
    return load_summarized_experiment(meta, project)
