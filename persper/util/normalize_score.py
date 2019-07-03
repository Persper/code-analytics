from typing import Dict
import logging

def normalize_with_coef(scores: Dict[str, float], coef=1.0) -> Dict[str, float]:
    normalized_scores = {}
    score_sum = 0
    for _, score in scores.items():
        score_sum += score

    for idx in scores:
        try:
            normalized_scores[idx] = scores[idx] / score_sum * coef
        except ZeroDivisionError:
            normalized_scores[idx] = 0
            logging.error('discover ZeroDivisionError!')

    return normalized_scores
