import logging
import logging.config
import argparse
import pathlib
import shutil

import yaml

from . import subr
from . import lib


with open(pathlib.Path(__file__).parent / 'logging.conf.yml') as f:
    logging.config.dictConfig(yaml.safe_load(f))


logger = logging.getLogger(__name__)


def main_build(args: argparse.Namespace):
    data_dir = lib.dir.get_data_dir()
    repo_dir = lib.dir.get_repo_dir(data_dir)
    build_dir = lib.dir.get_build_dir(data_dir)

    if args.repository:
        clone_dir_name = subr.git.get_repo_name(args.repository)
        subr.git.clone(
            url=subr.git.get_repo_url(args.repository),
            dir=repo_dir,
            name=clone_dir_name,
        )
        lib.main.build(args.repository, repo_dir, build_dir)
        return

    for repository in repo_dir.iterdir():
        lib.main.build(repository.name, repo_dir, build_dir)


def main_dist(args: argparse.Namespace):
    data_dir = lib.dir.get_data_dir()
    build_dir = lib.dir.get_build_dir(data_dir)
    clone_dir_name = subr.git.get_repo_name(args.repository)
    target_file = build_dir / (clone_dir_name + ".so")

    if not target_file.exists():
        raise FileNotFoundError(f'File not found: {str(target_file)}')

    print(str(target_file))


def main_update(args: argparse.Namespace):
    data_dir = lib.dir.get_data_dir()
    repo_dir = lib.dir.get_repo_dir(data_dir)

    for repository in repo_dir.iterdir():
        subr.git.pull(repo_dir, repository.name)


def main_list(args: argparse.Namespace):
    data_dir = lib.dir.get_data_dir()
    repo_dir = lib.dir.get_repo_dir(data_dir)

    for repository in repo_dir.iterdir():
        print(repository.name.replace('__', '/'))


def main_remove(args: argparse.Namespace):
    data_dir = lib.dir.get_data_dir()
    repo_dir = lib.dir.get_repo_dir(data_dir)

    logger.info(f'Remove repository: {str(repo_dir / args.repository)}')
    (repo_dir / subr.git.get_repo_name(args.repository)).unlink(missing_ok=True)


def main_clean(args: argparse.Namespace):
    data_dir = lib.dir.get_data_dir()
    build_dir = lib.dir.get_build_dir(data_dir)

    logger.info(f'Clean build directory: {str(build_dir)}')
    shutil.rmtree(build_dir)
    build_dir.mkdir()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')

    parser_build = subparsers.add_parser('build', help='Build tree-sitter module.')
    parser_build.add_argument('repository', help='Repository specifier in github or git URL.', nargs='?')
    parser_build.set_defaults(handler=main_build)

    parser_build = subparsers.add_parser('dist', help='Show path of tree-sitter module.')
    parser_build.add_argument('repository', help='Repository specifier in github or git URL.', nargs='?')
    parser_build.set_defaults(handler=main_dist)

    parser_update = subparsers.add_parser('update', help='Update tree-sitter module.')
    parser_update.set_defaults(handler=main_update)

    parser_list = subparsers.add_parser('list', help='List tree-sitter module.')
    parser_list.set_defaults(handler=main_list)

    parser_remove = subparsers.add_parser('remove', help='Remove tree-sitter module.')
    parser_remove.add_argument('repository', help='Repository specifier in github or git URL.')
    parser_remove.set_defaults(handler=main_remove)

    parser_clean = subparsers.add_parser('clean', help='Clean build directory.')
    parser_clean.set_defaults(handler=main_clean)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        exit(1)

    return args


def main():
    args = parse_args()
    args.handler(args)
