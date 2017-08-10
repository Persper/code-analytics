# Standard types (4 main classes):
BUG = 'bug'
FEATURE = 'feature'
MAINTENANCE = 'maintenance'
IMPROVEMENT = 'improvement'
SKIP = '_' # Excluded.

# Additional types for Linux filesystem patches:
PERFORMANCE = 'performance'
RELIABILITY = 'reliability'

# Priority labels:
HIGH = 'high'
MID = 'mid'
LOW = 'low'

# Mapping from project-specific types to the standard:

fs_type = { # For the Linux filesystem patches data set.
    'b': BUG,
    'f': FEATURE,
    'p': PERFORMANCE,
    'c': RELIABILITY,
    'misc': MAINTENANCE,
}

apache_type = { # For Apache JIRA projects.
    'Bug': BUG,
    'New Feature': FEATURE,
    'Improvement': IMPROVEMENT,
    'Test': MAINTENANCE,
    'Documentation': MAINTENANCE,
    'Dependency upgrade': MAINTENANCE,
    'Github Integration': MAINTENANCE,
    'Wish': SKIP,
    'Question': SKIP,
    'Brainstorming': SKIP,
    # The following are agile terms, simply skipped for now.
    'Epic': SKIP,
    'Story': SKIP,
    'Task': SKIP,
    'Technical task': SKIP,
    'Sub-task': SKIP,
    'Umbrella': SKIP,
}

apache_priority = { # For Apache JIRA projects.
    'Blocker': HIGH,
    'Critical': HIGH,
    'Major': MID,
    'Minor': LOW,
    'Trivial': LOW,
    'No priority': SKIP,
}
