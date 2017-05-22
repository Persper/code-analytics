import os
from graphs.patch_parser import PatchParser 
from graphs.detect_change import get_changed_functions
from graphs.call_graph.cpp import get_func_ranges_cpp
from graphs.srcml import transform_src_to_tree

dir_path = os.path.dirname(os.path.abspath(__file__))

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

def test_detect_change():
    parser = PatchParser()

    with open(os.path.join(dir_path, 'example.patch'), 'r') as f:
        example_patch = f.read()
        parsing_result = parser.parse(example_patch)
        assert(parsing_result == parsing_truth)

    with open(os.path.join(dir_path, 'example.cc'), 'r') as f:
        root = transform_src_to_tree(f.read(), ext='.cc')
        func_ranges_result = get_func_ranges_cpp(root)
        assert(func_ranges_result == func_ranges_truth)

    assert(changed_result == get_changed_functions(
        *func_ranges_result, *parsing_result))

def test_patch_parser():
    parser = PatchParser()

    patch2_truth = (
        [[0, 6]], 
        []
    )
    with open(os.path.join(dir_path, 'example2.patch'), 'r') as f:
        example2_patch = f.read()
        parsing_result = parser.parse(example2_patch)
        assert(parsing_result == patch2_truth)

    # view patch3_truth here
    # https://github.com/UltimateBeaver/test_feature_branch/commit/caaac10f604ea7ac759c2147df8fb2b588ee2a27
    patch3_truth = (
        [[10, 4], [12, 1], [14, 1], [17, 13]],
        [[9, 10], [12, 12], [14, 14]] 
    )
    with open(os.path.join(dir_path, 'example3.patch'), 'r') as f:
        example3_patch = f.read()
        parsing_result = parser.parse(example3_patch)
        print(parsing_result)
        assert(parsing_result == patch3_truth)





