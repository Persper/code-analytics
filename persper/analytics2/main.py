import logging
from persper.analytics2.repository import GitRepository
from persper.analytics2.metaanalyzer import MetaAnalyzer
from persper.analytics2.factories import RootContainer
from persper.util.path import root_path
from os import path


def analytics_main(repo_path):
    repo = GitRepository(repo_path)
    container = RootContainer(repo)
    analyzer = MetaAnalyzer(repo,
                            commit_analyzers=[container.CallCommitGraphAnalyzer],
                            post_analyzers=[container.DevRankAnalyzer],
                            origin_commit=None,
                            terminal_commit="HEAD",
                            analyzed_commits=None)
    analyzer.analyze()


# XXX: for ad-hoc testing only
if __name__ == '__main__':
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s [%(name)s] %(message)s", level=logging.INFO)

    analytics_main(path.join(root_path, r"repos\cpp_test_repo"))
