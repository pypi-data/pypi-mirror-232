from __future__ import annotations

import dataclasses
import datetime
import logging
import os
import re
import subprocess  # nosec B404
from pathlib import Path
from shutil import which

from bx_py_utils.path import assert_is_file
from packaging.version import InvalidVersion, Version

from cli_base.cli_tools.subprocess_utils import verbose_check_call, verbose_check_output


logger = logging.getLogger(__name__)


class GitError(BaseException):
    """Base class for all git errors"""


class NoGitRepoError(GitError):
    def __init__(self, path):
        super().__init__(f'"{path}" is not a git repository')


class GitBinNotFoundError(GitError):
    def __init__(self):
        super().__init__('Git executable not found in PATH')


@dataclasses.dataclass
class GitTagInfo:
    raw_tag: str
    version: Version | None = None

    @property
    def version_tag(self):
        if self.version:
            return f'v{self.version}'
        return self.raw_tag


@dataclasses.dataclass
class GitTagInfos:
    tags: list[GitTagInfo]

    @classmethod
    def from_raw_tags(cls, raw_tags: list[str]) -> GitTagInfos:
        tags = []
        for raw_tag in raw_tags:
            try:
                version = Version(raw_tag)
            except InvalidVersion as err:
                logger.warning(f'Ignore: {err}')
                version = None
            tags.append(GitTagInfo(raw_tag=raw_tag, version=version))

        null_version = Version('0')
        tags.sort(key=lambda x: x.version or null_version)

        return cls(tags=tags)

    def get_releases(self):
        result = []
        for tag in self.tags:
            if version := tag.version:
                if version.is_devrelease or version.is_prerelease:
                    continue
                result.append(tag)
        return result

    def get_last_release(self):
        if releases := self.get_releases():
            return releases[-1]

    def exists(self, version: Version):
        for tag in self.tags:
            if tag.version and tag.version == version:
                return True
        return False


def get_git_root(path: Path):
    if len(path.parts) == 1 or not path.is_dir():
        return None

    if Path(path / '.git').is_dir():
        return path

    return get_git_root(path=path.parent)


class Git:
    def __init__(self, *, cwd: Path, detect_root: bool = True):
        if detect_root:
            self.cwd = get_git_root(cwd)
            if not self.cwd:
                raise NoGitRepoError(cwd)
        else:
            self.cwd = cwd

        self.git_bin = which('git')
        if not self.git_bin:
            raise GitBinNotFoundError()

        self.env = dict(os.environ)
        # no translated git command output ;)
        self.env['LANG'] = 'en_US.UTF-8'
        self.env['LANGUAGE'] = 'en_US'

    def git_verbose_check_call(self, *popenargs, **kwargs):
        popenargs = [self.git_bin, *popenargs]
        return verbose_check_call(
            *popenargs,
            cwd=self.cwd,
            env=self.env,
            **kwargs,
        )

    def git_verbose_check_output(self, *popenargs, **kwargs):
        popenargs = [self.git_bin, *popenargs]
        return verbose_check_output(
            *popenargs,
            cwd=self.cwd,
            env=self.env,
            **kwargs,
        )

    def git_verbose_output(self, *popenargs, exit_on_error=False, ignore_process_error=True, **kwargs):
        popenargs = [self.git_bin, *popenargs]
        try:
            return verbose_check_output(*popenargs, cwd=self.cwd, exit_on_error=exit_on_error, **kwargs)
        except subprocess.CalledProcessError as err:
            if ignore_process_error:
                return err.stdout
            raise

    def get_current_hash(self, commit='HEAD', verbose=True) -> str:
        output = self.git_verbose_check_output('rev-parse', '--short', commit, verbose=verbose)
        if git_hash := output.strip():
            assert len(git_hash) == 7, f'No git hash from: {output!r}'
            return git_hash

        raise AssertionError(f'No git hash from: {output!r}')

    def get_commit_date(self, commit='HEAD', verbose=True) -> datetime.datetime:
        output = self.git_verbose_check_output('show', '-s', '--format=%cI', commit, verbose=verbose)
        raw_date = output.strip()
        # e.g.: "2022-10-25 20:43:10 +0200"
        return datetime.datetime.fromisoformat(raw_date)

    def diff(
        self,
        reference1,
        reference2,
        no_color=True,
        indent_heuristic=False,
        irreversible_delete=True,
        verbose=True,
    ) -> str:
        # https://git-scm.com/docs/git-diff
        args = []
        if no_color:
            args.append('--no-color')

        if not indent_heuristic:
            args.append('--no-indent-heuristic')

        if irreversible_delete:
            args.append('--irreversible-delete')

        output = self.git_verbose_output('diff', *args, reference1, reference2, verbose=verbose)
        return output

    def apply(self, patch_path, verbose=True):
        # https://git-scm.com/docs/git-apply
        self.git_verbose_check_call(
            'apply',
            '--reject',
            '--ignore-whitespace',
            '--whitespace=fix',
            '-C1',
            '--recount',
            '--stat',
            '--summary',
            '--verbose',
            '--apply',
            patch_path,
            verbose=verbose,
        )

    def init(
        self,
        branch_name='main',
        user_name='Foo Bar',
        user_email='foo-bar@test.tld',
        verbose=True,
    ) -> Path:
        output = self.git_verbose_check_output('init', '-b', branch_name, verbose=verbose, exit_on_error=True)
        assert 'initialized' in output.lower(), f'Seems there is an error: {output}'
        self.cwd = get_git_root(self.cwd)

        self.config('user.name', user_name, scope='local', verbose=verbose)
        self.config('user.email', user_email, scope='local', verbose=verbose)

        return self.cwd

    def config(self, key, value, scope='local', verbose=True):
        assert scope in ('global', 'system', 'local')
        output = self.git_verbose_check_output('config', f'--{scope}', key, value, verbose=verbose, exit_on_error=True)
        return output.strip()

    def get_config(self, key, verbose=True):
        if key in self.list_config_keys(verbose=verbose):
            output = self.git_verbose_check_output('config', '--get', key, verbose=verbose, exit_on_error=False)
            return output.strip()

    def list_config_keys(self, verbose=False) -> set:
        output = self.git_verbose_check_output('config', '--list', '--name-only', verbose=verbose, exit_on_error=False)
        keys = {item.strip() for item in output.splitlines() if item.strip()}
        return keys

    def add(self, spec, verbose=True) -> None:
        output = self.git_verbose_check_output('add', spec, verbose=verbose, exit_on_error=True)
        assert not output, f'Seems there is an error: {output}'

    def commit(self, comment, verbose=True) -> str:
        output = self.git_verbose_check_output('commit', '--message', comment, verbose=verbose, exit_on_error=True)
        assert comment in output, f'Seems there is an error: {output}'
        return output

    def reflog(self, verbose=True) -> str:
        return self.git_verbose_check_output('reflog', verbose=verbose, exit_on_error=True)

    def log(
        self,
        format='%h - %an, %ar : %s',
        no_merges=False,
        commit1: str | None = None,  # e.g.: "HEAD"
        commit2: str | None = None,  # e.g.: "v0.8.0"
        verbose=True,
        exit_on_error=True,
    ) -> list[str]:
        """
        e.g.: git log --no-merges HEAD...v0.8.0 --pretty=format:"%h %as %s"
        """
        args = ['log']
        if no_merges:
            args.append('--no-merges')

        if commit1 and commit2:
            args.append(f'{commit1}...{commit2}')

        args.append(f'--pretty=format:{format}')
        output = self.git_verbose_check_output(*args, verbose=verbose, exit_on_error=exit_on_error)
        lines = output.splitlines()
        return lines

    def get_file_dt(self, file_name, verbose=True, with_tz=True) -> datetime.datetime | None:
        output = self.git_verbose_check_output(
            'log',
            '-1',
            '--format="%aI"',  # author date, strict ISO 8601 format
            '--',
            file_name,
            verbose=verbose,
        )
        iso_dt = output.strip('" \n')
        if not iso_dt:
            logger.warning('No date time found in: %r', output)
            return None

        dt = datetime.datetime.fromisoformat(iso_dt)
        if with_tz:
            return dt

        # Remove time zone information:
        dt2 = datetime.datetime.fromtimestamp(dt.timestamp())
        logger.info('%r -> %s -> %s', iso_dt, dt, dt2)
        return dt2

    def tag(self, git_tag: str, message: str, verbose=True, exit_on_error=True):
        self.git_verbose_check_call('tag', '-a', git_tag, '-m', message, verbose=verbose, exit_on_error=exit_on_error)

    def push(
        self,
        name: str | None = None,
        branch_name: str | None = None,
        tags: bool = False,
        verbose=True,
        get_output=False,
    ):
        """
        e.g.:
            git.push()
            git.push(name='origin')
            git.push(name='origin', branch_name='my_branch')
        """
        args = ['push']
        if tags:
            args.append('--tags')

        if name:
            args.append(name)

        if branch_name:
            assert name
            args.append(branch_name)

        if get_output:
            return self.git_verbose_check_output(*args, verbose=verbose)
        else:
            self.git_verbose_check_call(*args, verbose=verbose)

    def tag_list(self, verbose=True, exit_on_error=True) -> list[str]:
        output = self.git_verbose_check_output('tag', verbose=verbose, exit_on_error=exit_on_error)
        lines = output.splitlines()
        return lines

    def get_tag_infos(self, verbose=True, exit_on_error=True) -> GitTagInfos:
        raw_tags = self.tag_list(verbose=verbose, exit_on_error=exit_on_error)
        return GitTagInfos.from_raw_tags(raw_tags)

    def ls_files(self, verbose=True) -> list[Path]:
        output = self.git_verbose_check_output('ls-files', verbose=verbose, exit_on_error=True)
        file_paths = []
        for line in output.splitlines():
            file_path = self.cwd / line
            assert_is_file(file_path)
            file_paths.append(file_path)
        return sorted(file_paths)

    def print_file_list(self, out_func=print, verbose=True) -> None:
        for item in self.ls_files(verbose=verbose):
            out_func(f'* "{item.relative_to(self.cwd)}"')

    def reset(self, *, commit, hard=True, verbose=True) -> None:
        args = ['reset']
        if hard:
            args.append('--hard')
        args.append(commit)
        output = self.git_verbose_check_output(*args, verbose=verbose, exit_on_error=True)
        test_str = f'HEAD is now at {commit} '
        assert output.startswith(test_str), f'Reset error: {output!r} does not start with {test_str!r}'

    def status(self, verbose=True) -> list:
        """
        Returns the changed files, if any.
        """
        output = self.git_verbose_check_output('status', '--porcelain', verbose=verbose, exit_on_error=True)
        result = []
        for line in output.splitlines():
            line = line.strip()
            status, filepath = line.split(' ', 1)
            result.append((status, filepath))
        return result

    def get_raw_branch_names(self, verbose=True) -> list[str]:
        output = self.git_verbose_check_output('branch', '--no-color', verbose=verbose)
        branches = output.splitlines()
        logger.debug('Git raw branches: %r', branches)
        return branches

    def get_current_branch_name(self, verbose=True) -> str | None:
        raw_branch_names = self.get_raw_branch_names(verbose=verbose)
        for branch_name in raw_branch_names:
            if branch_name.startswith('*'):
                return branch_name.strip('* ')
        raise GitError(f'Current branch name not found in: {raw_branch_names}')

    def get_branch_names(self, verbose=True) -> list[str]:
        return sorted(branch.strip('*+ ') for branch in self.get_raw_branch_names(verbose=verbose))

    def get_main_branch_name(self, possible_names=('main', 'master'), verbose=True):
        """
        Returns the name of the "main" git branch.
        """
        branches = self.get_branch_names(verbose=verbose)

        branch_name = None
        for name in possible_names:
            if name in branches:
                branch_name = name
                break

        if branch_name is None:
            raise GitError(f'Git main branch not found in: {branches}')

        logger.info('Git main branch: "%s"', branch_name)
        return branch_name

    def pull(self, name='origin', branch_name=None, verbose=True):
        assert branch_name
        return self.git_verbose_check_output('pull', name, branch_name, verbose=verbose)

    def checkout_branch(self, branch_name, verbose=True):
        return self.git_verbose_check_call('checkout', branch_name, verbose=verbose)

    def checkout_new_branch(self, branch_name, verbose=True):
        return self.git_verbose_check_call('checkout', '-b', branch_name, verbose=verbose)

    def get_remote_url(self, name='origin', action_type='push', verbose=True):
        """
        returns a string like:
            'git@github.com:<username>/<project_name>.git'
        """
        output = self.git_verbose_check_output('remote', '-v', verbose=verbose)
        matches = re.findall(r'(\S+)\s+(\S+)\s+\((\S+)\)', output)
        for current_name, url, current_action in matches:
            logger.info('Fount git remote: %r %r %r', current_name, url, current_action)
            if current_name == name and current_action == action_type:
                logger.info('Use git remote url: %r', url)
                return url

    def get_github_username(self, name='origin', action_type='push', verbose=True):
        """
        returns the user name from the git remote url
        e.g.:
            remote url is: 'git@github.com:<username>/<project_name>.git'
            -> returns '<username>'
        """
        url = self.get_remote_url(name=name, action_type=action_type, verbose=verbose)
        if 'github.com' not in url:
            logger.info('Non github url: %r', url)
            return

        matches = re.findall(r':(\S+)/', url)
        if matches:
            return matches[0]
