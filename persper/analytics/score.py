import numpy as np
from typing import Dict, List
from persper.util.normalize_score import normalize_with_coef


def commit_overall_scores(commit_devranks: Dict[str, float],
                          clf_results: Dict[str, List[float]],
                          label_weights: List[float],
                          top_one=False,
                          additive=False) -> Dict[str, float]:
    overall_scores = {}
    for sha, dr in commit_devranks.items():
        assert sha in clf_results, "Commit %s does not have label."
        if top_one:
            top_idx = np.argmax(clf_results[sha])
            category_vec = np.zeros(len(label_weights))
            category_vec[top_idx] = 1
        else:
            category_vec = clf_results[sha]

        if additive:
            overall_scores[sha] = np.dot(category_vec, label_weights) + len(commit_devranks) * dr
        else:
            overall_scores[sha] = np.dot(category_vec, label_weights) * dr

    return normalize_with_coef(overall_scores)
