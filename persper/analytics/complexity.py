from typing import Dict, List

import numpy as np
from networkx import DiGraph


def eval_project_complexity(G: DiGraph, r_n: float, r_e: float):
    """
    Evaluates project complexity from the specified bare call commit graph.
    remarks
        The formula is
            complexity = sum_by_node(added_units + removed_units) + r_n*len(nodes) + r_e*len(edges)
    """
    logical_units = 0
    for _, data in G.nodes(data=True):
        added = 0
        removed = 0
        for _, v in data["history"].items():
            # TODO change from LOC to logic units
            added += v["adds"]
            removed += v["dels"]
        logical_units += added + removed
    complexity = logical_units + r_n*len(G.nodes) + r_e*len(G.edges)
    return complexity
