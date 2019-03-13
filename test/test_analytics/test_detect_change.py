import os
from persper.analytics.patch_parser import PatchParser
from persper.analytics.detect_change import get_changed_functions
from persper.analytics.call_graph.cpp import get_func_ranges_cpp
from persper.analytics.srcml import src_to_tree

dir_path = os.path.dirname(os.path.abspath(__file__))


def test_detect_change():
    parser = PatchParser()

    # view parsing ground truth here
    # https://github.com/basicthinker/Sexain-MemController/commit/f050c6f6dd4b1d3626574b0d23bb41125f7b75ca
    parsing_truth = (
        [[7, 31], [27, 3], [44, 1], [50, 2], [70, 1], [77, 2], [99, 2]],
        [[32, 44], [56, 70]]
    )

    # view function ranges ground truth here
    # https://github.com/basicthinker/Sexain-MemController/blob/5b8886d9da3bb07140bfb1ff2d2b215b2dff584b/migration_controller.cc
    func_ranges_truth = (
        ['MigrationController::InputBlocks',
         'MigrationController::ExtractNVMPage',
         'MigrationController::ExtractDRAMPage',
         'MigrationController::Clear'],
        [[8, 28], [30, 52], [54, 79], [81, 100]]
    )

    changed_result = {
        'MigrationController::Clear': 2,
        'MigrationController::ExtractDRAMPage': 18,
        'MigrationController::ExtractNVMPage': 16,
        'MigrationController::InputBlocks': 3
    }

    with open(os.path.join(dir_path, 'example.patch'), 'r') as f:
        example_patch = f.read()
        parsing_result = parser.parse(example_patch)
        assert parsing_result == parsing_truth

    with open(os.path.join(dir_path, 'example.cc'), 'r') as f:
        root = src_to_tree('example.cc', f.read())
        func_ranges_result = get_func_ranges_cpp(root)
        assert func_ranges_result == func_ranges_truth

    assert changed_result == get_changed_functions(
        *func_ranges_result, *parsing_result)


def test_get_changed_functions():
    """This test is added to reproduce the bug described in
    https://gitlab.com/persper/code-analytics/issues/12
    """
    func_ranges_truth = (
        ['append',
         'add',
         'insert'],
        [[9, 20], [23, 38], [41, 65]]
    )

    parser = PatchParser()
    with open(os.path.join(dir_path, 'example7.patch'), 'r') as f:
        example_patch = f.read()
        parsing_result = parser.parse(example_patch)

    changed_truth = {
        'append': {
            'adds': 26,
            'dels': 9
        },
        'add': {
            'adds': 0,
            'dels': 5
        },
        'insert': {
            'adds': 0,
            'dels': 25
        }

    }
    assert changed_truth == get_changed_functions(
        *func_ranges_truth, *parsing_result, separate=True)


def test_patch_parser():
    parser = PatchParser()

    patch2_truth = (
        [[0, 6]],
        []
    )
    with open(os.path.join(dir_path, 'example2.patch'), 'r') as f:
        example2_patch = f.read()
        parsing_result = parser.parse(example2_patch)
        assert parsing_result == patch2_truth

    # view patch3_truth here
    # https://github.com/UltimateBeaver/test_feature_branch/commit/caaac10f604ea7ac759c2147df8fb2b588ee2a27
    patch3_truth = (
        [[10, 4], [12, 1], [14, 1], [17, 13]],
        [[9, 10], [12, 12], [14, 14]]
    )
    with open(os.path.join(dir_path, 'example3.patch'), 'r') as f:
        example3_patch = f.read()
        parsing_result = parser.parse(example3_patch)
        assert parsing_result == patch3_truth

    # view patch4_truth here
    # https://github.com/UltimateBeaver/test_feature_branch/commit/364d5cc49aeb2e354da458924ce84c0ab731ac77
    patch4_truth = (
        [[0, 27]],
        []
    )
    with open(os.path.join(dir_path, 'example4.patch'), 'r') as f:
        example4_patch = f.read()
        parsing_result = parser.parse(example4_patch)
        assert parsing_result == patch4_truth


def test_no_newline_at_the_end_of_file():
    parser = PatchParser()
    patch5_truth = (
        [[12, 1]], [[12, 12]]
    )
    with open(os.path.join(dir_path, 'example5.patch'), 'r') as f:
        example5_patch = f.read()
        parsing_result = parser.parse(example5_patch)
        assert parsing_result == patch5_truth

    patch6_truth = (
        [[17, 1], [20, 3], [30, 5]],
        [[12, 12], [17, 17], [20, 20], [22, 22], [24, 30]]
    )
    with open(os.path.join(dir_path, 'example6.patch'), 'r') as f:
        example6_patch = f.read()
        parsing_result = parser.parse(example6_patch)
        assert parsing_result == patch6_truth
