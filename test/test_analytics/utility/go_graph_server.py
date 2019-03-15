import os
import subprocess
import shutil
import tempfile
import time

GO_GRAPH_SERVER_GIT_REPO = "git@gitlab.com:meri.co/golang/graph-server.git"
GO_GRAPH_SERVER_GIT_BRANCH = "master"
GO_GRAPH_SERVER_PKG_MAIN = "gitlab.com/meri.co/golang/gs/app/graphserver"


class GoGraphBackend:

    def __init__(self, server_port: int):
        self.server_port = server_port
        self.git_repo = os.environ.get("GO_GRAPH_SERVER_GIT_REPO")
        if self.git_repo is None or self.git_repo == "":
            self.git_repo = GO_GRAPH_SERVER_GIT_REPO
        self.git_branch = os.environ.get("GO_GRAPH_SERVER_GIT_BRANCH")
        if self.git_branch is None or self.git_branch == "":
            self.git_branch = GO_GRAPH_SERVER_GIT_BRANCH
        self.pkg_main = os.environ.get("GO_GRAPH_SERVER_PKG_MAIN")
        if self.pkg_main is None or self.pkg_main == "":
            self.pkg_main = GO_GRAPH_SERVER_PKG_MAIN
        temp_dir = tempfile.gettempdir()
        self.src_path = os.path.join(temp_dir, 'merico', 'src', 'graph-server')
        self.bin_path = os.path.join(temp_dir, 'merico', 'bin', 'graphserver')
        print("git repo:", self.git_repo)
        print("git branch:", self.git_branch)
        print("pkg main:", self.pkg_main)
        print("src path:", self.src_path)
        print("bin path:", self.bin_path)
        self.process = None

    def build(self):
        # Always use latest source to create test repo
        if os.path.exists(self.src_path):
            shutil.rmtree(self.src_path)
        if os.path.exists(self.bin_path):
            os.remove(self.bin_path)

        ret = subprocess.call(["git", "clone", self.git_repo, self.src_path])
        if ret != 0:
            print("git clone failed")
            exit(1)
        if self.git_branch is not "master":
            ret = subprocess.call(["git", "checkout", "-b", self.git_branch, "origin/" + self.git_branch],
                                  cwd=self.src_path)
            if ret != 0:
                print("git checkout failed")
                exit(1)

        ret = subprocess.call(["git", "pull"], cwd=self.src_path)
        if ret != 0:
            print("git pull failed")
            exit(1)
        ret = subprocess.call(
            ["go", "build", "-o", self.bin_path, self.pkg_main], cwd=self.src_path)
        if ret != 0:
            print("go build failed")
            exit(1)

    def run(self):
        server_address = '127.0.0.1:%d' % self.server_port
        self.process = subprocess.Popen([self.bin_path, "-addr", server_address])
        print("go graph server pid:", self.process.pid)
        print("sleep for 1 second before graph server has been completely started")
        time.sleep(1)

    def terminate(self):
        if self.process is not None:
            self.process.terminate()
            self.process = None
