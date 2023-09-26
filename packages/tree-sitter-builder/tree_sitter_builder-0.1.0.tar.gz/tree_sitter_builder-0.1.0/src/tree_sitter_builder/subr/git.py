import logging
import pathlib
import re
import subprocess


logger = logging.getLogger(__name__)


def get_repo_url(repository: str) -> str:
    if '://' in repository:
        return repository

    return f'https://github.com/{repository}.git'


def get_repo_name(repository: str) -> str:
    def replace(s: str):
        tokens = '/:'
        for token in tokens:
            s = s.replace(token, '__')

        return s

    if ':' in repository:
        pat = r'://(.*?)(?:\.[^/\.]*)?$'
        if m := re.search(pat, repository):
            return replace(m.group(1))
        else:
            logger.warning(f'it seems URL but cannot parse: {repository}')

    return replace(repository)


def clone(url: str, dir: pathlib.Path, name: str):
    if dir.exists():
        return

    logger.info(f'Clone {url} to {str(dir / name)}')
    subprocess.run(['git', 'clone', url, name], cwd=dir, check=True)


def pull(dir: pathlib.Path, name: str):
    logger.info(f'Pull {str(dir / name)}')
    subprocess.run(['git', 'pull'], cwd=dir / name, check=True)
