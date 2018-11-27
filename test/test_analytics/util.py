
def assert_size_match_history(size, history):
    size_from_history = 0
    for _, csize in history.items():
        size_from_history += csize
    assert(size == size_from_history)
