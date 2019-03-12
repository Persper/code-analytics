import re

_hunkHeader = re.compile(
    r"^@@\s*\-(?P<LN>\d+),\s*\d+\s+\+(?P<RN>\d+),\s*\d+\s*@@")


def parseUnifiedDiff(diffContent: str, lineNumberOffset: int = 0):
    """
    Parse unified diff content, and return the ranges of added and removed lines.
    Returns
        (addedRanges, removedRanges), where
            addedRanges: a list of line ranges [[startLine1, endLine1], ...] added into the new file,
                        using the 1-based line numbers in the new file.
            removedRanges: a list of line ranges [[startLine1, endLine1], ...] removed from the old file,
                        using the 1-based line numbers in the old file.
    """
    leftLine: int = None
    rightLine: int = None
    addedRanges = []
    removedRanges = []
    lastAddedRange: list = None
    lastRemovedRange: list = None
    isInPrologue = True
    for diffLine in diffContent.rstrip("\r\n\v").split("\n"):
        if diffLine.startswith("@@"):
            match = _hunkHeader.search(diffLine)
            if not match:
                if isInPrologue:
                    continue
                raise ValueError(str.format(
                    "Invalid diff line: {0}.", diffLine))
            leftLine = int(match.group("LN")) + lineNumberOffset
            rightLine = int(match.group("RN")) + lineNumberOffset
            lastAddedRange = lastRemovedRange = None
            isInPrologue = False
        elif diffLine.startswith(" "):
            assert leftLine != None and rightLine != None
            leftLine += 1
            rightLine += 1
            lastAddedRange = lastRemovedRange = None
        elif diffLine.startswith("-"):
            assert leftLine != None and rightLine != None
            if lastRemovedRange:
                lastRemovedRange[1] = leftLine
            else:
                lastRemovedRange = [leftLine, leftLine]
                removedRanges.append(lastRemovedRange)
            leftLine += 1
        elif diffLine.startswith("+"):
            assert leftLine != None and rightLine != None
            if lastAddedRange:
                lastAddedRange[1] = rightLine
            else:
                lastAddedRange = [rightLine, rightLine]
                addedRanges.append(lastAddedRange)
            rightLine += 1
        elif diffLine.startswith("\\"):
            # \ No newline at end of file
            # Do nothing. We ignore blank lines.
            pass
        else:
            if isInPrologue:
                continue
            raise ValueError(str.format("Invalid diff line: {0}.", diffLine))
    return addedRanges, removedRanges
