from persper.analytics.score import commit_overall_scores
from pytest import fixture

@fixture
def commit_devranks():
    # sums up to 1
    return {
        'abcdefg': 0.2,
        'bcdefgh': 0.3,
        'cdefghi': 0.4,
        'defghij': 0.1,
    }

@fixture
def clf_results():
    # suppose a commit can be one of two types
    return {
        'abcdefg': [0.3, 0.7],
        'bcdefgh': [0.9, 0.1],
        'cdefghi': [0.2, 0.8],
        'defghij': [0.6, 0.4],
    }

@fixture
def label_weights():
    # the first type is twice as valuable as the second type
    return [2, 1]

def test_commit_overall_scores_multiplicative(commit_devranks, clf_results, label_weights):
    expected = {
        'abcdefg': 0.17687074829931967,
        'bcdefgh': 0.3877551020408163,
        'cdefghi': 0.326530612244898,
        'defghij': 0.108843537414966
    }

    assert expected == commit_overall_scores(commit_devranks, clf_results, label_weights)

def test_commit_overall_scores_multiplicative_with_top_one(commit_devranks, clf_results, label_weights):
    expected = {
        'abcdefg': 0.14285714285714285,
        'bcdefgh': 0.4285714285714285,
        'cdefghi': 0.2857142857142857,
        'defghij': 0.14285714285714285
    }

    assert expected == commit_overall_scores(commit_devranks, clf_results, label_weights, top_one=True)

def test_commit_overall_scores_additive(commit_devranks, clf_results, label_weights):
    expected = {
        'abcdefg': 0.17687074829931967,
        'bcdefgh': 0.3877551020408163,
        'cdefghi': 0.326530612244898,
        'defghij': 0.108843537414966,
    }

    assert expected == commit_overall_scores(commit_devranks, clf_results, label_weights)

def test_commit_overall_scores_additive_with_top_one(commit_devranks, clf_results, label_weights, additive=True):
    expected = {
        'abcdefg': 0.18,
        'bcdefgh': 0.32,
        'cdefghi': 0.26,
        'defghij': 0.24,
    }

    assert expected == commit_overall_scores(commit_devranks, clf_results, label_weights, top_one=True, additive=True)