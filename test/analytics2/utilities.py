from persper.analytics2.utilities import NodeHistoryAccumulator
from persper.analytics2.abstractions.callcommitgraph import NodeId

def test_node_history_accumulator():
    nodeHistory = NodeHistoryAccumulator()
    testId0 = NodeId("CTest0", "cpp")
    testId1 = NodeId("CTest1", "cpp")
    testId2 = NodeId("CTest2", "cpp")
    nodeHistory.add(testId1, 10, 20)
    nodeHistory.add(testId2, -10, 20)
    nodeHistory.add(testId1, 5, -5)
    assert nodeHistory.get(testId0) == (0, 0)
    assert nodeHistory.get(testId1) == (15, 15)
    assert nodeHistory.get(testId2) == (-10, 20)
    # TODO test `apply` with MemoryCCG
