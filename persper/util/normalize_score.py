from typing import Dict


def normalize_with_coef(scores: Dict[str, float], coef=1.0) -> Dict[str, float]:
    normalized_scores = {}
    score_sum = 0
    for _, score in scores.items():
        score_sum += score

    for idx in scores:
        normalized_scores[idx] = scores[idx] / score_sum * coef

    return normalized_scores
