import os
import tempfile
import github.Repository
import github.Commit
import pygit2 as git
from pathlib import Path
from typing import List

from ihk_ausbildungsnachweis_utilities import checker, builder, signator


class AzubiRepo:
    class LocalRepoRemoteCallbacks(git.RemoteCallbacks):
        def __init__(self, user: str, token: str):
            self.user = user
            self.token = token

        def credentials(self, url, username_from_url, allowed_types):
            return git.UserPass(self.user, self.token)

        def certificate_check(self, certificate, valid, host):
            return True

    def __init__(self, org: str, repo: str, token: str, ausbilder_whitelist: str) -> None:
        self._org = org
        self._repo = repo
        self._token = token
        self._ausbilder_whitelist = ausbilder_whitelist.split()

        self._github = github.Github(auth=github.Auth.Token(token))
        self._user_signature = git.Signature("Marvin", "mail+github_vw_marvin@twyleg.de")

        self.local_repo_dirpath = Path(tempfile.mkdtemp()) / "local_repo"
        self.my_remote_callback = AzubiRepo.LocalRepoRemoteCallbacks(self._github.get_user().login, self._token)

        self.remote_github_repo = self._get_remote_github_repo()
        self.local_git_repo = self._get_local_git_repo()

    def _get_remote_github_repo(self) -> github.Repository:
        azubi_repo_fullname = f"{self._org}/{self._repo}"
        return self._github.get_repo(azubi_repo_fullname)

    def _get_local_git_repo(self) -> git.Repository:
        git_https_url = f"https://github.com/{self._org}/{self._repo}.git"
        return git.clone_repository(git_https_url, str(self.local_repo_dirpath), callbacks=self.my_remote_callback)

    def checkout(self, branch_name: str) -> None:
        self.local_git_repo.remotes["origin"].fetch(callbacks=self.my_remote_callback)

        local_branch_path = f"refs/heads/{branch_name}"
        remote_branch_path = f"refs/remotes/origin/{branch_name}"

        remote_branch_id = self.local_git_repo.lookup_reference(remote_branch_path).target
        self.local_git_repo.checkout_tree(self.local_git_repo.get(remote_branch_id))

        self.local_git_repo.create_branch(branch_name, self.local_git_repo.get(remote_branch_id))
        branch_ref = self.local_git_repo.lookup_reference(local_branch_path)
        branch_ref.set_target(remote_branch_id)
        self.local_git_repo.references["HEAD"].set_target(local_branch_path)

    def add_files(self, filepaths: List[Path]) -> None:
        index = self.local_git_repo.index
        for filepath in filepaths:
            index.add(filepath.as_posix())
        index.write()

    def commit(self, message: str):
        author = self._user_signature
        commiter = self._user_signature
        tree = self.local_git_repo.index.write_tree()
        ref = self.local_git_repo.head.name
        parents = [self.local_git_repo.head.target]
        self.local_git_repo.create_commit(ref, author, commiter, message, tree, parents)

    def revert_commit(self, commit_remote: git.Commit) -> None:
        author = self._user_signature
        commiter = self._user_signature
        master = self.local_git_repo.head.peel()
        commit_to_revert = self.local_git_repo[commit_remote.sha]
        revert_index = self.local_git_repo.revert_commit(commit_to_revert, master)
        tree = revert_index.write_tree()

        commit_local = self.local_git_repo.create_commit(
            "HEAD", author, commiter, f"Revert commit {commit_remote.sha}", tree, [self.local_git_repo.head.target]
        )
        self.local_git_repo.index.write()
        self.local_git_repo.reset(commit_local, git.GIT_RESET_MIXED)

    def push(self, branch_name: str) -> None:
        branch = self.local_git_repo.lookup_branch(f"{branch_name}", git.GIT_BRANCH_LOCAL)
        # ref = self.local_git_repo.lookup_reference(branch.name)
        self.local_git_repo.remotes["origin"].push([branch.name], callbacks=self.my_remote_callback)

    def get_approvers(self, commit: github.Commit) -> List[str]:
        approvers: List[str] = []
        for pull in commit.get_pulls():
            for review in pull.get_reviews():
                if review.user.login in self._ausbilder_whitelist and review.state == "APPROVED":
                    approvers.append(review.user.login)
        return approvers

    def is_commit_approved(self, commit: github.Commit) -> bool:
        approvers = self.get_approvers(commit)
        for approver in approvers:
            if approver in self._ausbilder_whitelist:
                return True
        return False

    def is_commit_by_ausbilder(self, commit: github.Commit) -> bool:
        return commit.author.login in self._ausbilder_whitelist

    def is_commit_reverted(self, revert_candidate_commit: github.Commit) -> bool:
        commits = self.remote_github_repo.get_commits()

        for commit in commits:
            print(revert_candidate_commit.commit.message)
            if commit.commit.message == f"Revert commit {revert_candidate_commit.sha}":
                return True
        return False

    def is_commit_initial_commit(self, commit: github.Commit) -> bool:
        return not commit.parents

    def revert_unapproved_commits(self) -> None:
        for commit in self.remote_github_repo.get_commits():
            print(f"Commit: {commit.sha}, '{commit.commit.message}' ", end="")
            if (
                self.is_commit_initial_commit(commit)
                or self.is_commit_approved(commit)
                or self.is_commit_by_ausbilder(commit)
            ):
                print("Approved!")
            else:
                print("Not approved! ", end="")
                if not self.is_commit_reverted(commit):
                    self.revert_commit(commit)
                    print(f"Commit Reverted!")
                else:
                    print(f"Commit was already reverted!")

    def _sign_ausbildungsnachweise_in_commit(self, commit: github.Commit) -> int:
        num = 0
        for file in commit.files:
            filepath = self.local_repo_dirpath / file.filename
            if filepath.suffix == ".pdf" and not checker.check_ausbildungsnachweis_pdf_for_signature(filepath):
                print(f"Signing: {file.filename}")
                approver = self.get_approvers(commit)[0]
                signator.sign_ausbildungsnachweis_pdf(filepath, Path.cwd() / f"ausbilder_profiles/{approver}.json")
                self.add_files([filepath.relative_to(self.local_repo_dirpath)])
                num += 1
        return num

    def sign_ausbildungsnachweise(self) -> None:
        num = 0
        for commit in self.remote_github_repo.get_commits():
            num += self._sign_ausbildungsnachweise_in_commit(commit)
        self.commit(f"Signed {num} ausbildungsnachweise.")

    def build_ausbildungsnachweise(self, branch_name: str) -> None:
        input_filepath = self.local_repo_dirpath / f"ausbildungsnachweise/{branch_name}.xml"
        output_dir = input_filepath.parent
        output_filepath = builder.build_ausbildungsnachweis_pdf(input_filepath, output_dir)
        self.add_files([output_filepath.relative_to(self.local_repo_dirpath)])
        self.commit(f"Built ausbildungsnachweis {branch_name}")
