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
    patch2_truth = (
        [[0, 6]], 
        []
    )
    parser = PatchParser()
    with open(os.path.join(dir_path, 'example2.patch'), 'r') as f:
        example2_patch = f.read()
        parsing_result = parser.parse(example2_patch)
        assert(parsing_result == patch2_truth)




