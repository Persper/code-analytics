## Data set format

Each [project]-issues directory contains JIRA issues and GitHub pull request
(PR) comments of the project. Only issues resolved and PRs closed by commits
are included.

In a project directory, every file starts with the commit hash (first ten
digits) that the issue/PR is associated with. You can browse the commit via
https://github.com/[user]/[project]/commit/[hash]. E.g.,
https://github.com/apache/spark/commit/b8aec6cd23.

There are two types of files.

1. [hash]-[PROJECT]-[#].xml is an XML representation of the JIRA issue. You can
browse the original issue via
https://issues.apache.org/jira/browse/[PROJECT]-[#].  E.g.,
https://issues.apache.org/jira/browse/SPARK-10474.

2. [hash]-GitHub-[#].xml is an XML representation of the PR conversation. You
can browse the original PR via https://github.com/[user]/[project]/pull/[#].
E.g., https://github.com/apache/spark/pull/13796.

Besides, there are shadow files starting with ``.invalid.''. They can be
ignored by users of this data set. Those files denote wrong information in
commit messages. 
