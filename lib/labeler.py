# Standard labels (4 main classes):
BUG = 'bug'
FEATURE = 'feature'
MAINTENANCE = 'maintenance'
IMPROVEMENT = 'improvement'
SKIP = '_' # Excluded.

# Additional labels for Linux filesystem patches
PERFORMANCE = 'performance'
RELIABILITY = 'reliability'

# Mapping from project-specific labels to the standard:

fs_labeler = { # For the Linux filesystem patches data set.
    'b':BUG,
    'f':FEATURE,
    'p':PERFORMANCE,
    'c':RELIABILITY,
    'misc':MAINTENANCE,
}

apache_labeler = { # For Apache JIRA projects.
    'Bug':BUG,
    'New Feature':FEATURE,
    'Improvement':IMPROVEMENT,
    'Test':MAINTENANCE,
    'Documentation':MAINTENANCE,
    'Dependency upgrade':MAINTENANCE,
    'Github Integration':MAINTENANCE,
    'Wish':SKIP,
    'Question':SKIP,
    'Brainstorming':SKIP,
    # The following are agile terms, simply skipped for now.
    'Epic':SKIP,
    'Story':SKIP,
    'Task':SKIP,
    'Technical task':SKIP,
    'Sub-task':SKIP,
    'Umbrella':SKIP,
}

