from persper.analytics.score import commit_overall_scores


def test_commit_overall_scores():
    # sums up to 1
    commit_devranks = {
        'abcdefg': 0.2,
        'bcdefgh': 0.3,
        'cdefghi': 0.4,
        'defghij': 0.1,
    }

    # suppose a commit can be one of two types
    clf_results = {
        'abcdefg': [0.3, 0.7],
        'bcdefgh': [0.9, 0.1],
        'cdefghi': [0.2, 0.8],
        'defghij': [0.6, 0.4],
    }

    # the first type is twice as valuable as the second type
    label_weights = [2, 1]

    score_truth = {
        'abcdefg': 0.17687074829931967,
        'bcdefgh': 0.3877551020408163,
        'cdefghi': 0.326530612244898,
        'defghij': 0.108843537414966
    }

    top_one_score_truth = {
        'abcdefg': 0.14285714285714285,
        'bcdefgh': 0.4285714285714285,
        'cdefghi': 0.2857142857142857,
        'defghij': 0.14285714285714285
    }

    assert score_truth == commit_overall_scores(commit_devranks, clf_results, label_weights)
    assert top_one_score_truth == commit_overall_scores(commit_devranks, clf_results, label_weights, top_one=True)
