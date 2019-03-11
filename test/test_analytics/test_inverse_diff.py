import pytest
from persper.analytics.inverse_diff import inverse_diff


def test_inverse_diff():
    # view parsing ground truth here
    # https://github.com/basicthinker/Sexain-MemController/commit/f050c6f6dd4b1d3626574b0d23bb41125f7b75ca
    adds_dels = (
        [[7, 31], [27, 3], [44, 1], [50, 2], [70, 1], [77, 2], [99, 2]],
        [[32, 44], [56, 70]]
    )
    inv_truth = (
        [[65, 13], [79, 15]],
        [[8, 38], [59, 61], [66, 66], [73, 74], [80, 80], [88, 89], [112, 113]]
    )

    inv_result = inverse_diff(*adds_dels)
    assert inv_truth == inv_result
