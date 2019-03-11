from typing import Dict, List
import numpy as np


def normalize(scores: Dict[str, float]) -> Dict[str, float]:
    normalized_scores = {}
    score_sum = 0
    for _, score in scores.items():
        score_sum += score

    for idx in scores:
        normalized_scores[idx] = scores[idx] / score_sum
    return normalized_scores


def commit_overall_scores(commit_devranks: Dict[str, float],
                          clf_results: Dict[str, List[float]],
                          label_weights: List[float],
                          top_one=False) -> Dict[str, float]:
    overall_scores = {}
    for sha, dr in commit_devranks.items():
        assert sha in clf_results, "Commit %s does not have label."
        if top_one:
            top_idx = np.argmax(clf_results[sha])
            overall_scores[sha] = label_weights[top_idx] * dr
        else:
            overall_scores[sha] = np.dot(clf_results[sha], label_weights) * dr

    return normalize(overall_scores)
