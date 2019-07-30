import logging
from typing import Dict


def normalize_with_coef(scores: Dict[str, float], coef=1.0) -> Dict[str, float]:
    """Normalize the values of scores to sum to coef (whose default is 1)"""
    normalized_scores = {}
    score_sum = 0.0
    for _, score in scores.items():
        score_sum += score

    if score_sum == 0:
        logging.error('normalize_with_coef: ZeroDivisionError!')
        for k in scores:
            normalized_scores[k] = 0.0
    else:
        for k, v in scores.items():
            normalized_scores[k] = v / score_sum * coef
    return normalized_scores
