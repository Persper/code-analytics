import logging
from typing import Dict, List ,Optional,Set

import numpy as np
from networkx import DiGraph

_logger = logging.getLogger(__file__)


def eval_project_complexity(G: DiGraph, r_n: float, r_e: float,commit_black_list: Optional[Set] = None):
    """
    Evaluates project complexity from the specified bare call commit graph.
    remarks
        The formula is
            complexity = sum_by_node(added_units + removed_units) + r_n*len(nodes) + r_e*len(edges)
    """
    logical_units = 0
    useFallback = None
    
    for _, data in G.nodes(data=True):
        added = 0
        removed = 0
        for hexsha, v in data["history"].items():
            if commit_black_list is not None and hexsha in commit_black_list:
                continue

            if useFallback == None:
                useFallback = not "added_units" in v
                if useFallback:
                    _logger.warning(
                        "Will use LOC instead of logic units to measure complexity.")
            if useFallback:
                added += v["adds"]
                removed += v["dels"]
            else:
                added += v["added_units"]
                removed += v["removed_units"]
        logical_units += added + removed
    complexity = logical_units + r_n*len(G.nodes) + r_e*len(G.edges)
    return complexity
