from perseper.analytics.analyzer import AnalyzerObserver

class AnalyzerObserverVdev(AnalyzerObserver):
	"""docstring for ClassName"""
    def __init__(self, redis_address, redis_port, git_url):
        self.address = address
        self.port = port
        self.git_url = git_url
        self.redis_conn = redis.StrictRedis(host=address, port=port, charset="utf-8", decode_responses=True)

    
    def onAfterCommit(self, analyzer:Analyzer, index:int, commit, totoal_commits_num:int, isMaster:bool):
        """
        Called after the observed Analyzer has finished analyzing a commit.
        Params:
            analyzer: the observed Analyzer instance.
            index: the index of the commit, depending on the behavior of the analyzer.
                    This is usually a series of 1-based ordinal index for master commits,
                    and another series of 1-based ordinal index for branch commits.
            commit: the commit that has just been analyzed.
            isMaster: whether the current commit is one of the master commits.
        """
        __update_estimated_delay(total_commits, index)

    def function():
    	pass

    
    def __update_estimated_delay(self, total_commits, index):
        estimation = 0.8 * (total_commits - index)
        self.redis_conn.hmset(self.git_url, {'estimated_delay': estimation})

