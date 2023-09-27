import os
import shutil


class GitReadOnly:
    def __init__(self, git_repo_url):
        self.git_repo_url = git_repo_url
        self.dir_repo = None
        self.branch_name = None

    def clone(self, dir_repo, force=False):
        self.dir_repo = dir_repo
        self.force = force

    def init_dir_repo(self):
        if os.path.exists(self.dir_repo):
            shutil.rmtree(self.dir_repo)
        os.mkdir(self.dir_repo)

    @property
    def cmd_clone(self):
        assert self.git_repo_url is not None
        assert self.dir_repo is not None
        assert self.branch_name is not None

        return ''.join(
            [
                f'git clone  -b {self.branch_name} --single-branch ',
                f' {self.git_repo_url} {self.dir_repo}',
            ]
        )

    @property
    def cmd_cd(self):
        assert self.dir_repo is not None
        return f'cd {self.dir_repo}'

    @property
    def cmd_git_pull(self):
        assert self.branch_name is not None
        return f'git pull origin {self.branch_name}'

    @property
    def cmd_checkout(self):
        assert self.branch_name is not None
        return f'git checkout {self.branch_name}'

    @staticmethod
    def run(*cmd_list):
        cmd = ' && '.join(cmd_list)
        os.system(cmd)

    def checkout(self, branch_name):
        self.branch_name = branch_name

        if not os.path.exists(self.dir_repo) or self.force:
            self.init_dir_repo()
            self.run(
                self.cmd_cd,
                self.cmd_clone,
            )

        self.run(
            self.cmd_cd,
            self.cmd_checkout,
            self.cmd_git_pull,
        )

    def add_and_commit(self, message):
        self.run(self.cmd_cd, 'git add .', f'git commit -m "{message}"')
